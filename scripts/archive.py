#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geek Empire Skill - Archive Core Module
Transforms conversations into structured Geek Empire Markdown assets,
detects sensitive information, generates auto-incrementing IDs,
and auto-updates INDEX.md and CATALOG.csv.
"""

import argparse
import datetime
import glob
import json
import os
import re
import sys

# Sensitive Patterns Regex for Data Safety Checks
SENSITIVE_PATTERNS = [
    (r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|bearer\s+[a-zA-Z0-9_\-\.]{20,})\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]{10,})["\']?', "API Key or Secret Token"),
    (r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?([^\s"\']{4,})["\']?', "Password in Plaintext"),
    (r'(?i)-----BEGIN\s+(RSA|EC|DSA|OPENSSH|PRIVATE)\s+KEY-----', "Private Key Material"),
    (r'1[3-9]\d{9}', "Chinese Mobile Phone Number"),
    (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', "Email Address"),
]

DEFAULT_CATEGORIES = {
    "01_AI工具与工作流": ["ai", "prompt", "agent", "llm", "workflow", "gpt", "claude", "workbuddy", "codex", "大模型", "工作流"],
    "02_网络与故障排查": ["network", "proxy", "502", "http", "dns", "vpn", "ip", "bug", "error", "troubleshoot", "代理", "故障", "排查", "网络", "乱码", "bom", "utf-8"],
    "03_自动化与编程": ["python", "node", "script", "bash", "powershell", "api", "code", "bot", "auto", "自动化", "脚本", "编程", "代码"],
    "04_商业运营与管理": ["business", "strategy", "market", "pricing", "cost", "customer", "sales", "商业", "运营", "策略", "定价", "客户"],
    "05_教学课程与案例": ["course", "tutorial", "sop", "case", "study", "guide", "teaching", "教学", "教程", "案例", "指南"],
    "06_品牌发布成品": ["publish", "release", "brand", "product", "announcement", "发布", "成品", "品牌"]
}


def sanitize_text(text):
    """Scan and redact sensitive information from text."""
    redacted = text
    found_types = []
    
    for pattern, desc in SENSITIVE_PATTERNS:
        matches = re.findall(pattern, redacted)
        if matches:
            found_types.append(desc)
            # Redact matches safely
            if isinstance(matches[0], tuple):
                for m in matches:
                    val = m[1] if len(m) > 1 else m[0]
                    if len(val) > 4:
                        redacted = redacted.replace(val, val[:2] + "****" + val[-2:])
            else:
                for val in matches:
                    if len(val) > 4:
                        redacted = redacted.replace(val, val[:2] + "****" + val[-2:])
                        
    return redacted, found_types


def get_next_doc_id(vault_path, year=None):
    """Scan vault to find the highest GE-YYYY-NNN and generate next ID."""
    if not year:
        year = datetime.datetime.now().strftime("%Y")
        
    pattern = os.path.join(vault_path, "**", "*.md")
    max_num = 0
    
    id_regex = re.compile(rf'doc_id:\s*["\']?GE-{year}-(\d{{3}})["\']?')
    
    for filepath in glob.glob(pattern, recursive=True):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read(2000) # Read top 2000 chars
                match = id_regex.search(content)
                if match:
                    num = int(match.group(1))
                    if num > max_num:
                        max_num = num
        except Exception:
            continue
            
    next_num = max_num + 1
    return f"GE-{year}-{next_num:03d}"


def auto_detect_category(title, keywords, content=""):
    """Auto categorize based on keywords and title."""
    text_to_check = f"{title} {' '.join(keywords)} {content[:500]}".lower()
    
    for category, kw_list in DEFAULT_CATEGORIES.items():
        for kw in kw_list:
            if kw.lower() in text_to_check:
                return category
                
    return "01_AI工具与工作流" # Default fallback category


def load_template(skill_root_dir):
    """Load KNOWLEDGE_TEMPLATE.md from assets/."""
    template_path = os.path.join(skill_root_dir, "assets", "KNOWLEDGE_TEMPLATE.md")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
            
    # Fallback inline template if asset not found
    return """---
