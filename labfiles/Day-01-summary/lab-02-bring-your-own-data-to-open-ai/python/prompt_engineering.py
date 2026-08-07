import asyncio
import os

# Load values from the .env file
from dotenv import load_dotenv

# Azure OpenAI SDK
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

# Set to True if you want to see the complete API response
printFullResponse = False


async def main():
    try:
        # Read Azure OpenAI settings from the .env file
        azure_oai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_oai_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_oai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

        # Create the Azure OpenAI client
        client = AsyncOpenAI(
            api_key=azure_oai_key,
            base_url=azure_oai_endpoint,
        )

        # Keep running until the user types "quit"
        while True:

            # Pause so you can edit the system prompt if needed
            print(
                "------------------"
                "\nPausing the app to allow you to change the system prompt."
                "\nPress Enter to continue..."
            )
            input()

            # Read the system prompt from system.txt
            with open("system.txt", encoding="utf8") as file:
                system_text = file.read().strip()

            # Ask the user for a question
            user_text = input("Enter user message: ")

            # Exit the application
            if user_text.lower() == "quit":
                print("Exiting program...")
                break

            # Send the request to Azure OpenAI
            await call_openai_model(
                system_message=system_text,
                user_message=user_text,
                model=azure_oai_deployment,
                client=client,
            )

    except Exception as ex:
        print(f"Error: {ex}")


async def call_openai_model(system_message, user_message, model, client):

    # Read additional context from grounding.txt
    print("\nAdding grounding context from grounding.txt")

    with open("grounding.txt", encoding="utf8") as file:
        grounding_text = file.read().strip()

    # Combine the grounding text with the user's message
    user_message = grounding_text + "\n\n" + user_message

    # Create the conversation
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    print("\nSending request to Azure OpenAI...\n")

    # Send the request to the deployed model
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_completion_tokens=800,
    )

    # Print the complete response if enabled
    if printFullResponse:
        print(response)

    # Print only the model's reply
    print("Response:\n")
    print(response.choices[0].message.content)
    print()


# Start the application
if __name__ == "__main__":
    asyncio.run(main())