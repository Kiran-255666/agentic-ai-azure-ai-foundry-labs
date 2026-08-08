---
lab:
    title: 'Build AI agents with portal and VS Code'
    description: 'Create an AI agent using both Microsoft Foundry portal and the Foundry Toolkit VS Code extension with built-in tools like file search and code interpreter.'
    level: 300
    duration: 45
    islab: true
    status: 'released'
---

# Build AI agents with portal and VS Code

In this exercise, you'll build an AI agent solution using a Microsoft Foundry project that has already been deployed and prepared for the lab. You'll create and configure an agent in the Foundry portal, then interact with it from Visual Studio Code by using the Foundry Toolkit extension and a Python client application.

This exercise takes approximately **45** minutes.

> **Note**: Some of the technologies used in this exercise are in preview or active development. You may experience unexpected behavior, warnings, or errors.

## Prerequisites

Before starting this exercise, ensure you have:

- Access to the Microsoft Foundry project prepared by your trainer or lab environment
- Permission to create and configure agents in that project
- [Visual Studio Code](https://code.visualstudio.com/) installed on your local machine
- [Python 3.13](https://www.python.org/downloads/) or later installed
- [Git](https://git-scm.com/downloads) installed on your local machine
- Basic familiarity with Azure AI services and Python programming
- Install Azure CLI using the link- https://aka.ms/installazurecliwindows

> **Important**: The Microsoft Foundry project, resource, region, subscription, and deployed model are already provided for this lab. Do **not** create a new Foundry resource or project.

> Python 3.13 is available, but some dependencies may not yet be compiled for that release. The lab has been successfully tested with Python 3.13.12.

## Open the existing Microsoft Foundry project

Microsoft Foundry projects organize models, resources, data, and other assets used to develop an AI solution. For this lab, use the existing project prepared by your trainer or lab environment. Do **not** create a new project, Foundry resource, or model deployment.

1. Open the [Microsoft Foundry portal](https://ai.azure.com) at `https://ai.azure.com` and sign in using your Azure credentials. Close any tips or quick-start panes that appear.

1. On the project home page, select **Start building** in the **Build an agent** card.

    ![Microsoft Foundry project home page with the Start building button highlighted in the Build an agent card.](../../media/04-03-02.png)

1. If Foundry displays the **All resources** page, select the existing project provided for this lab. In this example, the project is named `hakunamatata1`.

    ![All resources page showing the existing hakunamatata1 project.](../../media/04-03-01.png)

1. In the **Create an agent** dialog, enter `it-support-agent` as the **Agent name**.

1. Select **Create**.

    ![Create an agent dialog with it-support-agent entered as the agent name.](../../media/04-03-03.png)

The agent playground opens. An available deployed model should already be selected for you.

    ![Screeshot of the playground.](../../media/04-03-04.png)

> **Important**: The existing project already contains the required resources and deployed model. Continue by configuring the agent; do not select **Create project**, deploy another model, or change the project resource settings.

## Configure your agent with instructions and grounding data

Now configure the agent with instructions, File search, and Code interpreter.

1. In the agent playground, set **Instructions** to:

    ```prompt
    You are an IT Support Agent for Contoso Corporation.
    You help employees with technical issues and IT policy questions.

    Guidelines:
    - Always be professional and helpful
    - Use the IT policy documentation to answer questions accurately
    - If you don't know the answer, admit it and suggest contacting IT support directly
    - When creating tickets, collect all necessary information before proceeding
    ```

    ![Screeshot.](../../media/04-03-05.png)

1. Download the IT policy document from the lab repository:

    ```text
    https://github.com/Kiran-255666/agentic-ai-azure-ai-foundry-labs/blob/main/labfiles/Day-04/Lab-03-build-agent-portal-and-vscode/IT_Policy.txt
    ```

    Save the file locally as `IT_Policy.txt`.

    > **Note**: This document contains sample policies for password resets, software installation requests, and hardware troubleshooting.

1. Return to the agent playground. In the **Tools** section, select **Add**. You will get a dropdown; under Most Popular, you can find **Code interpreter**. Toggle the switch from off to on. If it is not found, select **Add** again, then click on **Add tools**. You can then choose **Code interpreter** from the displayed options and click on **Add tool**.

    ![Screeshot.](../../media/04-03-07.png)

1. In the **Tools** section, select **Add**. You will get a dropdown; then click on **Add tools**. You can then choose **File search** from the displayed options and click on **Add tool**.

    ![Screeshot.](../../media/04-03-06.png)

1. After adding the tool, you will be redirected to a page where you can see **Drag and drop files here or browse for files**. You can either drag and drop the `IT_Policy.txt` file or browse your local files and upload it. If you have not downloaded the file earlier, you can download it from [GitHub](https://github.com/Kiran-255666/agentic-ai-azure-ai-foundry-labs/blob/main/labfiles/Day-04/Lab-03-build-agent-portal-and-vscode/IT_Policy.txt). After attaching the file, you will see the Status as **Success**. Then, select **Attach**.

1. Wait for the file to be indexed.
1. Download the system performance data file:

    ```text
    https://github.com/Kiran-255666/agentic-ai-azure-ai-foundry-labs/blob/main/labfiles/Day-04/Lab-03-build-agent-portal-and-vscode/system_performance.csv
    ```

    Save the file locally as `system_performance.csv`.

1. To the right of **</> Code interpreter**, select **+ Files**, then upload `system_performance.csv` by either drag and drop the `system_performance.csv` file or browse your local files and upload it.After attaching the file, you will see the Status as **Success**. Then, select **Attach**.

    > **Note**: This CSV file contains simulated CPU, memory, and disk metrics over time.

1. Save the agent.

## Test your agent

Test the agent to confirm that it uses the grounding data and code interpreter.

1. In the playground chat pane, enter:

    ```text
    What's the policy for password resets?
    ```

1. Review the response. The agent should use the IT policy document.

    ![Screeshot.](../../media/04-03-08.png)

1. Enter:

    ```text
    How do I request new software?
    ```

1. Review the response and observe how the agent uses the uploaded policy data.

    ![Screeshot.](../../media/04-03-09.png)

1. Test Code interpreter by entering:

    ```text
    Can you analyze the system performance data and tell me if there are any concerning trends?
    ```

    ![Screeshot.](../../media/04-03-10.png)

1. Request a visualization:

    ```text
    Create a chart showing CPU usage over time from the performance data
    ```

    ![Screeshot.](../../media/04-03-11.png)

The agent should use **Code interpreter** to analyze the CSV performance data, process the CPU usage values, and generate a visualization showing CPU usage over time. The visualization may be generated successfully, but in some cases, you may not be able to download the generated file from the agent playground. If this happens, you can copy the code generated by the agent and run it in **VS Code**, **Jupyter Notebook**, or **Google Colab** using the same CSV data. This should reproduce the visualization and allow you to view it successfully.
    ![Screeshot.](../../media/04-03-12.png)

## Interact with your agent using VS Code

The Foundry Toolkit for VS Code extension lets you work with Foundry project resources without leaving Visual Studio Code.

### Install and configure the extension

If Foundry Toolkit is already installed, skip this section.

1. Before starting the lab, install Azure CLI using the following link: [https://aka.ms/installazurecliwindows](https://aka.ms/installazurecliwindows). Click the link to download the installer. The download will start automatically and the installer will be available in your **Downloads** folder. If the download does not start automatically, copy and paste the link into your browser.

    ![Screenshot of the Azure CLI installer downloaded in the Downloads folder.](../../media/azure-cli-download.png)

2. After the download is complete, run the installer and follow the installation steps.

    ![Screenshot of the Azure CLI installation setup wizard.](../../media/azure-cli-install-wizard.png)

As a developer, you may spend time working in the Microsoft Foundry portal, but most development tasks are typically performed in Visual Studio Code. The Foundry Toolkit extension enables you to work with Foundry project resources directly within Visual Studio Code, allowing you to stay within your development environment.

1. Open Visual Studio Code.

2. Select **Extensions** from the left pane (or press **Ctrl+Shift+X**).

3. Search the Extensions Marketplace for the **Foundry Toolkit** extension from Microsoft and select **Install**.

    > **Note**: The extension is currently listed as **Foundry Toolkit for VS Code**, but some VS Code labels, commands, or older screenshots may still refer to **AI Toolkit**. In this lab, treat those names as referring to the same extension experience. Below is a snippet of the new version, which is the official **Foundry Toolkit for VS Code** extension published by Microsoft.

    ![Screenshot of the Foundry Toolkit for VS Code extension in the Extensions Marketplace.](../../media/foundry-toolkit-extension.png)

4. After installing the extension, select its icon in the sidebar to open the Foundry Toolkit view.

    You'll initially see the default **My Resources** and **Developer Tools** sections in the panel, but they won't be populated with your actual project data. To use the extension's full functionality and complete this lab, you need to sign in to your Azure account.

    ![Screenshot of the Foundry Toolkit sidebar showing My Resources and Developer Tools sections before sign-in.](../../media/foundry-toolkit-sidebar.png)

5. Open the integrated terminal (**Ctrl+Shift+`**) and run the following command to sign in to Azure:

    ```powershell
    az login
    ```

    A browser window will open automatically, asking you to sign in. Select the email address provided by your trainer, then select **Continue**.

    Back in the terminal, you'll see a prompt similar to:

    ```
    Select a subscription and tenant (Type a number or Enter for no changes):
    ```

    Type **1** and press **Enter** to select the default subscription (or the one provided by your trainer). You'll then see confirmation that the default subscription has been set, along with your account details.

    > **Note**: Sometimes you might additionally be prompted to sign in to Azure below this step too — if so, complete that sign-in the same way, using the same assigned account. You might be prompted to authenticate more than once during the setup process. If prompted, use the same assigned account to complete each authentication request.

    If the sign-in completes without any issues, skip ahead to step 8. If you see an error saying the `az` command isn't recognized, go to step 6. If the sign-in window closes or gets cancelled partway through, go to step 7.

6. If the `az` command isn't recognized (e.g., `'az' is not recognized as a name of a cmdlet, function, script file, or executable program`), Azure CLI likely isn't installed correctly, or the terminal session started before the installation finished updating your PATH.

    > **Troubleshooting**: To fix this:
    > 1. Close and reopen the integrated terminal (or restart VS Code entirely), then try `az login` again.
    > 2. If the error persists, uninstall and reinstall Azure CLI using the following commands:
    >    ```powershell
    >    winget uninstall Microsoft.AzureCLI
    >    winget install Microsoft.AzureCLI
    >    ```
    > 3. Restart the terminal after installation completes, then run `az login` again.

7. If the sign-in window is closed accidentally or cancelled (you may see `User cancelled the Accounts Control Operation`), run the following commands to reset the session and try again:

    ```powershell
    az logout
    az login
    ```

8. Verify that a default project is already active. The project name will appear under **My Resources**.

    > **Tip**: To switch to a different project, select **Models** in the left panel under **My Resources**. You'll see two options: **Switch Project** and **Create Project**. Select **Switch Project** to change your default Azure Resources project.

    ![Screenshot of the Foundry Toolkit sidebar showing the active default project under My Resources after signing in.](../../media/foundry-toolkit-default-project.png)

### Test your agent in VS Code

1. Under **Microsoft Foundry Resources**, select **Set Default Project**.
1. Select the existing project provided for the lab. If a default project is active already, its name appears in the resources list.

    ![Screenshot](../../media/04-03-13.png)

1. Under **MY RESOURCES**, select **Agents**

    ![Screenshot](../../media/04-03-14.png)

1. Expand the project. Under **Prompt Agents**, select `it-support-agent` to open Agent Builder.

    ![Screenshot](../../media/04-03-15.png)

1. In the playground chat pane, enter:

    ```text
    What is the policy for reporting a lost or stolen device?
    ```
    ![Screenshot](../../media/04-03-16.png)

1. Review the response. It should use the grounding data uploaded earlier.
    ![Screenshot](../../media/04-03-17.png)

> **Tip**: Use the built-in playground to quickly test agent instructions and knowledge without writing code.

## Create a client application to interact with your agent

Create a Python application that interacts with the agent programmatically.

1. In VS Code, open the Command Palette by pressing **Ctrl+Shift+P**.
1. Enter **Git: Clone** and select the command.
1. Enter this repository URL:

    ```text
    https://github.com/MicrosoftLearning/mslearn-ai-agents.git
    ```

1. Select a local location to clone the repository.
1. When prompted, select **Open** to open the cloned repository in VS Code.
1. Select **File > Open Folder**, browse to `mslearn-ai-agents/Labfiles/01-build-agent-portal-and-vscode/Python`, then select **Select Folder**.
1. In Explorer, open `agent_with_functions.py`. If the file is empty, replace it with the lab's provided `agent_with_functions.py` implementation.
1. Save the file.

> **Note**: The supplied client application uses `AIProjectClient`, retrieves the named portal agent, creates a conversation, sends user prompts through the Responses API, and saves generated charts or cited container files under `agent_outputs`.

### Configure environment and run the application

1. In Explorer, locate `.env.example` and `requirements.txt`.
1. Duplicate `.env.example` and rename the copy to `.env`.
1. In `.env`, replace the placeholder endpoint with the endpoint of the existing lab project:

    ```text
    PROJECT_ENDPOINT=<your_project_endpoint>
    AGENT_NAME=it-support-agent
    ```

    To get the endpoint, in Foundry Toolkit right-click the active project and select **Copy Endpoint**. If that command is unavailable, open the existing project in the Foundry portal and copy the project endpoint from its overview page.

1. Save `.env`.
1. Open **Terminal > New Terminal** in VS Code.
1. Create and activate a virtual environment, then install dependencies:

    ```powershell
    python -m venv labenv
    .\labenv\Scripts\Activate.ps1
    pip install -r requirements.txt
    ```

1. Authenticate to Azure:

    ```bash
    az login
    ```

1. Run the application:

    ```bash
    python agent_with_functions.py
    ```

## Test the client application

When the agent starts, test its different capabilities.

1. Test File search:

    ```text
    What's the policy for password resets?
    ```

1. Request data analysis with Code interpreter:

    ```text
    Analyze the system performance data and identify any periods where CPU usage exceeded 80%
    ```

1. Request a visualization:

    ```text
    Create a line chart showing memory usage trends over time
    ```

    The application saves generated charts and cited files in the `agent_outputs` folder and prints their local paths in the terminal.

1. Request statistical analysis:

    ```text
    What are the average, minimum, and maximum values for disk usage in the performance data?
    ```

1. Request combined analysis:

    ```text
    Find any correlation between high CPU usage and memory usage in the performance data
    ```

Observe how the agent uses File search for policy questions and Code interpreter for CSV analysis and visualizations. Type `exit` when you finish testing.

## Summary

You used an existing Microsoft Foundry project and its deployed model to create an IT support agent. You grounded it with IT policy data, enabled File search and Code interpreter, tested it in the portal and Foundry Toolkit, and interacted with it through a Python client application.