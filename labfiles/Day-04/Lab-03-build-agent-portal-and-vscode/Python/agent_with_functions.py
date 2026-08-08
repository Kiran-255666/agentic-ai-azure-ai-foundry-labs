import base64
import os
import time
from pathlib import Path

import requests
from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv


# ============================================================
# Configuration
# ============================================================

# All generated files will be saved here.
OUTPUT_DIR = Path("agent_outputs")

# Retry delays for temporary HTTP failures.
RETRY_DELAYS = [2, 5, 10]


# ============================================================
# Local file helpers
# ============================================================

def get_output_path(filename):
    """Create a unique local path for a generated file."""

    OUTPUT_DIR.mkdir(exist_ok=True)

    # Keep only the filename.
    file_name = Path(filename).name

    stem = Path(file_name).stem or "output"
    suffix = Path(file_name).suffix

    output_path = OUTPUT_DIR / file_name

    counter = 1

    while output_path.exists():
        output_path = OUTPUT_DIR / f"{stem}_{counter}{suffix}"
        counter += 1

    return output_path


def save_bytes(file_bytes, filename):
    """Save binary content to a local file."""

    output_path = get_output_path(filename)

    with open(output_path, "wb") as file_handle:
        file_handle.write(file_bytes)

    return output_path


def save_image(image_data, filename):
    """Save base64-encoded image data to a local file."""

    return save_bytes(
        base64.b64decode(image_data),
        filename,
    )


# ============================================================
# Azure authentication
# ============================================================

def get_access_token(credential):
    """Get an Azure access token for Microsoft Foundry."""

    return credential.get_token(
        "https://ai.azure.com/.default"
    ).token


# ============================================================
# Container file downloader
# ============================================================

