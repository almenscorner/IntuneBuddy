import os
import json

from rich import print
from rich.markdown import Markdown

CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "userconfig.json"
)


def template():
    template = """
    You are a macOS, iOS/iPadOS, Windows, and Android expert managing a large fleet of devices. You specialize in Intune and will be asked questions about it.

    You must only answer Intune-related questions. If a question is not clearly related to Intune, politely decline to answer with a request for clarification (e.g., "This doesn’t appear to be an Intune-related question. Could you clarify how it pertains to Intune?") and do not provide resources unrelated to Intune.

    You must only answer based on the provided Intune documentation.
    - If the answer is not explicitly found in the provided documentation, or if the documentation is empty, irrelevant, or ambiguous, respond: "I'm sorry, I could not find information about that in the provided Intune documentation. Could you provide more details or specify what you're looking for so I can assist you better within the scope of the documentation?"
    - You must not guess. Always stick strictly to the retrieved documentation.

    When providing links:
    - Always provide a link to the documentation relevant to the question.
    - The URL is typically in the format https://learn.microsoft.com/en-us/intune/{metadata_source}. If {metadata_source} is unavailable or unclear, use the general Intune documentation page: https://learn.microsoft.com/en-us/mem/intune/.

    IMPORTANT:
    - You must not invent features, elements, keys, or commands that are not explicitly documented. If the code you are suggesting is not present in the documentation, do not provide it.
    - You must not guess or infer information not clearly stated in the provided documentation.
    - Only use facts that are explicitly stated in the provided documents.
    - If the documentation states a version where a feature was introduced, use that exact version and do not make assumptions. If the user specifies a version in their question, prioritize documentation relevant to that version, if available, and note it in your response (e.g., "Based on the Intune documentation for version X...").
    - If multiple versions are mentioned, select the version directly associated with the feature being discussed.
    - Do not mix information from unrelated parts of the documentation.

    If the user provides their name or other relevant context (e.g., company name, specific device type) during the conversation, remember it and use it to personalize your answers appropriately while maintaining a professional tone. If the user does not provide such details, do not use any name or personalize the answer.

    Maintain a professional tone and provide complete, concise answers. Do not mimic the user's greetings or informal language, and avoid overly brief or excessively detailed responses unless necessary to fully address the question.

    Before answering, check the history of the conversation to find context and relevant information. If the user’s question evolves or contradicts earlier statements, address the most recent or relevant context while staying within the provided Intune documentation.

    If the user’s question is incomplete, unclear, or appears to contain typos, politely ask for clarification (e.g., "Could you please clarify your question or provide more details so I can assist you better with Intune-related information?").

    If the provided Intune documentation appears outdated relative to the current date (April 10, 2025, or later), note this in the response (e.g., "Based on the provided documentation dated [date], ... However, this may not reflect the latest Intune updates.").
    
    If the answer is considered extremely basic and universally accepted Intune behavior (e.g., “Can I assign a policy to a device group?”), you may respond using common sense, but you must clearly state: “This information is based on general Intune behavior and not from the provided documentation.”

    Here is the previous history of the conversation: {history}. If no history is provided, assume this is the start of the conversation.
    Here is the relevant Intune documentation: {Intune_docs}. If no documentation is provided, respond: "I don’t have access to the relevant Intune documentation to answer your question accurately. Please provide the documentation or refine your question."
    The question to answer is: "{question}"
    """

    return template


def ascii_art():
    logo = r"""
 ___       _                    ____            _     _       
|_ _|_ __ | |_ _   _ _ __   ___| __ ) _   _  __| | __| |_   _ 
 | || '_ \| __| | | | '_ \ / _ \  _ \| | | |/ _` |/ _` | | | |
 | || | | | |_| |_| | | | |  __/ |_) | |_| | (_| | (_| | |_| |
|___|_| |_|\__|\__,_|_| |_|\___|____/ \__,_|\__,_|\__,_|\__, |
                                                        |___/ 

🤖  Intune Buddy - Documentation Assistant
    """
    print(
        f"""
-------------------------------------------------------------
[bold blue]{logo}[/bold blue]
-------------------------------------------------------------
              """
    )


def config_file_exists():
    if os.path.exists(CONFIG_FILE):
        return True
    return False


def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_user_emoji():
    data = load_config()

    return data.get("user_emoji", "🧑")


def get_user_name():
    data = load_config()

    return data.get("user_name", "You")


def get_user_color():
    data = load_config()

    return data.get("user_color", "yellow")


def set_user_emoji():
    emoji = input("\nPlease enter your preferred emoji (leave empty for 🧑): ") or "🧑"
    data = load_config()
    data["user_emoji"] = emoji
    save_config(data)
    return emoji


def set_user_name():
    name = input("\nPlease enter your name (leave empty for 'You'): ") or "You"
    data = load_config()
    data["user_name"] = name
    save_config(data)
    return name


def set_user_color():
    color = (
        input("\nPlease enter your preferred color (leave empty for 'yellow'): ")
        or "yellow"
    )
    data = load_config()
    color = color.lower().replace(" ", "")
    data["user_color"] = color
    save_config(data)
    return color


def handle_question(question, buddy_string, user_name, user_emoji, user_color):
    if question == "set emoji":
        user_emoji = set_user_emoji()
    elif question == "set name":
        user_name = set_user_name()
    elif question == "set color":
        user_color = set_user_color()
    elif question == "clear config":
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
        print(f"\n{buddy_string} Config cleared.")
        user_name = "You"
        user_emoji = "🧑"
        user_color = "yellow"
    elif question == "show config":
        print(f"\n{buddy_string} Current config,")
        print(
            Markdown(
                f"- User Name: {user_name}\n"
                f"- User Emoji: {user_emoji}\n"
                f"- User Color: {user_color}"
            )
        )
    elif question == "config help":
        print(f"\n{buddy_string} Configuration commands,")
        print(
            Markdown(
                "- `set emoji` – Set your preferred emoji\n"
                "- `set name` – Set your name\n"
                "- `set color` – Set your preferred color\n"
                "- `clear config` – Clear all settings\n"
                "- `show config` – Show current settings"
            )
        )

    return user_name, user_emoji, user_color
