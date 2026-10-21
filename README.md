# Geek Empire Skill (`geek-empire-skill`)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)](https://www.python.org/)

**Turn AI conversations into reusable, structured knowledge assets.**

`geek-empire-skill` is an open-source Agent Skill that enables developers and creators to transform raw AI chat discussions into clean, standardized Markdown documents with automatic ID tracking, categorization, sensitive data redaction, and searchable indexes.

---

## 💡 What Problem Does It Solve?

In daily AI-assisted development and research, valuable context gets lost in long, messy conversation logs:
- Solutions and verified commands are buried under trial-and-error chatter.
- Failed attempts and root causes are forgotten, causing team members to repeat the same mistakes.
- Copy-pasting chat responses manually creates inconsistent notes scattered across directories.

`geek-empire-skill` bridges the gap between **transient AI chats** and **long-term structured knowledge assets**.

---

## ⚡ Key Features & Differences

| Feature | Standard AI Summary | Geek Empire Skill (`geek-empire-skill`) |
| :--- | :--- | :--- |
| **Output Format** | Plain unstructured text | YAML Frontmatter + Standardized Markdown Template |
| **Verification State** | Mixes facts with hallucinations | Explicitly separates **Verified / Unverified / Failed / Pending** |
| **Indexing** | Manual organizing needed | Auto-generates `INDEX.md` and Windows-friendly `CATALOG.csv` |
| **Data Safety** | Risk of leaking keys / secrets | Automatic regex scan and redaction for API Keys, Passwords & PII |
| **Portability** | Non-standard formats | Universal Python CLI + Agent Skill specification |

---

## ⏱️ 3-Minute Quick Demo (Try It Now!)

Want to see how it works instantly? Run this 1-liner in your terminal after cloning:

```bash
python scripts/archive.py --vault-path ./my_test_vault --title "My First Knowledge Asset" --background "Testing Geek Empire Skill auto-indexing"
```

Check `./my_test_vault`: You will see a newly created Markdown asset, `INDEX.md`, and `CATALOG.csv`!

---

## 🚀 Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher
- Any AI assistant platform supporting Agent Skills / Custom Skills (e.g., WorkBuddy, Claude Code, Cursor, AutoGen, etc.)

### 2. Clone Repository

```bash
git clone https://github.com/<your-username>/geek-empire-skill.git
```

### 3. Configure Knowledge Vault Path

Set the environment variable `GEEK_EMPIRE_PATH` to your custom knowledge directory:

**Linux / macOS:**
```bash
export GEEK_EMPIRE_PATH="/path/to/your/knowledge_vault"
```

**Windows (PowerShell):**
```powershell
$env:GEEK_EMPIRE_PATH = "C:\Users\YourName\Documents\GeekEmpire_Vault"
```

---

## 📖 How to Use

### Trigger in AI Conversation

Simply type in your AI chat:
- **Chinese**: `@极客帝国 归档`
- **English / Universal**: `/archive`

The AI agent will analyze the preceding conversation, extract key information, redact sensitive data, and run the Python script to archive the result.

### Manual CLI Execution

You can also run the archiving script manually via CLI:

```bash
python scripts/archive.py \
  --vault-path "/path/to/vault" \
  --title "Docker Container Memory Leak Troubleshooting SOP" \
  --background "Node.js service crashed due to OOMKilled" \
  --category "03_自动化与编程" \
  --keywords "Docker,Memory,Node.js" \
  --status "VERIFIED"
```

To update indexes manually:

```bash
python scripts/update_index.py --vault-path "/path/to/vault"
```

---

## 🔄 Full Example Flow

```text
[Original AI Conversation Log]
         │
         ▼
[Trigger: /archive or @极客帝国 归档]
         │
         ▼
[Sensitive Data Scan & Redaction]
         │
         ▼
[Structured Markdown File Generated]
   └── Vault/03_自动化与编程/GE-2026-099_Docker_Container_Memory_Leak.md
         │
         ▼
[Auto-updated Indexes]
   ├── INDEX.md (Markdown Overview)
   └── CATALOG.csv (UTF-8 with BOM for Windows Excel)
```

Check out [`examples/sample-archive.md`](examples/sample-archive.md) for a complete sample document.

---

## 🛡️ Data Safety & Privacy

- **Local-First Execution**: All extraction and index generation happen strictly on your local machine.
- **Sensitive Data Redaction**: Automatically scans and masks API Keys, Bearer Tokens, Passwords, and Chinese mobile numbers before saving.
- **Zero Cloud Leakage**: No conversation logs or metadata are sent to external third-party services.

---

## 🧪 Testing

Run the included unit test suite to verify installation and functionality:

```bash
python tests/test_archive.py
```

---

## 🤖 AI Tool Compatibility Matrix

| AI Assistant / Platform | Support Status | Notes |
| :--- | :---: | :--- |
| **WorkBuddy AI** | ✅ Verified | Native support via `@极客帝国 归档` / `/archive` |
| **Claude Code / Anthropic Agent** | ✅ Verified | Supported via skill definition / slash command |
| **Cursor / VS Code AI** | 🟡 Compatible | Invoked via prompt / terminal script integration |
| **ChatGPT / OpenAI Custom GPT** | 🟡 Compatible | Requires Python code execution or custom action |

---

## 🗑️ Uninstallation

Simply delete the repository folder and remove the environment variable `GEEK_EMPIRE_PATH`:

```bash
rm -rf geek-empire-skill
```

---

## 📄 License

Distributed under the [MIT License](LICENSE).

---

> **Geek Empire Skill · GEEK EMPIRE**  
> *Turn AI conversations into reusable, structured knowledge assets.*
