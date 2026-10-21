---
name: geek-empire-skill
description: Turn AI conversations into reusable, structured knowledge assets. Automatically extracts verified solutions, troubleshooting SOPs, failed attempts, and pending items into standard Geek Empire Markdown documents with automatic indexing.
keywords:
  - "@极客帝国 归档"
  - "@极客帝国"
  - "/archive"
  - "极客帝国"
  - "Geek Empire"
  - "对话归档"
  - "知识沉淀"
---

# Geek Empire Skill - Conversation Knowledge Archiver

This skill turns AI chat interactions into structured, reusable Geek Empire knowledge assets. It analyzes the conversation context, categorizes findings, checks for sensitive data, formats a Markdown document with YAML frontmatter, and updates search indexes (`INDEX.md` and `CATALOG.csv`).

---

## Trigger Keywords

- **Chinese**: `@极客帝国 归档`, `@极客帝国`, `整理并归档`, `把本次排查沉淀为知识库`
- **English / Slash**: `/archive`, `Geek Empire Archive`

---

## Execution Workflow (Agent SOP)

When the user triggers this skill via `@极客帝国 归档` or `/archive`, follow these steps:

### Step 1: Context Extraction & Distillation
Analyze the preceding conversation context and extract the following 7 core elements:
1. **Title**: Concise problem summary (e.g., "WorkBuddy Calling Codex CLI Proxy Recovery & CSV Encoding Fix").
2. **Problem & Background**: What issue occurred, the environment details, error logs, and user pain points.
3. **Verification Status Matrix**:
   - **Verified (已验证)**: Solution steps, configuration, or code proven to work.
   - **Unverified (未验证)**: Hypotheses, unconfirmed assumptions, or unverified workarounds.
   - **Failed (失败尝试)**: Methods attempted that failed, including exact error messages and root cause.
   - **Pending (待决事项)**: Unresolved blockers or follow-up items.
4. **Key Operations & Code**: Executable commands, script snippets, or configuration changes.
5. **Simplified SOP**: Step-by-step instructions to resolve identical problems in under 3 minutes.
6. **Lessons & Value**: Key takeaways and future reusable value.
7. **Category & Keywords**: Select or match one of the 6 standard categories:
   - `01_AI工具与工作流`
   - `02_网络与故障排查`
   - `03_自动化与编程`
   - `04_商业运营与管理`
   - `05_教学课程与案例`
   - `06_品牌发布成品`

### Step 2: Data Safety & Sensitivity Check
Scan all extracted text for sensitive content:
- API Keys / Tokens / Bearer headers
- Passwords & Secrets
- Private SSH / RSA keys
- Personal Identifiable Information (PII) like personal phone numbers or private addresses.
*Rule: Redact or replace sensitive values with placeholders (`****`). Never publish raw private tokens.*

### Step 3: Determine Vault Path
Check the target Geek Empire vault path:
1. Environment Variable `GEEK_EMPIRE_PATH` if set.
2. If in a workspace containing `00_极客帝国_GeekEmpire`, use that directory.
3. Otherwise, use the user's specified folder or `./00_GeekEmpire_Vault`.

### Step 4: Execute Search or Archive Script

- **If user wants to SEARCH knowledge** (e.g. `@极客帝国 搜索...`, `查找之前关于...`, `以前...怎么处理的`):
  Execute `scripts/search.py`:
  ```bash
  python scripts/search.py "<USER_QUERY>" --vault-path "<VAULT_PATH>"
  ```
  Or get JSON context for agent二次筛选:
  ```bash
  python scripts/search.py "<USER_QUERY>" --vault-path "<VAULT_PATH>" --format json
  ```
  *Safety Rule: Inspect the `verification_status` of candidates. Do NOT output unverified hypotheses or failed attempts as facts.*

- **If user wants to ARCHIVE context** (e.g. `@极客帝国 归档`, `/archive`):
  Assemble JSON payload and execute `archive.py`:
  ```bash
  python scripts/archive.py --vault-path "<VAULT_PATH>" --title "<TITLE>" ...
  ```

### Step 5: Verify Output & Inform User
Verify that:
1. The Markdown file was created under `<VAULT_PATH>/<CATEGORY>/GE-YYYY-NNN_<TITLE>.md`.
2. `INDEX.md` and `CATALOG.csv` were successfully refreshed.
3. Provide a clear summary response to the user with the generated file path and document ID.

---

> **Geek Empire Skill · GEEK EMPIRE**  
> *Turn AI conversations into reusable, structured knowledge assets.*