def download_container_file(
    credential,
    project_endpoint,
    annotation,
    downloaded_files,
):
    """
    Download a generated Microsoft Foundry container file.

    This intentionally bypasses:

        openai_client.containers.files.content.retrieve()

    because that SDK helper is returning HTTP 500 for the
    generated container files in this environment.

    The request uses the current OpenAI v1 container-file path:

        /openai/v1/containers/{container_id}/files/{file_id}/content
    """

    container_id = getattr(
        annotation,
        "container_id",
        None,
    )

    file_id = getattr(
        annotation,
        "file_id",
        None,
    )

    filename = (
        getattr(annotation, "filename", None)
        or f"{file_id}.bin"
    )

    # --------------------------------------------------------
    # Validate annotation
    # --------------------------------------------------------

    if not container_id or not file_id:
        print(
            "\n[Warning] Container file citation is missing "
            "container_id or file_id."
        )
        return None

    # --------------------------------------------------------
    # Prevent duplicate downloads
    # --------------------------------------------------------

    cache_key = (
        container_id,
        file_id,
    )

    if cache_key in downloaded_files:
        return downloaded_files[cache_key]

    # --------------------------------------------------------
    # Diagnostics
    # --------------------------------------------------------

    print("\n[Container file download]")
    print(f"File:      {filename}")
    print(f"Container: {container_id}")
    print(f"File ID:   {file_id}")

    # --------------------------------------------------------
    # Get Azure access token
    # --------------------------------------------------------

    try:
        token = get_access_token(credential)

    except Exception as exc:
        print(
            "\n[Warning] Could not acquire Azure access token:"
        )
        print(exc)
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/octet-stream",
    }

    # --------------------------------------------------------
    # Current v1 container-file endpoint
    # --------------------------------------------------------

    url = (
        f"{project_endpoint}"
        f"/openai/v1/containers/"
        f"{container_id}"
        f"/files/"
        f"{file_id}"
        f"/content"
    )

    print("[Download] API: OpenAI v1")
    print(f"[Download] URL: {url}")

    # --------------------------------------------------------
    # Retry temporary failures
    # --------------------------------------------------------

    for attempt, delay in enumerate(
        RETRY_DELAYS,
        start=1,
    ):

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=60,
            )

        except requests.RequestException as exc:

            print(
                f"[Warning] Request error "
                f"(attempt {attempt}/"
                f"{len(RETRY_DELAYS)}): {exc}"
            )

            if attempt < len(RETRY_DELAYS):
                print(
                    f"[Warning] Retrying in "
                    f"{delay} seconds..."
                )
                time.sleep(delay)

            continue

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        if (
            response.status_code == 200
            and response.content
        ):

            output_path = save_bytes(
                response.content,
                filename,
            )

            downloaded_files[cache_key] = output_path

            print(
                f"[OK] Downloaded successfully "
                f"on attempt {attempt}."
            )

            print(
                f"[OK] Downloaded bytes: "
                f"{len(response.content)}"
            )

            print(
                f"[OK] Saved to: {output_path}"
            )

            return output_path

        # ----------------------------------------------------
        # AUTHENTICATION FAILURE
        # ----------------------------------------------------

        if response.status_code == 401:

            print(
                "\n[Warning] Azure access token was rejected."
            )

            try:
                token = get_access_token(
                    credential
                )

                headers["Authorization"] = (
                    f"Bearer {token}"
                )

                print(
                    "[Info] Azure token refreshed."
                )

            except Exception as exc:

                print(
                    "[Warning] Could not refresh "
                    f"Azure token: {exc}"
                )

                return None

            # Retry immediately with the refreshed token.
            continue

        # ----------------------------------------------------
        # FORBIDDEN
        # ----------------------------------------------------

        if response.status_code == 403:

            print(
                "\n[Warning] Container file download "
                "was forbidden (HTTP 403)."
            )

            print(
                "[Warning] Check your Azure identity "
                "and Microsoft Foundry project permissions."
            )

            if response.text:
                print(
                    f"[Warning] Server response: "
                    f"{response.text[:1000]}"
                )

            return None

        # ----------------------------------------------------
        # NOT FOUND
        # ----------------------------------------------------

        if response.status_code == 404:

            print(
                "\n[Warning] Container or file was not found "
                "(HTTP 404)."
            )

            if response.text:
                print(
                    f"[Warning] Server response: "
                    f"{response.text[:1000]}"
                )

            return None

        # ----------------------------------------------------
        # BAD REQUEST
        # ----------------------------------------------------

        if response.status_code == 400:

            print(
                "\n[Warning] Server rejected the request "
                "(HTTP 400)."
            )

            if response.text:
                print(
                    f"[Warning] Server response: "
                    f"{response.text[:1000]}"
                )

            return None

        # ----------------------------------------------------
        # TEMPORARY SERVER ERROR
        # ----------------------------------------------------

        print(
            f"[Warning] Container file download failed "
            f"(attempt {attempt}/"
            f"{len(RETRY_DELAYS)}): "
            f"HTTP {response.status_code}"
        )

        if response.text:
            print(
                f"[Warning] Server response: "
                f"{response.text[:1000]}"
            )

        # Retry only 5xx errors.
        if (
            500 <= response.status_code < 600
            and attempt < len(RETRY_DELAYS)
        ):

            print(
                f"[Warning] Retrying in "
                f"{delay} seconds..."
            )

            time.sleep(delay)

            continue

        # Other HTTP status codes aren't worth retrying.
        break

    # --------------------------------------------------------
    # Complete failure
    # --------------------------------------------------------

    print(
        f"\n[Warning] Could not download "
        f"'{filename}'."
    )

    return None


# ============================================================
# Output formatting
# ============================================================