brand: "极客帝国 | GEEK EMPIRE"
slogan: "Turn AI conversations into reusable, structured knowledge assets."
doc_id: "{{DOC_ID}}"
title: "{{TITLE}}"
created_at: "{{CREATED_AT}}"
updated_at: "{{UPDATED_AT}}"
version: "v1.0"
category: "{{CATEGORY}}"
keywords: [{{KEYWORDS}}]
source: "{{SOURCE}}"
status: "{{STATUS}}"
publish_status: "{{PUBLISH_STATUS}}"
---

# 极客帝国 · 知识资产 | {{TITLE}}

> **品牌理念**：把实践经验，沉淀为可复制的能力。  
> **文档编号**：{{DOC_ID}} | **版本号**：v1.0 | **验证状态**：{{STATUS}}

---

## 一、知识精华 (Knowledge Core)

### 1. 核心问题与背景 (Problem & Background)
{{BACKGROUND}}

### 2. 实践验证与状态矩阵 (Verification Matrix)
| 模块 / 验证项 | 结果状态 | 详细说明 |
| :--- | :---: | :--- |
| **已验证方案 (Verified)** | ✅ VERIFIED | {{VERIFIED_SUMMARY}} |
| **未验证推测 (Unverified)** | ⚠️ UNVERIFIED | {{UNVERIFIED_SUMMARY}} |
| **失败尝试 (Failed)** | ❌ FAILED | {{FAILED_SUMMARY}} |
| **遗留/待决问题 (Pending)** | ⏳ PENDING | {{PENDING_SUMMARY}} |

### 3. 关键操作步骤与代码 (Key Steps & Code)
```bash
{{VERIFIED_CODE}}
```

### 4. 简化 SOP (Simplified SOP)
{{SOP_STEPS}}

---

## 二、用户意图｜忠实清理版 (User Intent Layer)

{{USER_INTENT_CLEANED}}

---

## 三、需求变更与修正历史 (Requirements Revision)

{{REQUIREMENTS_REVISION}}

---

## 四、关键词与模糊搜索提示 (Fuzzy Search Hints)

- **模糊搜索词提示**：{{FUZZY_SEARCH_HINTS}}
- **复用建议与总结**：{{LESSONS_LEARNED}}

---

