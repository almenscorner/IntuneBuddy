# Intune Buddy

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

## 🚀 Requirements

- Python 3.9+
- [Ollama](https://ollama.com/) installed and running locally.

---

## 📦 Installation

Clone this repository:

```bash
git clone https://github.com/almenscorner/IntuneBuddy.git
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

---

## ⚠️ Important Notes
- This chatbot only answers based on Intune documentation.
- It will not invent answers or guess things not in the docs.
- If the information isn’t found, it will tell you.
- It automatically updates the vector database when Intune documentation changes.

---

## 🧑‍💻 Contributing

Feel free to fork and submit pull requests!
Issues and ideas are very welcome.


--- 

## 📄 License

This project is licensed under the MIT License.