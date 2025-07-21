# 🛡️ UHT-Framework: UfaqTech Hacking Toolkit  
*A Modern, Multi-OS Cybersecurity Framework for Penetration Testing & Ethical Hacking*

![GitHub stars](https://img.shields.io/github/stars/AwaisNawaz-UfaqTech/UHT-Framework?style=social)
![GitHub forks](https://img.shields.io/github/forks/AwaisNawaz-UfaqTech/UHT-Framework?style=social)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

---

## 📚 Table of Contents
- [✨ Introduction](#-introduction)
- [🚀 Features](#-features)
- [📁 Directory Structure](#-directory-structure)
- [🛠️ Getting Started](#-getting-started)
- [⚙️ Usage](#️-usage)
- [➕ Adding New Tools](#-adding-new-tools)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [📬 Contact & Connect](#-contact--connect)

---

## ✨ Introduction

Welcome to **UHT (Ufaq Hacking Toolkit)** — a cutting-edge, modular, and intuitive CLI framework designed to simplify and accelerate cybersecurity workflows.

Developed by [**Awais Nawaz**](https://www.linkedin.com/in/awais-nawaz-52b643315), UHT consolidates powerful open-source and commercial tools for penetration testing, ethical hacking, and security assessments.

> 🚀 Forget managing dozens of repos. UHT makes setup, updates, and tool management seamless across OS platforms.

---

## 🚀 Features

- 🌐 **Multi-OS Support**: Linux (Debian/Ubuntu, Arch, Termux), macOS, Windows
- 🖥️ **Modern CLI**: Clean, color-coded, intuitive interface
- ⚙️ **Dynamic Tool Management**: All tools defined in `tools.json`
- 📦 **Automated Installer**: Installs all system and Python dependencies
- 🔄 **Update Tools & Framework**: One-click CLI-based updates
- 📁 **Organized Directory Layout**: Tools, logs, wordlists, configs
- 📝 **Logs**: All actions are logged for troubleshooting

---

## 📁 Directory Structure

```
UHT-Framework/
├── uht.py                  # Main CLI launcher
├── install.sh              # OS + env setup script
├── config/
│   ├── tools.json          # Tool metadata
│   └── settings.json       # Global config
├── lib/                    # Core Python modules
│   ├── os_utils.py
│   ├── menu_handler.py
│   ├── tool_manager.py
│   └── update_checker.py
├── tools/                  # Installed tools
├── wordlists/              # Wordlists (seclists, rockyou.txt)
├── logs/                   # Logs for installs/errors
├── README.md               # This file
└── LICENSE                 # MIT License
```

---

## 🛠️ Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/AwaisNawaz-UfaqTech/UHT-Framework.git
cd UHT-Framework
```

### 2. Run the Installer
```bash
bash install.sh
```

This installs:
- Git, Python, pip, and system tools
- Virtual environment (`venv`)
- Python libraries: `termcolor`, `json5`, `requests`

### 3. Activate Virtual Environment
```bash
source venv/bin/activate      # Linux/macOS/Termux
.\venv\Scripts\activate       # Windows CMD
.\venv\Scripts\Activate.ps1   # Windows PowerShell
```

### 4. Launch UHT CLI
```bash
python uht.py
```

---

## ⚙️ Usage

- ✅ **Install Tools** from categories (Recon, Exploit, Web Hacking, etc.)
- 🔄 **Update** installed tools or the full framework
- 🏃‍♂️ **Run Tools** directly via CLI interface
- 🔍 **Browse Tools** with easy-to-navigate menu

---

## ➕ Adding New Tools

Edit `config/tools.json` to add a tool.  
Example entry:
```json
{
  "name": "ToolName",
  "description": "Describe the tool",
  "github_url": "https://github.com/example/tool",
  "install_path": "tools/toolname",
  "run_command": "python3 tool.py",
  "os_compat": ["linux", "termux", "windows", "mac"],
  "dependencies": ["python3", "pip"],
  "post_install_commands": [],
  "skip_if_os_not_supported": true
}
```
Then restart UHT.

---

## 🤝 Contributing

Contributions welcome!

```bash
git checkout -b feature/your-feature
# make your changes
git commit -m "Add XYZ tool"
git push origin feature/your-feature
```

Then open a Pull Request.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 📬 Contact & Connect

[![Portfolio](https://img.shields.io/badge/-Portfolio-0a192f?style=flat&logo=Google-Chrome&logoColor=white)](https://ufaqtech.github.io/awais.github.io/)  
[![GitHub](https://img.shields.io/badge/-GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/AwaisNawaz-UfaqTech)  
[![LinkedIn](https://img.shields.io/badge/-LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/awais-nawaz-52b643315)  
[![Twitter](https://img.shields.io/badge/-Twitter-1DA1F2?style=flat&logo=twitter&logoColor=white)](https://twitter.com/Ufaq_Tech)  
[![Telegram](https://img.shields.io/badge/-Telegram-0088cc?style=flat&logo=telegram&logoColor=white)](https://t.me/UfaqTech)  
[![WhatsApp Channel](https://img.shields.io/badge/-WhatsApp%20Channel-25D366?style=flat&logo=whatsapp&logoColor=white)](https://whatsapp.com/channel/0029VaFZ1eO5zYQLnCOsIQ1F)  
[![Email](https://img.shields.io/badge/-Email-D14836?style=flat&logo=gmail&logoColor=white)](mailto:mawais03415942806@gmail.com)

---

> Made with ❤️ by **Awais Nawaz (UfaqTech)**  
> Empowering Cybersecurity with Simplicity & Speed.