> **极客帝国 · GEEK EMPIRE**  
> *Turn AI conversations into reusable, structured knowledge assets.*
"""


def archive_knowledge(
    vault_path,
    title,
    background,
    verified_summary="",
    verified_code="",
    unverified_summary="无",
    failed_summary="无",
    failed_details="无",
    failed_root_cause="无",
    pending_summary="无",
    pending_details="无",
    sop_steps="",
    user_intent_cleaned="",
    requirements_revision="",
    fuzzy_search_hints="",
    lessons_learned="",
    category=None,
    keywords=None,
    status="VERIFIED",
    publish_status="INTERNAL",
    source="AI Conversation Archive",
    doc_id=None,
    force=False
):
    """Create archive document and update index."""
    vault_path = os.path.abspath(vault_path)
    if not os.path.exists(vault_path):
        os.makedirs(vault_path, exist_ok=True)

    if keywords is None:
        keywords = []
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",") if k.strip()]

    # Sanitization scan
    raw_combined = f"{title}\n{background}\n{verified_summary}\n{verified_code}\n{failed_details}\n{sop_steps}\n{user_intent_cleaned}\n{requirements_revision}"
    sanitized_combined, warnings = sanitize_text(raw_combined)
    
    if warnings:
        print(f"⚠️ Data Safety Warning: Detected potential sensitive data: {', '.join(warnings)}")

    # Category determination
    if not category:
        category = auto_detect_category(title, keywords, background)

    # Date and Doc ID
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    if not doc_id:
        doc_id = get_next_doc_id(vault_path)

    # Sanitize title for filename
    safe_title = re.sub(r'[\\/*?:"<>|]', '_', title).replace(' ', '_')
    filename = f"{doc_id}_{safe_title}.md"
    
    target_dir = os.path.join(vault_path, category)
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, filename)

    # Check for duplicates by title or existing doc_id
    existing_files = glob.glob(os.path.join(vault_path, "**", f"{doc_id}_*.md"), recursive=True)
    if existing_files and not force:
        print(f"Notice: Archive file for {doc_id} already exists at: {existing_files[0]}")

    # Build content from template
    skill_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    template_str = load_template(skill_root_dir)

    formatted_keywords = ", ".join([f'"{k}"' for k in keywords])

    replacements = {
        "{{DOC_ID}}": doc_id,
        "{{TITLE}}": title,
        "{{CREATED_AT}}": today_str,
        "{{UPDATED_AT}}": today_str,
        "{{CATEGORY}}": category,
        "{{KEYWORDS}}": formatted_keywords,
        "{{SOURCE}}": source,
        "{{STATUS}}": status.upper(),
        "{{PUBLISH_STATUS}}": publish_status.upper(),
        "{{BACKGROUND}}": background,
        "{{VERIFIED_SUMMARY}}": verified_summary or "方案已验证通过。",
        "{{UNVERIFIED_SUMMARY}}": unverified_summary or "无",
        "{{FAILED_SUMMARY}}": failed_summary or "无",
        "{{PENDING_SUMMARY}}": pending_summary or "无",
        "{{VERIFIED_CODE}}": verified_code or "# 代码/命令可正常执行",
        "{{FAILED_DETAILS}}": failed_details or "未发生显著尝试失败。",
        "{{FAILED_ROOT_CAUSE}}": failed_root_cause or "N/A",
        "{{SOP_STEPS}}": sop_steps or "遵照上述代码与验证步骤运行即可。",
        "{{USER_INTENT_CLEANED}}": user_intent_cleaned or "用户表达的需求已忠实清洗记录。",
        "{{REQUIREMENTS_REVISION}}": requirements_revision or "无显式需求变更记录。",
        "{{FUZZY_SEARCH_HINTS}}": fuzzy_search_hints or ", ".join(keywords),
        "{{PENDING_DETAILS}}": pending_details or "无遗留阻塞项。",
        "{{LESSONS_LEARNED}}": lessons_learned or "可直接复用于同类技术场景。"
    }

    doc_content = template_str
    for key, val in replacements.items():
        doc_content = doc_content.replace(key, str(val))

    # Write archive file
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(doc_content)

    print(f"✅ Knowledge Asset Created: {target_file}")

    # Sync INDEX.md and CATALOG.csv
    sys.path.insert(0, os.path.dirname(__file__))
    try:
        import update_index
        update_index.update_catalog_and_index(vault_path)
    except Exception as e:
        print(f"Warning: Index update failed: {e}", file=sys.stderr)

    return target_file, doc_id


def main():
    parser = argparse.ArgumentParser(description="Archive conversation knowledge into Geek Empire Vault")
    parser.add_argument("--vault-path", default=os.environ.get("GEEK_EMPIRE_PATH", os.getcwd()), help="Vault directory path")
    parser.add_argument("--input-json", help="JSON file containing extracted archive fields")
    parser.add_argument("--title", help="Asset title")
    parser.add_argument("--background", help="Problem background")
    parser.add_argument("--category", help="Subdirectory category")
    parser.add_argument("--keywords", help="Comma-separated keywords")
    parser.add_argument("--status", default="VERIFIED", choices=["VERIFIED", "UNVERIFIED", "FAILED", "PENDING", "DRAFT"])
    
    args = parser.parse_args()

    if args.input_json:
        with open(args.input_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            data["vault_path"] = args.vault_path
            archive_knowledge(**data)
    elif args.title and args.background:
        archive_knowledge(
            vault_path=args.vault_path,
            title=args.title,
            background=args.background,
            category=args.category,
            keywords=args.keywords,
            status=args.status
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
