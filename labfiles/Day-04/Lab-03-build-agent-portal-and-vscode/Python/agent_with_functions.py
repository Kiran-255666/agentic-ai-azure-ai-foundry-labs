import base64
import json
import os
import re
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import requests
from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv


# ============================================================
# Configuration
# ============================================================

OUTPUT_DIR = Path("agent_outputs")
DOWNLOADS_DIR = Path.home() / "Downloads"
RETRY_DELAYS = [2, 5, 10]

# If the user's message contains any of these words, we skip the
# broken code-interpreter image pipeline entirely and generate
# the chart locally instead.
CHART_KEYWORDS = ["chart", "plot", "graph", "visuali"]


# ============================================================
# Local file helpers
# ============================================================

def get_output_path(filename, directory=OUTPUT_DIR):
    directory.mkdir(exist_ok=True)
    file_name = Path(filename).name
    stem = Path(file_name).stem or "output"
    suffix = Path(file_name).suffix
    output_path = directory / file_name
    counter = 1
    while output_path.exists():
        output_path = directory / f"{stem}_{counter}{suffix}"
        counter += 1
    return output_path


def save_bytes(file_bytes, filename, directory=OUTPUT_DIR):
    output_path = get_output_path(filename, directory)
    with open(output_path, "wb") as file_handle:
        file_handle.write(file_bytes)
    return output_path


def save_image(image_data, filename):
    return save_bytes(base64.b64decode(image_data), filename)


# ============================================================
# LOCAL CHART GENERATION (bypasses the broken container endpoint)
# ============================================================

def extract_json_block(text):
    """Pull the first JSON object/array out of a text blob."""
    match = re.search(r"\{.*\}|\[.*\]", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def request_chart_data(openai_client, agent, conversation, description):
    """
    Ask the agent for the underlying numbers as JSON — NOT an image.
    This avoids the code interpreter ever needing to hand us a
    container file, so there is nothing that can 500 on download.
    """

    prompt = (
        f"{description}\n\n"
        "Do not generate an image, chart, or file. Just look at the "
        "data and respond with ONLY a single raw JSON object, no "
        "markdown code fences, no commentary before or after, in "
        "exactly this shape:\n"
        '{"title": "...", "x_label": "...", "y_label": "...", '
        '"labels": ["point1", "point2", ...], '
        '"series": {"SeriesName": [number1, number2, ...]}}\n\n'
        "labels and each series array must be the same length."
    )

    openai_client.conversations.items.create(
        conversation_id=conversation.id,
        items=[{"type": "message", "role": "user", "content": prompt}],
    )

    response = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={
            "agent_reference": {"name": agent.name, "type": "agent_reference"}
        },
        input="",
    )

    text = getattr(response, "output_text", "") or ""

    # Fallback: some SDKs don't populate output_text; walk output items.
    if not text and hasattr(response, "output") and response.output:
        for item in response.output:
            if getattr(item, "type", "") == "message":
                for content_item in getattr(item, "content", []) or []:
                    if getattr(content_item, "type", "") == "output_text":
                        text += content_item.text or ""

    return extract_json_block(text), text


def plot_chart_locally(chart_data, filename="chart.png"):
    """Render the chart ourselves with matplotlib and save to Downloads."""

    labels = chart_data.get("labels", [])
    series = chart_data.get("series", {})

    if not labels or not series:
        raise ValueError("Chart data missing 'labels' or 'series'")

    plt.figure(figsize=(10, 5))

    for name, values in series.items():
        plt.plot(labels, values, marker="o", label=name)

    plt.title(chart_data.get("title", "Chart"))
    plt.xlabel(chart_data.get("x_label", ""))
    plt.ylabel(chart_data.get("y_label", ""))
    plt.xticks(rotation=45, ha="right")

    if len(series) > 1:
        plt.legend()

    plt.tight_layout()

    output_path = get_output_path(filename, DOWNLOADS_DIR)
    plt.savefig(output_path, dpi=150)
    plt.close()

    return output_path


