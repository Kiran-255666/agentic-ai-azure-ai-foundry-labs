---
lab:
    title: 'Integrate an AI agent with Foundry IQ'
    description: 'Use Azure AI Agent Service to develop an agent that uses Foundry IQ to search knowledge bases.'
    level: 300
    duration: 45
    islab: true
    status: 'released'
---

# Integrate an AI agent with Foundry IQ
**Note: We have already updated the mentioned files with the code mentioned in the instructions, but we would highly suggest going through it before executing it**

In this exercise, you'll configure an AI agent that uses Foundry IQ to search and retrieve information from a knowledge base. You'll use your existing Foundry project and deployed models, create a search resource and knowledge base with sample data, configure an agent, and then connect to it from Visual Studio Code.

> **Tip**: The code used in this exercise is based on the Microsoft Foundry SDK for Python. You can develop similar solutions using the SDKs for Microsoft .NET, JavaScript, and Java. Refer to [Microsoft Foundry SDK client libraries](https://learn.microsoft.com/azure/ai-foundry/how-to/develop/sdk-overview) for details.

This exercise should take approximately **45** minutes to complete.

> **Note**: Some of the technologies used in this exercise are in preview or in active development. You may experience some unexpected behavior, warnings, or errors.

## Prerequisites

Before starting this exercise, ensure you have:

- An [Azure subscription](https://azure.microsoft.com/free/)
- [Visual Studio Code](https://code.visualstudio.com/) installed on your local machine
- [Python 3.13](https://www.python.org/downloads/) or later installed
- An existing Foundry project with deployed chat and embedding models
- Basic familiarity with the Microsoft Foundry portal and Python programming

## Use your Foundry project and deployed models

This lab uses the Foundry project and deployed models that are already available to you. You don't need to create a new Foundry project or deploy a new model for this exercise.

1. In a web browser, open the [Foundry portal](https://ai.azure.com) and sign in using your Azure credentials.

    > **Important**: Make sure the **New Foundry** toggle is *On* so you use the updated interface for this lab.

1. Select your existing Foundry project **(hakunamatata1)** from the project selector.
1. On the project home page, verify that a chat model and an embedding model are already deployed and available.
1. Keep the Foundry portal open. You'll use the existing chat model when creating the agent and knowledge base, and the existing embedding model when creating the knowledge source.

## Create an agent

With the Foundry project selected and the deployed model available, create an agent that will search the product knowledge base.

1. On the project home page, select the **Build** tab. On the **Agents** tab, select **Create agent**.
1. Create an agent with a descriptive name, such as `product-expert-agent`.
1. Select your existing deployed chat model if prompted.

    After the agent is created, the agent playground opens. You'll now configure the agent with product information from Foundry IQ.

## Configure data and Foundry IQ (The instructor/moderator has already created AI search and Storage account resources for your use; feel free to skip the creation of created AI search and Storage account resources )

First, add instructions to your agent. Then create a search resource, upload the product documents, and create a knowledge base that connects those documents to the agent.

1. Give your agent the following instructions:

    ```
    You are a helpful AI assistant for Contoso, specializing in outdoor camping and hiking products.
    You must ALWAYS search the knowledge base to answer questions about our products or product
    catalog. Provide detailed, accurate information and always cite your sources.
    If you don't find relevant information in the knowledge base, say so clearly.
    ```

1. Select **Save** to save your current agent configuration.
1. In the **Knowledge** section, expand the **Add** dropdown and select **Connect to Foundry IQ**. (Please select the one which your instrutor has created for you)
1. In the Foundry IQ setup window, select **Connect to an AI Search resource**, then select **Create new resource**.
1. Create a search resource with the following settings:

    - **Resource name**: A globally unique name
    - **Subscription**: Your Azure subscription
    - **Resource group**: Use the same resource group as your Foundry project  - **AgenticAIEngineer**
    - **Region**: The same location as your Foundry project
    - **Pricing tier**: Basic
    - **Foundry IQ Knowledge base capabilities**: Pause until next month

The search resource provides the retrieval layer for the knowledge base. Next, upload the source product documents.

1. Open a new browser tab and download the sample product information files from:

    ```
    https://github.com/Kiran-255666/agentic-ai-azure-ai-foundry-labs/raw/main/labfiles/Day-05/Lab-02-integrate-agent-with-foundry-iq/data/contoso-products.zip
    ```

1. Extract the ZIP file. It contains three PDFs describing Contoso products.
1. Open the [Azure portal](https://portal.azure.com). In the top search bar, search for **Storage accounts** and select **Storage accounts**.
1. Create a storage account with the following settings:

    - **Subscription**: Your Azure subscription
    - **Resource group**: Use the same resource group as your Foundry project - **AgenticAIEngineer**
    - **Storage account name**: A unique storage account name
    - **Region**: The same location as your Foundry project
    - **Primary service**: Azure Blob Storage or Azure Data Lake Storage
    - **Performance**: Standard
    - **Redundancy**: Locally-redundant storage (LRS)

1. After the storage account is created, open it and select **Upload** from the top bar.
1. In the **Upload blob** pane, create a new container named `contosoproducts`.
1. Browse to the extracted product files, select all three PDFs, and select **Upload**.
1. After the files are uploaded, navigate to the search service you created.
1. In the left pane, select **Security + networking** > **Keys**. For **API Access control**, select **Both** and confirm the selection.
1. Leave the Azure portal tab open. Return to the Foundry portal and refresh the page.
1. On the **Knowledge** page, select **Create a knowledge base**. Choose **Azure Blob Storage** as the knowledge source, then select **Connect**.
1. Configure the knowledge source with the following settings:

    - **Name**: `ks-contosoproducts`
    - **Description**: `Contoso product catalog items`
    - **Storage account name**: Select your storage account
    - **Container name**: `contosoproducts`
    - **Authentication type**: API Key
    - **Content extraction mode**: minimal
    - **Embedding model**: Select your available deployed embedding model **(text-embedding-ada-002)**
    - **Chat completions model**: Select your available deployed chat model **(gpt-5.4-mini)**

1. Select **Create**.
1. On the knowledge base creation page, select your deployed chat model from the **Chat completions model** dropdown and leave the remaining settings unchanged.
1. Select **Save knowledge base**. Refresh the browser until the knowledge source status is **active**.
1. Select the back button to return to the **Knowledge** page, then select **Manage** next to the **Connection** dropdown.
1. Scroll to **Connected resources**, select your search service, and find the **Authentication** section.
1. Select **Key authentication**, then select **Edit authentication**.
1. Return to the Azure portal tab, which should still show the search service **Keys** page. Copy one key into the Foundry dialog, then select **Save**.

Your Foundry IQ knowledge base is now connected to the product documents and ready for use by your agent.

## Test the agent in the playground

Before using code, confirm that the portal agent can retrieve product information from the knowledge base.

1. Navigate back to your agent from **Build** > **Agents**, then select `product-expert-agent`.
1. In the playground, find the knowledge section and add Foundry IQ by selecting the connection and knowledge base you created.
1. Test the agent with the following queries:

    - `What types of tents does Contoso offer?`
    - `Tell me about which backpacks are available in XL.`
    - `What camping accessories are available?`

1. Review the responses. The agent should provide product-specific information, remain grounded in the available data, and may include citations or document references.
1. You can also use **Preview agent** for a more refined web application experience.
1. In the agent details page, copy the following information to a notepad. You'll use these values when configuring the client application:

    - **Agent name**: The name you created, such as `product-expert-agent`
    - **Project endpoint**: Available from the project home page or project settings

### Configure approval for tool calls
**Note: We have already updated the mentioned files with the code mentioned in the instructions, but we would highly suggest going through it before executing it**

By default, the Foundry IQ knowledge tool runs without asking for approval. To let your application review and control each knowledge-base lookup, configure the agent to require approval before it uses the tool.

> **Note**: The Foundry portal doesn't currently expose this approval setting. Configure it with the Foundry Toolkit for VS Code extension.

> **Note**: If the Foundry Toolkit extension is already installed and signed in from a previous lab, skip to step 3.

1. In Visual Studio Code, select **Extensions** from the left pane, or press **Ctrl+Shift+X**. Search for `Foundry Toolkit for VS Code` from Microsoft and select **Install** if it isn't already installed.

    > **Note**: The extension is currently listed as **Foundry Toolkit**, but some labels, commands, or older screenshots may still refer to **AI Toolkit**. In this lab, treat these names as the same extension experience.

    ![Screenshot of the Foundry Toolkit for VS Code extension in the Extensions Marketplace.](../../media/foundry-toolkit-extension.png)
   
1. Select the **Foundry Toolkit** icon in the sidebar and sign in to Azure if prompted.

    > **Note**: If you cannot sign in through Foundry Toolkit, select the Azure extension and sign in there. Then return to Foundry Toolkit to access your resources.

1. Under **Microsoft Foundry Resources**, choose **Set Default Project** and select the project used in this lab.
1. Expand the project. Under **Prompt Agents**, select `product-expert-agent` to open **Agent Builder**.
1. In the **Tools** section, add the **Azure AI Search** tool. Select the connection and knowledge base that you created earlier.

    > **Note**: The portal may add a **Web search** tool to new agents by default. Use the three dots on the **Azure AI Search** tool associated with your knowledge base, not another tool.

1. In **Require approval before using tools**, select **Ask for approval for all tools**. Save your changes if prompted.

Your agent now requests approval whenever it uses Foundry IQ. The Python client you complete next will prompt you to approve or deny each request.

## Connect to your agent from an app

Now that the agent and knowledge base work in the portal, use the provided Python application to communicate with the agent programmatically.

### Get the application files from GitHub

> **Note**: If you've already downloaded and extracted the repository in a previous lab, skip ahead to step 5 below.

1. If you already downloaded and extracted this repository's ZIP file in a previous exercise, skip ahead to the next step and navigate directly to the folder path below. Otherwise, follow the remaining steps to download it.
1. Open a web browser and go to the [lab files on GitHub](https://github.com/Kiran-255666/agentic-ai-azure-ai-foundry-labs).
1. On the repository page, select the green **`<> Code`** button, then select **Download ZIP**.

    ![Screenshot of the Code button.](../../media/code.png)

1. After the download finishes, locate the ZIP file and extract it to a folder on your computer.
1. In the extracted folder, navigate to:

    ```
    agentic-ai-azure-ai-foundry-labs\labfiles\Day-05\Lab-02-integrate-agent-with-foundry-iq\python
    ```

    This folder already contains everything you need for this exercise.

    > **Tip**: If you're not sure which folder contains the exercise files, check with your trainer.

1. In **File Explorer**, select the address bar, type the following command, and press **Enter**:

    ```
    code .
    ```

    This opens the folder directly in Visual Studio Code.

    > **Tip**: If `code .` doesn't work, open the folder manually in Visual Studio Code.

1. In the **Explorer** pane, view the code files for this exercise. The folder includes application code, configuration settings, and the agent client starter code.

### Configure the application settings

The application needs the project endpoint and the name of the agent you created in the portal.

1. In Visual Studio Code, open the **.env** file in the `Lab-02-integrate-agent-with-foundry-iq\python` folder.
1. Replace the **your_project_endpoint** placeholder with your project endpoint.
1. Set the `AGENT_NAME` variable to your agent name, such as `product-expert-agent`.
1. Save the file with **Ctrl+S**.

### Complete the agent client code

> **Note**: We have already updated the mentioned files with the code in these instructions, but verify the code before you run it so there are no indentation issues.

> **Tip**: As you add code, maintain the correct indentation. Use the comment indentation levels as a guide.

1. In the `Lab-02-integrate-agent-with-foundry-iq\python` folder, open **agent_client.py**.
1. Review the starter code, including the imports and configuration loading, the `send_message_to_agent()` and `display_conversation_history()` functions, and the main program loop.
1. Find the first **TODO** comment and add the following code to connect to the project and agent, then create a conversation:

    ```python
    # Connect to the project and agent
    credential = DefaultAzureCredential(
        exclude_environment_credential=True,
        exclude_managed_identity_credential=True
    )
    project_client = AIProjectClient(
        credential=credential,
        endpoint=project_endpoint
    )

    # Get the OpenAI client
    openai_client = project_client.get_openai_client()

    # Get the agent
    agent = project_client.agents.get(agent_name=agent_name)
    print(f"Connected to agent: {agent.name} (id: {agent.id})\n")

    # Create a new conversation
    conversation = openai_client.conversations.create(items=[])
    print(f"Created conversation (id: {conversation.id})\n")
    ```

1. Find the second **TODO** comment inside `send_message_to_agent()` and add the following code to send messages and handle MCP approval requests:

    ```python
    # Add user message to the conversation
    openai_client.conversations.items.create(
        conversation_id=conversation.id,
        items=[{"type": "message", "role": "user", "content": user_message}],
    )

    # Store in conversation history (client-side)
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    # Create a response using the agent
    response = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        input=""
    )

    # Check if the response output contains an MCP approval request
    approval_request = None
    if hasattr(response, 'output') and response.output:
        for item in response.output:
            if hasattr(item, 'type') and item.type == 'mcp_approval_request':
                approval_request = item
                break

    # Handle approval request if present
    if approval_request:
        print(f"[Approval required for: {approval_request.name}]\n")
        print(f"Server: {approval_request.server_label}")

        # Parse and display the arguments (optional, for transparency)
        import json
        try:
            args = json.loads(approval_request.arguments)
            print(f"Arguments: {json.dumps(args, indent=2)}\n")
        except:
            print(f"Arguments: {approval_request.arguments}\n")

        # Prompt user for approval
        approval_input = input("Approve this action? (yes/no): ").strip().lower()

        if approval_input in ['yes', 'y']:
            print("Approving action...\n")
            approval_response = {
                "type": "mcp_approval_response",
                "approval_request_id": approval_request.id,
                "approve": True
            }
        else:
            print("Action denied.\n")
            approval_response = {
                "type": "mcp_approval_response",
                "approval_request_id": approval_request.id,
                "approve": False
            }

        # Add the approval response to the conversation
        openai_client.conversations.items.create(
            conversation_id=conversation.id,
            items=[approval_response]
        )

        # Get the actual response after approval or denial
        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
            input=""
        )
    ```

1. Save **agent_client.py**.
1. Review the completed code. It creates a conversation, adds user messages with `conversations.items.create()`, creates agent responses with `responses.create()`, detects `mcp_approval_request` responses, and sends an `mcp_approval_response` after you approve or deny the lookup.

## Test the integration

You're ready to run the client and confirm that it can retrieve knowledge-base information through the agent.

1. In the `Lab-02-integrate-agent-with-foundry-iq\python` folder, right-click and select **Open in Integrated Terminal**.
1. Create a virtual environment and install dependencies:

    ```
    python -m venv labenv
    .\labenv\Scripts\Activate.ps1
    pip install -r requirements.txt
    ```

1. Sign in to Azure:

    ```
    az login
    ```

    > **Note**: If you have subscriptions in multiple tenants, you may need to include the `--tenant` parameter. For details, see [Sign into Azure interactively using the Azure CLI](https://learn.microsoft.com/cli/azure/authenticate-azure-cli-interactively).

1. Complete the browser sign-in flow and select the subscription that contains your Foundry project if prompted.
1. Run the application:

    ```
    python agent_client.py
    ```

1. Test the following queries. When prompted, enter **yes** to approve the Foundry IQ lookup.

    **Product categories**

    ```
    What types of outdoor products does Contoso offer?
    ```

    **Specific product details**

    ```
    Tell me about the weatherproof features of your tents.
    ```

    **Product comparison**

    ```
    What's the difference between your daypacks and expedition backpacks?
    ```

    **Accessories and add-ons**

    ```
    What camping accessories would you recommend for a weekend hiking trip?
    ```

    **Follow-up question**

    ```
    How much do those items typically cost?
    ```

1. Type `history` to view the complete conversation history.
1. Type `quit` when you're done testing.

### Review the results

Consider the following aspects of the agent's responses:

- **MCP approval flow**: Each knowledge-base lookup requires your approval.
- **Accuracy**: The agent retrieves information from the indexed product documents.
- **Citations**: The response may include source references or document IDs.
- **Context awareness**: The agent maintains context for follow-up messages in the same conversation.
- **Grounding**: The agent should state clearly when no relevant information is found in the knowledge base.
- **Error handling**: The client handles connection and response errors gracefully.

## Summary

In this exercise, you:

- Used an existing Foundry project and deployed models.
- Created a product-expert agent and configured Foundry IQ.
- Added Contoso product documents to an Azure Blob Storage knowledge source.
- Created and connected an Azure AI Search-backed knowledge base.
- Configured the agent to request approval before querying the knowledge base.
- Connected a Python client application to the agent and tested approval-controlled knowledge retrieval.
