![intunebuddylogo](https://github.com/user-attachments/assets/c6484b63-0652-4772-b28b-24635d7e29e9)

**Intune Buddy** is a simple documentation chatbot that helps you find answers about [Intune](https://learn.microsoft.com/intune).  
It uses local Intune documentation files and a lightweight AI model to answer your questions accurately.

![Work in Progress](https://img.shields.io/badge/status-work_in_progress-yellow)
![License](https://img.shields.io/github/license/almenscorner/IntuneBuddy)
![Python Version](https://img.shields.io/badge/python-3.9+-blue)

> ⚡ **Work in Progress**  
> Intune Buddy is still under active development. Things might change, break, or get better rapidly!

---

## ✨ Features

- Search Intune documentation locally.
- Intelligent answers based strictly on real docs — no guessing!
- Automatic updates if documentation changes (via Git pull).
- Works offline after setup (requires Ollama).
- Supports flexible models (default: `gemma3:12b`).
- Clean, terminal-based chat experience.

---

## :clapper: Demo

https://github.com/user-attachments/assets/325750da-cc0c-4109-b5b8-5bccc730bef1

---

## 🚀 Requirements

- Python 3.9+ (3.13 unsupported).
- [Ollama](https://ollama.com/) installed and running locally.
- [Git](https://git-scm.com/) installed.
- On Windows, Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/.

---

## 📦 Installation

Clone this repository:

```bash
git clone https://<your-username>:<your-token>@github.com/almenscorner/IntuneBuddy.git
OR
Download the code as a ZIP file and extract it.

cd IntuneBuddy

pip install -e .
```
> **Note**: The `-e` flag installs the package in "editable" mode, allowing you to make changes to the code without reinstalling.

---

## 🛠️ Usage

Simply run:
```bash
intune-buddy
```

You can also enable debug mode:
```bash
intune-buddy --debug
```

Or even change the model used:
```bash
intune-buddy --model <model-name>
```

To copy the last message from the chatbot to your clipboard, just type `copy` in the chat.
```bash
🧑 You: copy

🤖 Buddy: Last message copied to clipboard.
```
> **Note**: The chatbot will only copy the last message from the chatbot to your clipboard. It will not copy any other messages or context.

Configuration options,

`config help` will show you all available options:
```bash
🧑 You: config help

🤖 Buddy: Configuration commands,

 • set emoji – Set your preferred emoji                                                                               
 • set name – Set your name                                                                                 
 • set color – Set your preferred color                                                                               
 • clear config – Clear all settings                                                                              
 • show config – Show current settings  
```

`show config` will show you the current settings:
```bash
🧑 You: show config

🤖 Buddy: Current config,

 • User Name: You                                                                                   
 • User Emoji: 🧑                                                                                    
 • User Color: yellow 
```

`clear config` will clear all settings:
```bash
🧑 You: clear config

🤖 Buddy: All settings cleared.
```

`set emoji` lets you configure the emoji for you
```bash
🧑 You: set emoji

Please enter your preferred emoji (leave empty for 🧑): 😈

😈 You:
```

`set name` lets you configure you're name
```bash
😈 You: set name

Please enter your name (leave empty for 'You'): Mr Awesome

😈 Mr Awesome:
```

`set color` lets you configure the color of your name
```bash
😈 Mr Awesome: set color

Please enter your preferred color (leave empty for 'yellow'): cyan
```
---

## ⚠️ Important Notes
- This chatbot only answers based on Intune documentation.
- It will not invent answers or guess things not in the docs.
- If the information isn’t found, it will tell you.
- It automatically updates the vector database when Intune documentation changes.
- All processing happens locally on your machine — no data is sent to the cloud. 
    - Because of this, your hardware needs to be capable of running the model. By default, the chatbot uses the `gemma3:12b` model, which is a 12-billion-parameter model and requires fairly powerful hardware.
    - If you experience performance issues, you can switch to a smaller model like `gemma3:4b`, which requires significantly less resources. However, keep in mind that using a smaller model may impact the quality of the answers.

Remember: **the chatbot is only as good as the documentation it is trained on**.

- If the official documentation is **poorly structured** or **contains incorrect information**, the chatbot will also provide **poor or incorrect results**.
- **Garbage in, garbage out**: If you provide a poorly worded question, lacking important details, the chatbot might not be able to give you a good or accurate answer.

For best results:
- Ask **clear and specific questions**.
- Understand that the chatbot **only knows what the documentation contains** – it cannot "make up" information or correct mistakes from the source material.

Thanks for understanding! 🙌

---

## 🤖 What’s Going on Behind the Scenes?

When you run Intune Buddy, a lot happens automatically to give you a smooth experience:
1.	Documentation Sync
    - The chatbot checks if the documentation repository exists.
    - If not, it clones the official documentation from GitHub.
    - If it already exists, it pulls the latest changes to ensure you always have up-to-date docs.
2.	Document Indexing
    - It hashes the documentation files to detect what has changed.
    - Only new or updated files are split into chunks and added to the vector database.
    -	This makes it fast and avoids rebuilding everything unnecessarily.
3.	Vector Database (Chroma)
    -	The text chunks are embedded using an embedding model (mxbai-embed-large via Ollama).
    -	A vector database is created and updated, allowing the chatbot to search your documentation efficiently.
4.	Question Handling
    -	When you ask a question, the chatbot first retrieves the most relevant documentation chunks.
    -	It then feeds your question plus the retrieved content into a locally running language model (Gemma 3B or 12B).
    -	The model generates a complete answer based only on what is found in the official documentation.

---

## 🧑‍💻 Contributing

Feel free to fork and submit pull requests!
Issues and ideas are very welcome.


--- 

## 📄 License

This project is licensed under the MIT License.
