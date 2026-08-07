---
lab:
  title: Querying your own data and building a vector store
  description: Use Azure OpenAI embeddings and FAISS to chunk, index, search, and cite your own documents.
  level: 300
  duration: 120
  islab: true
  status: 'released'
---

# Querying your own data and building a vector store

In this exercise, you'll build the retrieval part of a Retrieval-Augmented Generation (RAG) system. You'll load documents, split them into token-aware chunks, turn those chunks into embeddings, store them in a FAISS vector index, and retrieve the passages that best match a question.

You'll also filter results by metadata, remove duplicate or very short chunks, use MMR to avoid repetitive results, and package retrieved passages with citations for a later answer-generation step.

This exercise takes approximately **120** minutes.

## Learning goals

By the end of this exercise, you'll be able to:

- Explain why applications retrieve information from their own documents
- Split documents into token-aware chunks with metadata
- Create embeddings and store them in a FAISS index
- Run semantic searches and interpret similarity scores
- Improve retrieval with filtering, deduplication, minimum chunk length, and MMR
- Create citation-ready retrieval results

## Prerequisites

- An active [Azure subscription](https://azure.microsoft.com/pricing/purchase-options/azure-account)
- [Python 3.13](https://www.python.org/downloads/) or later installed
- [Visual Studio Code](https://code.visualstudio.com/) installed, with the Python and Jupyter extensions
- A web browser
- Basic familiarity with Python, Jupyter notebooks, and terminal commands

> A Foundry project has been set up for you. This exercise requires an **embeddings model deployment**. The optional grounded-answer section also requires a chat model deployment, such as **gpt-5.4-mini**.
>
> **Important:** Save the Azure OpenAI endpoint, API key, embeddings deployment name, and chat deployment name in a local text file, such as Notepad. You'll use them in this and later exercises.
>
> **Security note:** Never place API keys directly in a notebook or commit them to GitHub. Do not share endpoints, API keys, or screenshots that expose them. Mask these values before sharing a screenshot or log.

# Find connection details

1. If you already saved your **Azure OpenAI endpoint**, **API key**, and the required **deployment names** from an earlier exercise, skip ahead to **Set up the notebook**. Otherwise, follow the steps below.
1. Open the [Microsoft Foundry portal](https://ai.azure.com) at `https://ai.azure.com` and sign in with your Azure credentials.
1. On the home page, select the project set up by your trainer or lab environment.

    ![Screenshot of the Foundry portal showing project details.](../../media/home-page.png)

    Selecting the project opens its home page.

    ![Screenshot of the Foundry project home page, showing API key, Project endpoint, and Azure OpenAI endpoint fields.](../../media/project-home-page-1.png)

1. Copy the **Azure OpenAI endpoint** and an **API key**. For this notebook, use the Azure OpenAI endpoint, not the Project endpoint.

    ![Screenshot of the API key, Project endpoint, and Azure OpenAI endpoint fields.](../../media/project-endpoint-copy.png)

1. Confirm the names of the deployed models using any of these options:
    - Under **Use a model**, select **View deployments**
    - On the project home page, scroll down and check **Recent work** or **All**
    - In the top menu, select **Build**, then **Models**

    ![Screenshot of the View deployments page, listing deployed models.](../../media/view-deployments.png)

    This notebook needs an **embeddings deployment**. It uses this deployment for every chunk and search query. If you plan to run the optional grounded-answer section, also note the **gpt-5.4-mini** deployment name.

    > **Important:** gpt-5.4-mini is a chat model. It cannot replace the embeddings deployment required by the vector-store steps.

1. Save the following values in your local text file:
    - Azure OpenAI endpoint
    - API key
    - Embeddings deployment name
    - gpt-5.4-mini deployment name, if available

    > **Tip**: If you cannot find an embeddings deployment, check with your trainer before continuing. The notebook cannot build a vector store without one.

# Set up the notebook

1. If you already downloaded and extracted this repository's ZIP file in a previous exercise, skip ahead to step 5. Otherwise, continue with the download steps below.
1. Open the [lab files on GitHub](https://github.com/Kiran-255666/agentic-ai-azure-ai-foundry-labs).
1. Select the green **`<> Code`** button, then select **Download ZIP**.
1. Extract the ZIP file to a folder on your computer.
1. In the extracted repository, open this folder:

    ```
    agentic-ai-azure-ai-foundry-labs\labfiles\Day-01-summary\lab-03-build-vector-store-and-indexes\python
    ```

    This folder contains:
    - `lab.ipynb`, the notebook for this exercise
    - `data`, a folder containing sample `.txt` documents

1. Open the `python` folder in Visual Studio Code. In File Explorer, select the address bar, type `code .`, and press Enter. If this doesn't work, open the folder manually from Visual Studio Code.
1. Open the integrated terminal in Visual Studio Code.
1. Set these PowerShell environment variables for the current terminal session. Replace every placeholder with the values you saved earlier:

    ```powershell
    $env:AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com/"
    $env:AZURE_OPENAI_API_KEY = "your_azure_openai_api_key"
    $env:AZURE_OPENAI_API_VERSION = "2024-10-21"
    $env:AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT = "your_embeddings_deployment_name"
    $env:AZURE_OPENAI_CHAT_DEPLOYMENT = "your_gpt-5.4-mini_deployment_name"
    ```

    The chat deployment variable is only needed for the optional grounded-answer section. Do not use gpt-5.4-mini as the value of `AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT`.

    > These variables apply only to the current PowerShell session. Set them again if you close the terminal, restart Visual Studio Code, or open a new terminal.

1. Open `lab.ipynb`. When Visual Studio Code asks you to choose a kernel, select your Python environment with Jupyter support.
1. Run the first notebook cell to install the required packages. If you see a prompt to restart the kernel after installation, restart it before continuing.

## Update the configuration cell (Note: We have the code updated in the mentioned files instructions but verify before you start the execution, so that there are no indentation issues)

Before running the notebook's Azure OpenAI configuration cell, make sure it does not contain any real endpoint or API key as a default value. It should read values only from the PowerShell environment variables you set above.

Replace the configuration cell with this code if needed:

```python
import os
from openai import AzureOpenAI

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21").strip()

EMBEDDINGS_DEPLOYMENT = os.getenv(
    "AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT", ""
).strip()

CHAT_DEPLOYMENT = os.getenv(
    "AZURE_OPENAI_CHAT_DEPLOYMENT", ""
).strip()

if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
    raise ValueError(
        "Missing AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY. "
        "Set the PowerShell environment variables before running this notebook."
    )

if not EMBEDDINGS_DEPLOYMENT:
    raise ValueError(
        "Missing AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT. "
        "This exercise requires an embeddings model deployment."
    )

client = AzureOpenAI(
    api_version=API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
)

print("AzureOpenAI client ready")
print("Embeddings deployment:", EMBEDDINGS_DEPLOYMENT)
print("Chat deployment:", CHAT_DEPLOYMENT or "Not configured")
```

Run this cell, then run the connectivity-check cell. It embeds a short test string and prints the returned vector length. If that succeeds, your endpoint, key, and embeddings deployment are working.

# Understand retrieval

Read the notebook's theory section before moving on. Querying your own data means answering questions from documents you control, such as policies, manuals, wikis, or tickets, instead of relying only on a model's training data.

The notebook builds this sequence:

flowchart LR
    A[Documents] --> B[Chunks]
    B --> C[Embeddings]
    C --> D[FAISS Index]
    D --> E[Query Embedding]
    E --> F[Matching Passages]

Retrieved passages make it possible to ground an answer in current source text and return citations to the chunks used.

# Load documents

The notebook provides two options:

1. **Option A** loads a small built-in corpus about tokenization, embeddings, and vector stores.
1. **Option B** loads the `.txt` files in the local `data` folder. The folder already includes three sample files: AI usage guidelines, a RAG pipeline runbook, and vector-store best practices.

For this lab, run Option A first. Then run Option B to replace the built-in corpus with the supplied files from `data`. Check the printed document count and sample filename before continuing.

# Create token-aware chunks

Run the chunking cells. They use `tiktoken` to split documents into chunks of roughly 400 tokens, with a 50-token overlap. Every chunk keeps the source document ID, title, unique chunk ID, text, and token count.

Review the printed chunk count and preview. If you add your own files to `data`, rerun the data-loading and chunking cells before building the index again.

# Build the FAISS vector store

Run the embedding and FAISS cells in order. The notebook embeds every chunk with your embeddings deployment, normalizes the vectors, then adds them to a FAISS `IndexFlatIP` index.

Because the vectors are normalized, FAISS inner-product scores work as cosine-similarity scores. A higher score means the chunk is more semantically similar to the query.

# Search and filter results

Run the `search` function and its example query. Review each result's rank, score, document title, chunk ID, token count, and text preview.

Next, run the metadata-filtering section. It creates a temporary index containing only chunks that match a filter, such as a document title or document ID. Change the filter and query values to see how the returned results change.

# Improve retrieval quality

Run the retrieval-quality cells in order. The notebook:

- Normalizes whitespace in chunk text
- Drops chunks under 20 tokens
- Removes duplicate chunks with a content hash
- Uses MMR to keep top results relevant without returning several near-identical passages

Run the MMR example and compare its output with the plain semantic search results.

# Create citation-ready results

Run the `grounding_bundle` and `print_bundle` cells. They package results with citation IDs such as `[S1]`, document metadata, chunk text, and similarity scores. This is the information a later answer-generation step needs to cite its sources.

# Optional: generate a grounded answer

If you set `AZURE_OPENAI_CHAT_DEPLOYMENT` to your gpt-5.4-mini deployment, run the `grounded_answer` cell. Then uncomment and run the example at the end of that section.

The chat model receives the retrieved passages as sources and is instructed to answer only from those sources, with inline citations such as `[S1]`. Skip this section if no chat deployment is available.

# Save and reload the vector store

Run the persistence cells to save the FAISS index, chunk metadata, and embeddings matrix in a local `vector_store_out` folder. Then run the load cell to confirm the files can be restored without creating embeddings again.

# Run a quick check

Run the final evaluation cells. They test whether expected keywords appear in the top results for a few sample questions. This is a simple check that the retrieval pipeline is returning relevant content.

## Summary

You loaded local documents, split them into token-aware chunks, created Azure OpenAI embeddings, and stored them in a FAISS vector index. You searched the index, filtered and diversified results, created citation-ready retrieval bundles, and optionally used gpt-5.4-mini to generate an answer based only on retrieved passages.