def format_output_text(
    content_item,
    credential,
    project_endpoint,
    downloaded_files,
):
    """
    Replace container file citations in agent output
    with local file paths.
    """

    text = content_item.text or ""

    replacements = []

    referenced_files = set()

    # --------------------------------------------------------
    # Process annotations
    # --------------------------------------------------------

    for annotation in (
        content_item.annotations or []
    ):

        # Only process generated container files.
        if (
            getattr(annotation, "type", "")
            != "container_file_citation"
        ):
            continue

        output_path = download_container_file(
            credential,
            project_endpoint,
            annotation,
            downloaded_files,
        )

        filename = (
            getattr(annotation, "filename", None)
            or getattr(
                annotation,
                "file_id",
                "generated_file",
            )
        )

        # ----------------------------------------------------
        # Successful download
        # ----------------------------------------------------

        if output_path is not None:

            replacement_text = (
                f"{filename} "
                f"(saved to {output_path})"
            )

            referenced_files.add(
                output_path
            )

        # ----------------------------------------------------
        # Failed download
        # ----------------------------------------------------

        else:

            replacement_text = (
                f"{filename} "
                f"(download failed)"
            )

        # ----------------------------------------------------
        # Use annotation indexes when available
        # ----------------------------------------------------

        start_index = getattr(
            annotation,
            "start_index",
            None,
        )

        end_index = getattr(
            annotation,
            "end_index",
            None,
        )

        if (
            start_index is not None
            and end_index is not None
        ):

            replacements.append(
                (
                    start_index,
                    end_index,
                    replacement_text,
                )
            )

            continue

        # ----------------------------------------------------
        # Fallback for SDKs without indexes
        # ----------------------------------------------------

        annotated_text = getattr(
            annotation,
            "text",
            "",
        )

        if annotated_text:

            text = text.replace(
                annotated_text,
                replacement_text,
            )

    # --------------------------------------------------------
    # Apply indexed replacements backwards
    # --------------------------------------------------------

    for (
        start_index,
        end_index,
        replacement_text,
    ) in sorted(
        replacements,
        reverse=True,
    ):

        text = (
            text[:start_index]
            + replacement_text
            + text[end_index:]
        )

    return text, referenced_files


# ============================================================
# Main application
# ============================================================

