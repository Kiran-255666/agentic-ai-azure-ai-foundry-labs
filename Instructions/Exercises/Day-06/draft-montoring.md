---
lab:
    title: 'Monitor Foundry models with Azure Monitor'
    description: 'Use Azure Monitor and Log Analytics to check requests, usage, and failures for an existing Foundry model.'
    level: 300
    duration: 35
    islab: true
    status: 'released'
---

# Monitor Foundry models with Azure Monitor

In this exercise, you'll connect an existing Foundry model to Azure Monitor. You'll send its diagnostic logs and metrics to Log Analytics, run one quick test prompt, and use Azure Monitor to review the activity.

You will use the project and deployed model already provided for the training. You do not need to create a new project or deploy a model.

This exercise should take approximately **35** minutes to complete.

> **Note**: Some portal labels can differ slightly depending on your Azure subscription and resource type.

## Prerequisites

Before starting this exercise, ensure you have:

- Access to the existing Foundry project and deployed model
- Access to the Azure portal
- Permission to create or use a Log Analytics workspace
- Permission to configure diagnostic settings on the Foundry or Azure OpenAI resource

## Open the existing project

1. Open the [Microsoft Foundry portal](https://ai.azure.com) and sign in.
1. Select the training Foundry project from the project selector.
1. On the project home page, verify that a deployed chat model is available.
1. Keep this tab open. You will return here later to send a test prompt.

## Create a Log Analytics workspace

A Log Analytics workspace stores the logs that Azure Monitor collects. If your trainer already gave you a workspace, use that workspace and move to the next section.

1. Open the [Azure portal](https://portal.azure.com).
1. Search for **Log Analytics workspaces** and select it.
1. Select **Create**.
1. Enter the following details:

    - **Subscription**: Your Azure subscription
    - **Resource group**: Use the resource group for the training project when possible
    - **Name**: Enter a unique name, such as `ai-monitoring-workspace`
    - **Region**: Use the same region as the Foundry resource when possible

1. Select **Review + create**, then select **Create**.
1. After deployment completes, open the workspace.

## Send model logs to Azure Monitor

Now connect the Foundry or Azure OpenAI resource to the Log Analytics workspace.

1. In the Azure portal search box, search for the Foundry or Azure OpenAI resource used by the training project.
1. Open the resource.
1. In the left menu, select **Diagnostic settings** under **Monitoring**.
1. Select **+ Add diagnostic setting**.
1. For the name, enter `ai-model-monitoring`.
1. Under **Logs**, select the available log categories related to requests, usage, audit, and traces.
1. Under **Metrics**, select **AllMetrics**.
1. Under **Destination details**, select **Send to Log Analytics workspace**.
1. Select your Log Analytics workspace.
1. Select **Save**.

> **Tip**: The exact log category names can differ. Select the available categories that include request logs, usage logs, audit logs, and trace logs.

## Send one test prompt

You only need to send one or two prompts so that you have recent activity to view in Azure Monitor.

1. Return to the Foundry portal.
1. Open an existing agent or model playground that uses the deployed model.
1. Send the following prompt:

    ```
    Explain in one sentence why application monitoring is important.
    ```

1. Send one more prompt:

    ```
    List two signs that an AI application may have a problem.
    ```

1. Wait for the responses, then wait a few minutes for the telemetry to appear in Log Analytics.

## Review model metrics

Metrics provide a quick view of service activity.

1. Return to the Foundry or Azure OpenAI resource in the Azure portal.
1. Select **Metrics** under **Monitoring**.
1. Select **Add metric**.
1. Look for a metric related to requests, tokens, latency, errors, or throttling.
1. Select one available metric and set the time range to **Last 30 minutes**.
1. Confirm that the chart shows activity from the prompts you sent.

You do not need to create a dashboard for this lab. The goal is simply to confirm that the resource is producing metrics.

## Review logs in Log Analytics

1. Open the Log Analytics workspace.
1. Select **Logs**.
1. Run the following query to see which tables have recent data:

    ```kusto
    search *
    | where TimeGenerated > ago(1h)
    | summarize Records = count() by $table
    | order by Records desc
    ```

1. Review the result. You may see tables such as `AzureDiagnostics`, `AzureMetrics`, or resource-specific tables.
1. Run the following query to review recent metric records:

    ```kusto
    AzureMetrics
    | where TimeGenerated > ago(1h)
    | take 50
    ```

1. If the `AzureDiagnostics` table contains data, run this query:

    ```kusto
    AzureDiagnostics
    | where TimeGenerated > ago(1h)
    | take 50
    ```

1. Confirm that recent records are available. The field names and log details can vary by resource type and selected diagnostic categories.

## Create a simple alert

Alerts help you notice a problem without watching the portal constantly.

1. In the Azure portal, open **Monitor**.
1. Select **Alerts**, then select **+ Create** > **Alert rule**.
1. For **Scope**, select the Foundry or Azure OpenAI resource.
1. For **Condition**, choose an available metric related to failures, errors, latency, or throttling.
1. Set a simple threshold for the lab. For example, alert when the selected error metric is greater than zero.
1. Create or select an action group with an email notification if your environment allows it.
1. Name the rule `ai-model-alert`.
1. Select **Create alert rule**.

> **Note**: You do not need to force an error to test the alert in this lab.

## Apply monitoring practices

For a production AI solution, monitor more than the model request count. Keep these areas in mind:

- Monitor request volume, token usage, latency, errors, and throttling.
- Monitor agent tools, API calls, workflows, and knowledge retrieval if your agent uses them.
- Review agent traces and evaluations when response quality changes.
- Give each agent an owner and document the data, tools, and deployment channel it uses.
- Use least-privilege access for agents that connect to APIs, enterprise applications, or knowledge sources.
- Review costs and usage regularly before scaling to more users.

Agents can be deployed through Azure applications, Copilot Studio, Teams, Microsoft 365 Copilot, Fabric, or other business applications. The monitoring approach should remain consistent across these channels.

## Cleanup

If you created resources only for this exercise, remove them when your trainer confirms that cleanup is appropriate.

1. Open the Foundry or Azure OpenAI resource.
1. Open **Diagnostic settings** and remove `ai-model-monitoring` if it is no longer needed.
1. Open **Monitor** > **Alerts** and delete or disable `ai-model-alert` if you created it only for the lab.
1. Delete the Log Analytics workspace only if it was created only for this lab and your trainer has confirmed that it is safe to remove.

## Summary

In this exercise, you:

- Used an existing Foundry project and deployed model.
- Created or used a Log Analytics workspace.
- Sent model logs and metrics to Azure Monitor.
- Sent two quick test prompts.
- Reviewed metrics and logs.
- Created a simple alert rule.
- Identified the main monitoring areas for a production AI solution.
