#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import pyperclip

from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from rich.console import Console
from rich.markdown import Markdown
from rich import print
from rich.panel import Panel
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.history import InMemoryHistory
from argparse import ArgumentParser
from .utils import (
    retry_chain_invoke,
    ensure_model_installed,
    clean_output,
    stop_models,
    ensure_ollama_installed,
    ensure_git_installed,
)
from .config import (
    CONFIG_FILE,
    template,
    ascii_art,
    get_user_emoji,
    get_user_color,
    get_user_name,
    config_file_exists,
    handle_question,
)

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

    ensure_git_installed()
    # check if ollama is installed
    ensure_ollama_installed()

    ensure_model_installed(args.model)
    ensure_model_installed("mxbai-embed-large")

    user_emoji = get_user_emoji() if config_file_exists() else "🧑"
    user_name = get_user_name() if config_file_exists() else "You"
    user_color = get_user_color() if config_file_exists() else "yellow"

    from .vector import retreiver

    model = OllamaLLM(model=args.model)

    console = Console()

    chat_template = template()

    chat_prompt = ChatPromptTemplate.from_template(chat_template)

    chain = chat_prompt | model

    buddy_string = "[bold blue]🤖 Buddy:[/bold blue]"

    ascii_art()

    print("\nHi, I'm [bold blue]Intune Buddy[/bold blue]!")
    print("\n")
    print("I will help you find information about Intune using the documentation.")
    print("You can ask any question related to Intune.")
    print("\n")
    print("To quit, type 'q' or 'bye'.\n")
    if args.debug:
        print(
            "\n[yellow]Debug mode is enabled. Debug information will be displayed.[/yellow]"
        )

    history = []
    prompt_history = InMemoryHistory()

    try:
        while True:
            print()
            try:
                style = Style.from_dict(
                    {
                        "prompt": f"bold {user_color}",  # color the prompt
                    }
                )
            except ValueError:
                print(
                    f"[red]Invalid color '{user_color}' specified. Using default color.[/red]\n"
                )
                style = Style.from_dict({"prompt": "bold yellow"})

            question = prompt(
                f"{user_emoji} {user_name}: ", style=style, history=prompt_history
            ).strip()
            if question.lower() in ["q", "bye"]:
                print(f"\n{buddy_string} Goodbye!\n")
                # stop running ollama model
                stop_models(args.model, "mxbai-embed-large")
                break

            if question.lower() == "copy":
                if not history:
                    print(f"\n{buddy_string} No conversation history to copy.")
                    continue
                pyperclip.copy(history[-1])
                print(f"\n{buddy_string} Last message copied to clipboard.")
                continue

            config_commands = [
                "set emoji",
                "set name",
                "set color",
                "clear config",
                "show config",
                "config help",
            ]

            if question.lower() in config_commands:
                user_name, user_emoji, user_color = handle_question(
                    question.lower(), buddy_string, user_name, user_emoji, user_color
                )
                continue

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
                print()
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
                        "metadata_source": (
                            docs[0].metadata["source"].removesuffix(".md")
                            if len(docs) > 0
                            else ""
                        ),
                    }
                )
                result = clean_output(result)

                fallback_response = (
                    "I don’t have access to the relevant Intune documentation to answer your question accurately. "
                    "Please provide the documentation or refine your question."
                )

                result, retries = retry_chain_invoke(
                    chain,
                    {
                        "Intune_docs": Intune_docs,
                        "question": question,
                        "history": history,
                        "metadata_source": (
                            docs[0].metadata["source"].removesuffix(".md")
                            if docs
                            else ""
                        ),
                    },
                    fallback_response,
                )

                if retries > 0 and args.debug:
                    print(f"[yellow]⚠️ Retried {retries} times.[/yellow]")

            console.print(buddy_string, end=" ")
            console.print(Markdown(result))
            history.append(f"User: {question}")
            history.append(f"Buddy: {result}")

    except KeyboardInterrupt:
        print(f"{buddy_string} Operation cancelled by user. Exiting gracefully... 👋")
        # stop running ollama model
        stop_models(args.model, "mxbai-embed-large")
        sys.exit(0)


if __name__ == "__main__":
    main()