def main():
    """Start the IT Support Agent."""

    # --------------------------------------------------------
    # Load environment variables
    # --------------------------------------------------------

    load_dotenv()

    project_endpoint = os.environ.get(
        "PROJECT_ENDPOINT"
    )

    agent_name = os.environ.get(
        "AGENT_NAME",
        "it-support-agent",
    )

    if not project_endpoint:

        print(
            "Error: PROJECT_ENDPOINT "
            "environment variable not set."
        )

        print(
            "Please set PROJECT_ENDPOINT "
            "in your .env file."
        )

        return

    # Remove trailing slash.
    project_endpoint = (
        project_endpoint.rstrip("/")
    )

    # --------------------------------------------------------
    # Connect to Microsoft Foundry
    # --------------------------------------------------------

    print(
        "Connecting to Microsoft Foundry project..."
    )

    credential = AzureCliCredential()

    # IMPORTANT:
    # AIProjectClient expects:
    #
    #     endpoint=...
    #     credential=...
    #
    # Both are passed as keywords to avoid the
    # "multiple values for argument 'endpoint'" error.

    project_client = AIProjectClient(
        endpoint=project_endpoint,
        credential=credential,
    )

    # Get authenticated OpenAI client.
    openai_client = (
        project_client.get_openai_client()
    )

    # --------------------------------------------------------
    # Load agent
    # --------------------------------------------------------

    print(
        f"Loading agent: {agent_name}"
    )

    agent = project_client.agents.get(
        agent_name=agent_name,
    )

    print(
        f"Connected to agent: "
        f"{agent.name} "
        f"(id: {agent.id})"
    )

    # --------------------------------------------------------
    # Create conversation
    # --------------------------------------------------------

    conversation = (
        openai_client.conversations.create(
            items=[]
        )
    )

    print(
        f"Conversation created "
        f"(id: {conversation.id})"
    )

    # --------------------------------------------------------
    # Application header
    # --------------------------------------------------------

    print("\n" + "=" * 60)

    print(
        "IT Support Agent Ready!"
    )

    print(
        "Ask questions, request data analysis, "
        "or get help."
    )

    print(
        "Generated files are saved to "
        "./agent_outputs"
    )

    print(
        "Type 'exit' to quit."
    )

    print("=" * 60 + "\n")

    # --------------------------------------------------------
    # Conversation loop
    # --------------------------------------------------------

    while True:

        user_input = input(
            "You: "
        ).strip()

        # ----------------------------------------------------
        # Exit
        # ----------------------------------------------------

        if user_input.lower() in [
            "exit",
            "quit",
            "bye",
        ]:

            print("Goodbye!")
            break

        # Ignore empty input.
        if not user_input:
            continue

        # ----------------------------------------------------
        # Add user message
        # ----------------------------------------------------

        openai_client.conversations.items.create(
            conversation_id=conversation.id,
            items=[
                {
                    "type": "message",
                    "role": "user",
                    "content": user_input,
                }
            ],
        )

        print(
            "\n[Agent is thinking...]"
        )

        # ----------------------------------------------------
        # Run agent
        # ----------------------------------------------------

        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={
                "agent_reference": {
                    "name": agent.name,
                    "type": "agent_reference",
                }
            },
            input="",
        )

        handled_output = False

        # Files downloaded during this response.
        downloaded_files = {}

        # Files already referenced in output text.
        referenced_files = set()

        image_count = 0

        # ----------------------------------------------------
        # Process response output
        # ----------------------------------------------------

        if (
            hasattr(response, "output")
            and response.output
        ):

            for item in response.output:

                item_type = getattr(
                    item,
                    "type",
                    "",
                )

                # --------------------------------------------
                # Normal message
                # --------------------------------------------

                if (
                    item_type == "message"
                    and getattr(
                        item,
                        "content",
                        None,
                    )
                ):

                    for content_item in item.content:

                        if (
                            getattr(
                                content_item,
                                "type",
                                "",
                            )
                            != "output_text"
                        ):
                            continue

                        (
                            formatted_text,
                            message_files,
                        ) = format_output_text(
                            content_item,
                            credential,
                            project_endpoint,
                            downloaded_files,
                        )

                        referenced_files.update(
                            message_files
                        )

                        if formatted_text:

                            print(
                                f"\nAgent: "
                                f"{formatted_text}\n"
                            )

                            handled_output = True

                # --------------------------------------------
                # Other text output
                # --------------------------------------------

                elif (
                    hasattr(item, "text")
                    and item.text
                ):

                    print(
                        f"\nAgent: "
                        f"{item.text}\n"
                    )

                    handled_output = True

                # --------------------------------------------
                # Direct image output
                # --------------------------------------------

                elif item_type == "image":

                    image_count += 1

                    filename = getattr(
                        item,
                        "filename",
                        f"chart_{image_count}.png",
                    )

                    image = getattr(
                        item,
                        "image",
                        None,
                    )

                    image_data = getattr(
                        image,
                        "data",
                        None,
                    )

                    if image_data:

                        file_path = save_image(
                            image_data,
                            filename,
                        )

                        print(
                            "\n[Agent generated a "
                            "chart - saved to: "
                            f"{file_path}]"
                        )

                    else:

                        print(
                            "\n[Agent generated an "
                            "image, but no image "
                            "data was returned.]"
                        )

                    handled_output = True

            # ------------------------------------------------
            # Report downloaded files
            # ------------------------------------------------

            for file_path in (
                downloaded_files.values()
            ):

                if (
                    file_path
                    not in referenced_files
                ):

                    print(
                        "\n[Agent generated a "
                        "file - saved to: "
                        f"{file_path}]"
                    )

                    handled_output = True

        # ----------------------------------------------------
        # Final fallback
        # ----------------------------------------------------

        if (
            not handled_output
            and hasattr(
                response,
                "output_text",
            )
            and response.output_text
        ):

            print(
                f"\nAgent: "
                f"{response.output_text}\n"
            )


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    main()