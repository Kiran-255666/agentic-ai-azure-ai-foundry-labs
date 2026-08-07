---
lab:
  title: Create a generative AI chat app
  description: Learn how to deploy a model in Microsoft Foundry and build a simple Python app that chats with it.
  level: 200
  duration: 20
  islab: true
  status: 'released'
---

# Create a generative AI chat app

In this exercise, you'll deploy a language model in Microsoft Foundry, then use the Foundry Python SDK to build a small app that sends messages to the model and shows its replies.

This exercise takes approximately **20** minutes.

> **Note**: Some of the technologies used in this exercise are in preview or in active development. You may see unexpected behavior, warnings, or errors.

## Prerequisites

Before starting this exercise, ensure you have:

- An active [Azure subscription](https://azure.microsoft.com/pricing/purchase-options/azure-account)
- A web browser
- Basic familiarity with running commands in a terminal (you don't need to know Python already; the code is provided)

> If your instructor or lab environment already created a Foundry project and deployed a model, skip ahead to **Create a client application to chat with the model**.

# Deploy a model in a Foundry project

A **Foundry project** is a workspace that holds the AI models, connections, and settings you use to build an app. Before you can chat with a model, you need to deploy one inside a project.

1. In a web browser, open the [Microsoft Foundry portal](https://ai.azure.com) at `https://ai.azure.com` and sign in with your Azure credentials. Close any tips or quick-start panes that appear the first time you sign in. If you get lost, select the Foundry logo in the top left to return to the home page (close the Help pane too, if it's open).
1. On the home page, find **Explore models and capabilities** and search for **gpt-5.4-mini**. This is the model your app will talk to.
1. Select **gpt-5.4-mini** in the results to open its details page, then select **Use this model** near the top.
1. When asked to create a project, type in a name and expand **Advanced options**.
1. Select **Customize** and fill in:
    - **Foundry resource**: a name for the resource that will host your project
    - **Subscription**: your Azure subscription
    - **Resource group**: create a new one, or pick an existing one
    - **Region**: any region marked **AI Foundry recommended**

    > **Tip**: Some regions run out of capacity for certain models. If that happens later in this exercise, you may need to create a new resource in a different region.

1. Select **Create**, then wait while your project and the gpt-5.4-mini deployment are set up.

    > **Important**: If your subscription doesn't have enough quota for gpt-5.4-mini in your chosen region, Foundry may ask you to deploy in a different region instead. If this happens, accept the default settings. Keep in mind that later in this exercise, you won't be able to use the project's default endpoint; you'll need the model-specific target URI instead (this is explained in the next section).

1. Once your project is ready, the chat playground opens automatically so you can try out the model. If it doesn't open, select **Playgrounds** in the left-hand menu, then open the **Chat playground**.
1. In the Setup pane, note the name of your model deployment. It should read **gpt-5.4-mini**. You can double-check this on the **Models and endpoints** page, also in the left-hand menu.

# Create a client application to chat with the model

Now that a model is deployed, you'll write a small Python app that connects to it and sends and receives chat messages. A **client application** here just means: code that runs on your machine and talks to the model over the internet.

### Prepare the application configuration

1. In the Foundry portal, open the **Overview** page for your project.
1. Find the **Endpoints and keys** section, and make sure the Foundry library option is selected. Note the **Foundry project endpoint** shown there; this is the web address your app will use to reach your project and model. (You could also use the Azure OpenAI endpoint instead, if you prefer.)
1. Open a new browser tab (leave the Foundry portal open in the first one) and go to the [Azure portal](https://portal.azure.com) at `https://portal.azure.com`. Sign in again if asked, and close any welcome notifications.
1. Near the search bar at the top, select the `[>_]` icon to open a new **Cloud Shell**. Choose a **PowerShell** environment, with no storage attached, in your subscription. The shell opens as a pane at the bottom of the page; you can resize or maximize it.

    > If you already have a Cloud Shell set up with Bash, switch it to PowerShell.

1. In the Cloud Shell toolbar, open the **Settings** menu and select **Go to Classic version**. This older interface includes a code editor you'll need later. Confirm you're on the classic version before moving on.
1. Download the exercise's code files by running:

    ```
    rm -r mslearn-ai-foundry -f
    git clone https://github.com/KiranAvulasetty/ai-studio mslearn-ai-foundry
    ```

    Type these in, or copy them and paste as plain text (right-click in the command line). If the screen fills up with output, type `cls` to clear it.

1. Move into the folder holding the chat app files, and list what's there:

    ```
    cd mslearn-ai-foundry/labfiles/chat-app/python
    ls -a -l
    ```

    You should see a code file, a configuration file for app settings, and a file listing the Python packages the app needs.

1. Install those packages:

    ```
    python -m venv labenv
    ./labenv/bin/Activate.ps1
    pip install -r requirements.txt azure-identity azure-ai-projects openai
    ```

1. Open the configuration file so you can edit it:

    ```
    code .env
    ```

    > If you deployed gpt-5.4-mini in your project's default region, use the Foundry project endpoint or Azure OpenAI endpoint from the project's Overview page. If your model landed in a different region because of quota limits, go to **Models + Endpoints**, select your model, and copy its **Target URI** instead.

1. In the file, replace `your_project_endpoint` with the endpoint you noted earlier, and `your_model_deployment` with the exact name of your gpt-5.4-mini deployment.
1. Save with **Ctrl+S** (or right-click and choose Save), then close the editor with **Ctrl+Q** (or right-click and choose Quit). Keep the Cloud Shell command line open.

### Write code to connect to your project and chat with your model

> **Tip**: Watch your indentation as you add each block of code below; Python treats indentation as part of the code's structure, so a misaligned line will cause an error.

1. Open the app's code file:

    ```
    code chat-app.py
    ```

1. Near the top, some import statements are already there. Find the comment `# Add references` and add these lines below it, so your app can use the SDKs you installed:

    ```python
    # Add references
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient
    from openai import AzureOpenAI
    ```

1. In the `main` function, under `# Get configuration settings`, the code already reads your project endpoint and model deployment name from the `.env` file you edited earlier. No changes needed there.
1. Find `# Initialize the project client` and add:

    ```python
    # Initialize the project client
    project_client = AIProjectClient(
        credential=DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True
        ),
        endpoint=project_endpoint,
    )
    ```

    This creates a connection between your app and your Foundry project, using your signed-in Azure identity instead of a password or key.

1. Find `# Get a chat client` and add:

    ```python
    # Get a chat client
    openai_client = project_client.get_openai_client(api_version="2024-10-21")
    ```

1. Find `# Initialize prompt with system message` and add:

    ```python
    # Initialize prompt with system message
    prompt = [
        {"role": "system", "content": "You are a helpful AI assistant that answers questions."}
    ]
    ```

    This line sets up the model's instructions before any conversation starts, telling it how to behave.

1. The code already has a loop that keeps asking for input until you type "quit". Inside that loop, find `# Get a chat completion` and add:

    ```python
    # Get a chat completion
    prompt.append({"role": "user", "content": input_text})
    response = openai_client.chat.completions.create(
        model=model_deployment,
        messages=prompt)
    completion = response.choices[0].message.content
    print(completion)
    prompt.append({"role": "assistant", "content": completion})
    ```

    Each time you ask something, this code adds your question to the conversation, sends the whole conversation to the model, prints the reply, and saves that reply too. Saving both sides of the conversation is what lets the model remember earlier questions when you ask a follow-up.

1. Save the file with **Ctrl+S**.

# Sign into Azure and run the app

1. In the Cloud Shell, sign in to Azure:

    ```
    az login
    ```

    You need to do this even though the Cloud Shell session already knows who you are; the app itself needs its own sign-in.

    > If your account has access to subscriptions in more than one tenant, add the `--tenant` parameter. See [Sign into Azure interactively using the Azure CLI](https://learn.microsoft.com/cli/azure/authenticate-azure-cli-interactively) for details.

1. Follow the prompts: open the sign-in link in a new tab, enter the code shown, and sign in with your Azure credentials. Back in the command line, pick the subscription containing your Foundry project if you're asked to.
1. Run the app:

    ```
    python chat-app.py
    ```

1. When prompted, type a question, such as "What is the fastest animal on Earth?", and read the model's reply.
1. Ask a follow-up, like "Where can I see one?" or "Are they endangered?" The model should answer using the earlier question as context, since your app is saving the conversation history.
1. Type "quit" to exit the program.

    > If the app stops with a rate-limit error, wait a few seconds and try again. If your subscription doesn't have enough quota left, the model may not respond at all.

## Clean up

If you're done exploring, delete the resources you created so they don't keep costing you money.

1. Open the [Azure portal](https://portal.azure.com) and open the resource group where you created your Foundry project.
1. On the toolbar, select **Delete resource group**.
1. Type the resource group's name to confirm, then delete it.

## Summary

You deployed a gpt-5.4-mini model in a Foundry project, then built a Python app that connects to it and holds a back-and-forth conversation, using conversation history so the model can follow up on earlier questions.
