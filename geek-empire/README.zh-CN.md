# Geek Empire Skill (`geek-empire-skill`) 中文说明书

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)](https://www.python.org/)

**把实践经验，沉淀为可复制的能力。**

`geek-empire-skill` 是一个开源的 Agent Skill（智能体技能），旨在帮助开发者和创作者将 AI 对话中的有效知识、排查 SOP、失败尝试与遗留问题，自动整理为标准化的 Markdown 知识资产文档，并自动生成可检索的索引。

---

## 💡 解决了什么问题？

在日常使用 AI 辅助开发与研究时，对话中蕴含的大量高价值经验容易散失：
- 解决问题的关键命令和配置沉没在长篇对话记录中。
- 踩坑经历和失败原因被遗忘，导致团队重复犯错。
- 手动复制粘贴整理不仅耗时，而且文件格式混乱、缺乏统一编号。

`geek-empire-skill` 打通了 **临时 AI 对话** 到 **长期结构化知识资产** 的自动化沉淀链路。

---

## ⚡ 核心功能与区别

| 功能特性 | 普通 AI 对话总结 | 极客帝国技能 (`geek-empire-skill`) |
| :--- | :--- | :--- |
| **文档格式** | 自由无序的纯文本 | 带 YAML 元数据的品牌标准化 Markdown 模板 |
| **验证矩阵** | 易混淆事实与推测 | 明确区分 **Verified (已验证) / Unverified (未验证) / Failed (失败尝试) / Pending (待决事项)** |
| **索引能力** | 需人工手动整理 | 自动同步生成 `INDEX.md` 总索引与 Windows Excel 兼容的 `CATALOG.csv` |
| **数据安全** | 容易误保存密钥私钥 | 内置正则扫描，自动掩码脱敏 API Key、密码与个人隐私 |
| **跨平台复用** | 强绑定特定环境 | 提供标准 Python 脚本与通用 Agent Skill 规范 |

---

## ⏱️ 3分钟快速体验（立即试用！）

无需复杂配置，克隆后在终端运行以下一行命令即可体验完整归档与索引生成：

```bash
python scripts/archive.py --vault-path ./my_test_vault --title "我的第一个知识资产" --background "测试极客帝国归档与索引自动化"
```

检查 `./my_test_vault` 目录：您将直接看到生成的标准化 Markdown 文档、`INDEX.md` 总索引以及 `CATALOG.csv`！

---

## 🚀 快速开始与安装

### 1. 环境要求
- Python 3.8 或更高版本
- 支持 Agent Skill 或自定义技能的 AI 助手平台（如 WorkBuddy、Claude Code、Cursor 等）

### 2. 克隆仓库

```bash
git clone https://github.com/<your-username>/geek-empire-skill.git
```

### 3. 配置知识库保存路径

设置环境变量 `GEEK_EMPIRE_PATH` 指定您的知识库目录：

**Linux / macOS:**
```bash
export GEEK_EMPIRE_PATH="/path/to/your/knowledge_vault"
```

**Windows (PowerShell):**
```powershell
$env:GEEK_EMPIRE_PATH = "C:\Users\YourName\Documents\GeekEmpire_Vault"
```

---

## 📖 使用指南

### 1. 对话中一句话触发

在 AI 对话框中输入：
- **中文**：`@极客帝国 归档` 或 `整理并归档`
- **英文 / 斜杠指令**：`/archive`

AI 智能体会自动分析上文对话，提炼核心结论，检查脱敏，并调用归档脚本写入文档。

### 2. 手动 CLI 命令行执行

也可以通过命令行直接运行归档脚本：

```bash
python scripts/archive.py \
  --vault-path "/path/to/vault" \
  --title "Docker 容器内存泄漏排查 SOP" \
  --background "Node.js 服务频繁触发 OOMKilled 崩溃" \
  --category "03_自动化与编程" \
  --keywords "Docker,内存泄漏,Node.js" \
  --status "VERIFIED"
```

手动更新知识库索引：

```bash
python scripts/update_index.py --vault-path "/path/to/vault"
```

---

## 🔄 完整归档流程示例

```text
[原始 AI 对话记录]
       │
       ▼
[触发指令：/archive 或 @极客帝国 归档]
       │
       ▼
[敏感数据自动扫描与脱敏掩码]
       │
       ▼
[生成结构化 Markdown 文档]
 └── Vault/03_自动化与编程/GE-2026-099_Docker容器内存泄漏排查SOP.md
       │
       ▼
[自动更新索引]
 ├── INDEX.md (Markdown 总览)
 └── CATALOG.csv (带 BOM 编码，Windows Excel 直接双击打开无乱码)
```

查看完整样例文档：[`examples/sample-archive.md`](examples/sample-archive.md)。

---

## 🛡️ 数据安全与隐私保障

- **纯本地运行**：文本提炼与索引生成均在用户本地环境完成。
- **敏感信息脱敏**：保存前自动扫描 API Key、Bearer Token、密码、私钥及手机号并自动遮蔽（如 `sk-12****78`）。
- **零数据上云**：不会将聊天记录发送至任何未授权的第三方外部服务。

---

## 🧪 单元测试

运行项目自带的单元测试套件验证安装与功能：

```bash
python tests/test_archive.py
```

---

## 🤖 AI 工具兼容情况说明

| AI 助手 / 平台 | 兼容状态 | 说明 |
| :--- | :---: | :--- |
| **WorkBuddy AI** | ✅ 完全原生支持 | 通过 `@极客帝国 归档` 或 `/archive` 触发 |
| **Claude Code / Anthropic Agent** | ✅ 完全支持 | 通过加载 `SKILL.md` / 斜杠指令触发 |
| **Cursor / VS Code AI** | 🟡 兼容 | 通过 Prompt 引导或终端调用脚本 |
| **ChatGPT / Custom GPT** | 🟡 兼容 | 需要支持 Python 代码执行环境 |

---

## 🗑️ 卸载方法

直接删除项目文件夹并移除 `GEEK_EMPIRE_PATH` 环境变量即可：

```bash
rm -rf geek-empire-skill
```

---

## 📄 开源许可证

本项目采用 [MIT 许可证](LICENSE) 开源。

---

> **极客帝国 · GEEK EMPIRE**  
> *把实践经验，沉淀为可复制的能力。*
