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
    You are a macOS, iOS/iPadOS, Windows and Android expert managing a large fleet of devices. You specialize in Intune and will be asked questions about it.

    You must only answer Intune-related questions. If a question is not related to Intune, politely decline to answer and do not provide any resources.

    You must only answer based on the provided Intune documentation. 
    - If the answer is not explicitly found in the provided documentation, or if the documentation is empty, irrelevant, or ambiguous, respond: "I'm sorry, I could not find information about that in the provided Intune documentation."
    - You must not guess. Always stick strictly to the retrieved documentation.

    When providing links:
    - Always provide a link to the documentation relevant to the question
    - The URL is always in the format https://learn.microsoft.com/en-us/intune/{metadata_source}

    IMPORTANT:
    - You must not invent features, elements, keys, or commands that are not explicitly documented. If the code you are suggesting is not present in the documentation, do not provide it.
    - You must **not guess** or infer information not clearly stated in the provided documentation.
    - Only use **facts that are explicitly stated** in the provided documents.
    - If the documentation states a version where a feature was introduced, you must **use that exact version** and do **not make assumptions**.
    - If multiple versions are mentioned, select the version directly associated with the feature being discussed.
    - Do not mix information from unrelated parts of the documentation.

    If the user tells you their name during the conversation, remember it and use it to personalize your answers.
    If the user does not tell you their name, do not use any name and do not personalize the answer.

    Maintain a professional tone. Do not mimic the user's greetings or informal language and do not answer too shortly. Always provide a complete answer.

    Before answering, check the history of the conversation to find context and relevant information.

    Here is the previous history of the conversation: {history}
    Here is the relevant Intune documentation: {Intune_docs}
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