def handle_chart_request(openai_client, agent, conversation, user_input):
    """Full local-chart flow. Returns True if it handled the request."""

    print("\n[Detected a chart request — generating it locally, "
          "bypassing the Foundry container-file download entirely...]")

    chart_data, raw_text = request_chart_data(
        openai_client, agent, conversation, user_input
    )

    if not chart_data:
        print(
            "\n[Warning] Could not get structured data back from the "
            "agent to plot. Raw response was:\n"
        )
        print(raw_text[:1000])
        return False

    safe_title = re.sub(r"[^a-zA-Z0-9_-]+", "_", chart_data.get("title", "chart"))
    filename = f"{safe_title.lower() or 'chart'}.png"

    try:
        output_path = plot_chart_locally(chart_data, filename)
    except Exception as exc:
        print(f"\n[Warning] Failed to render chart locally: {exc}")
        return False

    print(f"\n[Chart saved to: {output_path}]")
    return True


# ============================================================
# Container file downloader (kept as fallback for non-chart files)
# ============================================================

def get_access_token(credential):
    return credential.get_token("https://ai.azure.com/.default").token


def download_container_file(credential, project_endpoint, annotation, downloaded_files):
    container_id = getattr(annotation, "container_id", None)
    file_id = getattr(annotation, "file_id", None)
    filename = getattr(annotation, "filename", None) or f"{file_id}.bin"

    if not container_id or not file_id:
        print("\n[Warning] Container file citation missing container_id or file_id.")
        return None

    cache_key = (container_id, file_id)
    if cache_key in downloaded_files:
        return downloaded_files[cache_key]

    print("\n[Container file download]")
    print(f"File:      {filename}")
    print(f"Container: {container_id}")
    print(f"File ID:   {file_id}")

    try:
        token = get_access_token(credential)
    except Exception as exc:
        print(f"\n[Warning] Could not acquire Azure access token: {exc}")
        return None

    headers = {"Authorization": f"Bearer {token}", "Accept": "application/octet-stream"}
    url = f"{project_endpoint}/openai/v1/containers/{container_id}/files/{file_id}/content"

    for attempt, delay in enumerate(RETRY_DELAYS, start=1):
        try:
            response = requests.get(url, headers=headers, timeout=60)
        except requests.RequestException as exc:
            print(f"[Warning] Request error (attempt {attempt}/{len(RETRY_DELAYS)}): {exc}")
            if attempt < len(RETRY_DELAYS):
                time.sleep(delay)
            continue

        if response.status_code == 200 and response.content:
            output_path = save_bytes(response.content, filename)
            downloaded_files[cache_key] = output_path
            print(f"[OK] Downloaded on attempt {attempt} -> {output_path}")
            return output_path

        if response.status_code in (401, 403, 404, 400):
            print(f"[Warning] HTTP {response.status_code}: {response.text[:500]}")
            return None

        print(f"[Warning] HTTP {response.status_code} (attempt {attempt}/{len(RETRY_DELAYS)})")
        if attempt < len(RETRY_DELAYS):
            time.sleep(delay)

    print(f"\n[Warning] Could not download '{filename}'.")
    return None


def format_output_text(content_item, credential, project_endpoint, downloaded_files):
    text = content_item.text or ""
    replacements = []
    referenced_files = set()

    for annotation in content_item.annotations or []:
        if getattr(annotation, "type", "") != "container_file_citation":
            continue

        output_path = download_container_file(
            credential, project_endpoint, annotation, downloaded_files
        )
        filename = getattr(annotation, "filename", None) or getattr(
            annotation, "file_id", "generated_file"
        )

        if output_path is not None:
            replacement_text = f"{filename} (saved to {output_path})"
            referenced_files.add(output_path)
        else:
            replacement_text = f"{filename} (download failed)"

        start_index = getattr(annotation, "start_index", None)
        end_index = getattr(annotation, "end_index", None)

        if start_index is not None and end_index is not None:
            replacements.append((start_index, end_index, replacement_text))
            continue

        annotated_text = getattr(annotation, "text", "")
        if annotated_text:
            text = text.replace(annotated_text, replacement_text)

    for start_index, end_index, replacement_text in sorted(replacements, reverse=True):
        text = text[:start_index] + replacement_text + text[end_index:]

    return text, referenced_files


