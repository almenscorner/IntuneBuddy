#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import re
import subprocess

from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from rich.console import Console
from rich.markdown import Markdown
from rich import print
from rich.panel import Panel
from prompt_toolkit import prompt
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.history import InMemoryHistory
from argparse import ArgumentParser

sys.path.insert(0, os.path.dirname(__file__))


def main():
    args = ArgumentParser()

    args.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Enable debug mode.",
    )

    args.add_argument(
        "--model",
        "-m",
        type=str,
        default="gemma3:12b",
        help="Specify the model to use. Default is 'gemma3:12b'.",
    )

    args = args.parse_args()

    # check if ollama is installed
    try:
        subprocess.run(
            ["ollama", "-v"],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        # This happens if the binary doesn't exist at all
        print("[red]Ollama is not installed or not found in PATH.[/red]")
        sys.exit(1)
    except subprocess.CalledProcessError:
        # This happens if the binary exists but fails badly
        print(
            "[red]Ollama was found but it returned an error. Please check the installation.[/red]"
        )
        sys.exit(1)

    # check gemma model is installed
    cmd = ["ollama", "list"]
    output = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
    if args.model not in output.stdout:
        print(
            f"[red]Model is not installed. Please install it by running 'ollama pull {args.model}'[/red]"
        )
        sys.exit(1)

    # model = OllamaLLM(model="deepseek-r1:8b")
    from vector import retreiver

    model = OllamaLLM(model=args.model)

    console = Console()

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

    Here is the previous history of the conversation: {history}. If no history is provided, assume this is the start of the conversation.
    Here is the relevant Intune documentation: {Intune_docs}. If no documentation is provided, respond: "I don’t have access to the relevant Intune documentation to answer your question accurately. Please provide the documentation or refine your question."
    The question to answer is: "{question}"
    """

    chat_prompt = ChatPromptTemplate.from_template(template)

    chain = chat_prompt | model

    def clean_output(output: str) -> str:
        """
        Cleans the LLM output by removing unwanted patterns and unnecessary greetings.
        """
        # Remove anything between <think>...</think> tags
        output = re.sub(r"<think>.*?</think>", "", output, flags=re.DOTALL)

        # List of unwanted strings to remove
        unwanted_phrases = [
            "<think>",
            "</think>",
            "**Answer:**",
            "Hello!",
            "Hello.",
        ]

        for phrase in unwanted_phrases:
            output = output.replace(phrase, "")

        # Remove extra leading/trailing whitespace
        return output.strip()

    def ascii_munki_buddy_logo():
        logo = r"""
-----------------------------------------------------------
 ___       _                    ____            _     _       
|_ _|_ __ | |_ _   _ _ __   ___| __ ) _   _  __| | __| |_   _ 
 | || '_ \| __| | | | '_ \ / _ \  _ \| | | |/ _` |/ _` | | | |
 | || | | | |_| |_| | | | |  __/ |_) | |_| | (_| | (_| | |_| |
|___|_| |_|\__|\__,_|_| |_|\___|____/ \__,_|\__,_|\__,_|\__, |
                                                        |___/ 

🤖  Intune Buddy - Documentation Assistant
-----------------------------------------------------------
        """
        print(logo)

    ascii_munki_buddy_logo()
    print("\nHi, I'm Intune Buddy!")
    print("\n")
    print("I will help you find information about Intune using the documentation.")
    print("You can ask any question related to Intune.")
    print("\n")
    print("To quit, type 'q' or 'bye'.")
    if args.debug:
        print(
            "\n[yellow]Debug mode is enabled. Debug information will be displayed.[/yellow]"
        )

    history = []
    prompt_history = InMemoryHistory()

    try:
        while True:
            print("\n")
            style = Style.from_dict(
                {
                    "prompt": "bold yellow",  # color the prompt
                }
            )

            question = prompt("🧑 You: ", style=style, history=prompt_history)
            print("\n")
            if question.lower() in ["q", "bye"]:
                print("🤖: Goodbye!\n")
                break

            with console.status("Searching documentation...", spinner="dots"):
                if args.debug:
                    console.print(
                        Panel.fit(
                            Markdown(f"Question: {question}"),
                            title="Debug Info",
                            title_align="left",
                            border_style="yellow",
                        )
                    )

                # retriever = create_retriever(question)
                docs = retreiver.invoke(question)
                if args.debug:
                    for doc in docs:
                        console.print(
                            Panel.fit(
                                Markdown(
                                    f"Document: {doc.metadata['source']}\n\n {doc.page_content[:500]}"
                                ),
                                title="Debug Info",
                                title_align="left",
                                border_style="yellow",
                            )
                        )

                Intune_docs = "\n\n".join(doc.page_content for doc in docs)
                result = chain.invoke(
                    {
                        "Intune_docs": Intune_docs,
                        "question": question,
                        "history": history,
                        "metadata_source": docs[0]
                        .metadata["source"]
                        .removesuffix(".md"),
                    }
                )
                result = clean_output(result)

            console.print(
                Panel.fit(
                    Markdown(result),
                    title="🤖 Buddy",
                    title_align="left",
                    border_style="green",
                )
            )
            history.append(f"User: {question}")
            history.append(f"Buddy: {result}")

    except KeyboardInterrupt:
        print("🤖 Buddy: Operation cancelled by user. Exiting gracefully... 👋")
        sys.exit(0)


if __name__ == "__main__":
    main()
