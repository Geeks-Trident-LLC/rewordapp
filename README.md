
# RewordApp

---

## 📖 Overview

A versatile Python utility that transforms text into a readable yet securely obfuscated form. Designed for remote work, contract development, and distributed collaboration, RewordApp helps safeguard sensitive information while preserving structure and usability. It enables safe testing, automation, and workflow sharing across diverse environments without exposing real data.

---

## 💡 Use Cases

- Sharing logs or datasets with contractors  
- Protecting client information in demos  
- Creating safe test fixtures
- Automating obfuscation in CI/CD pipelines
- Preparing reproducible bug reports without leaking data

---

## ✨ Features

- 🔌 **Fully Offline Operation** - RewordApp runs entirely on your machine with **no internet connection required**, ensuring maximum privacy and data protection.

- 🔏 **Readable Obfuscation** - Preserve the shape and intent of text while masking sensitive content.

- ⚙️ **Rule‑Driven Rewriting** - YAML‑based rewrite rules let you define custom transformations.

- 🖥️ **CLI and GUI Modes** - Use the command‑line interface for automation or launch the GUI for interactive workflows.

- 🤝 **Safe for Collaboration** - Designed for contractors, remote developers, QA teams, gig workers, freelancers, tech‑support staff, field‑service teams, and sales professionals—keeping sensitive data protected across every workflow.

---

## ⚙️ Installation

Install from PyPI:

```bash
pip install rewordapp
```

Or install from source:

```bash
git clone git@github.com:Geeks-Trident-LLC/rewordapp.git
cd rewordapp
pip install -e .
```
---

## 📦 Dependencies  

This project depends on the following Python packages to provide core functionality and seamless integration:  

- [**PyYAML**](https://pypi.org/project/PyYAML/) – YAML parser and emitter, enabling structured configuration management.

---

## 🧰 Command‑Line Usage

RewordApp provides a clean, script‑friendly CLI:

```bash
rewordapp [options]
```

### 🔖 Common Flags

| Flag                | Description                              |
|---------------------|------------------------------------------|
| `--gui`             | Launch the graphical interface           |
| `-f, --data-file`   | Path to the input text file              |
| `-r, --rule-file`   | YAML rule file defining rewrite behavior |
| `--show-data`       | Display raw input data                   |
| `--show-rules`      | Display rewrite rules                    |
| `--show-header`     | Display a header above the output        |
| `-o, --output-file` | Save rewritten content to a file         |
| `--save-rule-file`  | Save the active rewrite rules            |
| `--dependency`      | Show dependency information              |
| `-v, --version`     | Show installed version                   |

### Example

```bash
rewordapp \
    --data-file dummy-data.txt \
    --rule-file dummy-rule.yaml \
    --show-data \
    --show-rules \
    --show-header \
    --output-file dummy-output.txt
```

---

## 🖥️ GUI Mode

Prefer a visual workflow? Launch the GUI:

```bash
rewordapp --gui
```

or

```bash
reword-app
```

The GUI provides:

- Live previews
- Rule inspection
- Interactive rewriting  
- Easy file loading and saving

---

## 🛠️ Development

Clone the repository and install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run the test suite:

```bash
pytest
```

---
## 📚 References

- [Wiki](https://github.com/Geeks-Trident-LLC/rewordapp/wiki)  
- [Rewrite Rules](https://github.com/Geeks-Trident-LLC/rewordapp/wiki/Rewrite-Rules)
- [FAQ](https://github.com/Geeks-Trident-LLC/rewordapp/wiki/FAQ)

---

## 🐞 Bugs & Feature Requests  

If you encounter a bug or have a feature request, please submit it through the official [GitHub Issue Tracker](https://github.com/Geeks-Trident-LLC/rewordapp/issues). This helps us track, prioritize, and resolve issues efficiently while keeping all feedback in one place.

---

## 📜 License  

This project is licensed under the **BSD 3‑Clause License**.  
You can review the full license text here:  
- [BSD 3‑Clause License](https://github.com/Geeks-Trident-LLC/rewordapp/blob/develop/LICENSE)  

### 🔍 What the BSD 3‑Clause License Means  
- ✅ **Freedom to Use** – You may use this library in both open‑source and proprietary projects.  
- ✅ **Freedom to Modify** – You can adapt, extend, or customize the code to fit your needs.  
- ✅ **Freedom to Distribute** – Redistribution of source or binary forms is permitted, with or without modification.  
- ⚠️ **Conditions** – You must retain the copyright notice, license text, and disclaimers in redistributions.  
- ❌ **Restrictions** – You cannot use the names of the project or its contributors to endorse or promote derived products without prior permission.  

### ⚡ Why BSD 3‑Clause?  
The BSD 3‑Clause License strikes a balance between openness and protection. It allows broad usage and collaboration while ensuring proper attribution and preventing misuse of contributor names for marketing or endorsement.  

---

## ⚠️ Disclaimer  

This package is currently in **pre‑beta development**. Features, APIs, and dependencies may change before the official 1.x release. While it is functional, please use it with caution in production environments and expect ongoing updates as the project matures.  

--- 