# ============================================================
# Main application
# ============================================================

def main():
    load_dotenv()

    project_endpoint = os.environ.get("PROJECT_ENDPOINT")
    agent_name = os.environ.get("AGENT_NAME", "it-support-agent")

    if not project_endpoint:
        print("Error: PROJECT_ENDPOINT environment variable not set.")
        print("Please set PROJECT_ENDPOINT in your .env file.")
        return

    project_endpoint = project_endpoint.rstrip("/")

    print("Connecting to Microsoft Foundry project...")
    credential = AzureCliCredential()
    project_client = AIProjectClient(endpoint=project_endpoint, credential=credential)
    openai_client = project_client.get_openai_client()

    print(f"Loading agent: {agent_name}")
    agent = project_client.agents.get(agent_name=agent_name)
    print(f"Connected to agent: {agent.name} (id: {agent.id})")

    conversation = openai_client.conversations.create(items=[])
    print(f"Conversation created (id: {conversation.id})")

    print("\n" + "=" * 60)
    print("IT Support Agent Ready!")
    print("Ask questions, request data analysis, or get help.")
    print(f"Charts are generated locally and saved to: {DOWNLOADS_DIR}")
    print("Other generated files are saved to ./agent_outputs")
    print("Type 'exit' to quit.")
    print("=" * 60 + "\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break

        if not user_input:
            continue

        # ------------------------------------------------------------
        # Chart requests: handled entirely locally, no container files.
        # ------------------------------------------------------------
        if any(keyword in user_input.lower() for keyword in CHART_KEYWORDS):
            print("\n[Agent is thinking...]")
            handled = handle_chart_request(openai_client, agent, conversation, user_input)
            if handled:
                continue
            print("\n[Falling back to normal response for this message...]\n")
            # fall through to normal flow below if local chart failed

        # ------------------------------------------------------------
        # Normal flow (text answers, stats, etc.) — unaffected by the bug
        # ------------------------------------------------------------
        openai_client.conversations.items.create(
            conversation_id=conversation.id,
            items=[{"type": "message", "role": "user", "content": user_input}],
        )

        print("\n[Agent is thinking...]")

        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={
                "agent_reference": {"name": agent.name, "type": "agent_reference"}
            },
            input="",
        )

        handled_output = False
        downloaded_files = {}
        referenced_files = set()
        image_count = 0

        if hasattr(response, "output") and response.output:
            for item in response.output:
                item_type = getattr(item, "type", "")

                if item_type == "message" and getattr(item, "content", None):
                    for content_item in item.content:
                        if getattr(content_item, "type", "") != "output_text":
                            continue

                        formatted_text, message_files = format_output_text(
                            content_item, credential, project_endpoint, downloaded_files
                        )
                        referenced_files.update(message_files)

                        if formatted_text:
                            print(f"\nAgent: {formatted_text}\n")
                            handled_output = True

                elif hasattr(item, "text") and item.text:
                    print(f"\nAgent: {item.text}\n")
                    handled_output = True

                elif item_type == "image":
                    image_count += 1
                    filename = getattr(item, "filename", f"chart_{image_count}.png")
                    image = getattr(item, "image", None)
                    image_data = getattr(image, "data", None)

                    if image_data:
                        file_path = save_image(image_data, filename)
                        print(f"\n[Agent generated a chart - saved to: {file_path}]")
                    else:
                        print("\n[Agent generated an image, but no image data was returned.]")

                    handled_output = True

            for file_path in downloaded_files.values():
                if file_path not in referenced_files:
                    print(f"\n[Agent generated a file - saved to: {file_path}]")
                    handled_output = True

        if not handled_output and hasattr(response, "output_text") and response.output_text:
            print(f"\nAgent: {response.output_text}\n")


if __name__ == "__main__":
    main()