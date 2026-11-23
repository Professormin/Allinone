#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geek Empire Skill - Index & Catalog Auto Sync Script
Generates/Updates INDEX.md and CATALOG.csv from Markdown knowledge assets.
"""

import argparse
import csv
import glob
import os
import re
import sys

def parse_frontmatter(content):
    """Extract YAML frontmatter fields from markdown content."""
    metadata = {}
    
    # Extract YAML block between ---
    fm_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
    if not fm_match:
        return metadata
        
    fm_text = fm_match.group(1)
    
    # Field regex matchers
    fields = {
        "doc_id": r'doc_id:\s*["\']?(GE-\d{4}-\d{3}|GE-[A-Za-z0-9_-]+)["\']?',
        "title": r'title:\s*["\']?([^"\']+)["\']?',
        "category": r'category:\s*["\']?([^"\']+)["\']?',
        "created_at": r'created_at:\s*["\']?([^"\']+)["\']?',
        "updated_at": r'updated_at:\s*["\']?([^"\']+)["\']?',
        "version": r'version:\s*["\']?([^"\']+)["\']?',
        "status": r'status:\s*["\']?([^"\']+)["\']?',
        "publish_status": r'publish_status:\s*["\']?([^"\']+)["\']?',
    }
    
    for key, pattern in fields.items():
        match = re.search(pattern, fm_text)
        if match:
            metadata[key] = match.group(1).strip()
            
    # Keywords list matcher
    kw_match = re.search(r'keywords:\s*\[(.*?)\]', fm_text)
    if kw_match:
        raw_kw = kw_match.group(1)
        # Clean quotes and strip whitespace
        cleaned = [k.strip().strip('"').strip("'") for k in raw_kw.split(",") if k.strip()]
        metadata["keywords"] = ", ".join(cleaned)
    else:
        metadata["keywords"] = ""
        
    return metadata


def update_catalog_and_index(vault_path):
    vault_path = os.path.abspath(vault_path)
    if not os.path.exists(vault_path):
        print(f"Error: Vault path does not exist: {vault_path}", file=sys.stderr)
        return False

    catalog_path = os.path.join(vault_path, "CATALOG.csv")
    index_path = os.path.join(vault_path, "INDEX.md")

    print(f"Syncing Geek Empire Knowledge Assets at: {vault_path}")

    docs = []
    # Collect all .md files
    md_files = glob.glob(os.path.join(vault_path, "**", "*.md"), recursive=True)

    # Exclude system files and internal skill folders
    ignore_dirs = {"templates", "assets", "examples", "tests", "scripts", ".git", ".workbuddy-ai"}
    ignore_files = {"README.md", "README.zh-CN.md", "INDEX.md", "SKILL.md"}

    seen_paths = set()

    for file_path in md_files:
        rel_path = os.path.relpath(file_path, vault_path).replace("\\", "/")
        parts = rel_path.split("/")

        # Skip ignored directories and root ignored files
        if any(part in ignore_dirs for part in parts[:-1]):
            continue
        if len(parts) == 1 and parts[0] in ignore_files:
            continue
        if rel_path in seen_paths:
            continue
        seen_paths.add(rel_path)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Warning: Could not read file {rel_path}: {e}", file=sys.stderr)
            continue

        meta = parse_frontmatter(content)

        doc_info = {
            "doc_id": meta.get("doc_id", "GE-UNASSIGNED"),
            "title": meta.get("title", os.path.basename(file_path)),
            "category": meta.get("category", parts[0] if len(parts) > 1 else "Uncategorized"),
            "file_path": rel_path,
            "created_at": meta.get("created_at", ""),
            "updated_at": meta.get("updated_at", ""),
            "version": meta.get("version", "v1.0"),
            "status": meta.get("status", "UNVERIFIED"),
            "publish_status": meta.get("publish_status", "INTERNAL"),
            "keywords": meta.get("keywords", "")
        }
        docs.append(doc_info)

    # Deduplicate by doc_id (keep latest or non-UNASSIGNED) and sort
    # Sort key: doc_id ascending, fallback to file_path
    docs.sort(key=lambda x: (x["doc_id"] == "GE-UNASSIGNED", x["doc_id"], x["file_path"]))

    # 1. Write CATALOG.csv (UTF-8 with BOM for Windows Excel compatibility)
    fieldnames = [
        "doc_id", "title", "category", "file_path", 
        "created_at", "updated_at", "version", 
        "status", "publish_status", "keywords"
    ]
    
    try:
        with open(catalog_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(docs)
        print(f"Updated CATALOG.csv -> {catalog_path}")
    except Exception as e:
        print(f"Error writing CATALOG.csv: {e}", file=sys.stderr)
        return False

    # 2. Write INDEX.md
    status_badges = {
        "VERIFIED": "✅ VERIFIED",
        "UNVERIFIED": "⚠️ UNVERIFIED",
        "FAILED": "❌ FAILED",
        "PENDING": "⏳ PENDING",
        "DRAFT": "📝 DRAFT"
    }

    index_content = """# 极客帝国 · 知识资产总索引 | GEEK EMPIRE INDEX

> **品牌理念**：Turn AI conversations into reusable, structured knowledge assets.
> **所属系统**：Geek Empire Knowledge System

---

## 📚 知识资产列表

| 编号 | 标题 | 分类 | 验证状态 | 更新日期 | 文件链接 |
| :--- | :--- | :--- | :---: | :---: | :--- |
"""
    for d in docs:
        badge = status_badges.get(d["status"].upper(), f"❓ {d['status']}")
        index_content += f"| **{d['doc_id']}** | {d['title']} | `{d['category']}` | {badge} | {d['updated_at']} | [查看文档]({d['file_path']}) |\n"

    index_content += f"""
---

## 🛠 索引更新说明

共有 **{len(docs)}** 篇知识文档已列入索引。运行脚本自动更新索引：

```bash
python scripts/update_index.py --vault-path "{vault_path}"
```

---

> **极客帝国 · GEEK EMPIRE**  
> *Turn AI conversations into reusable, structured knowledge assets.*
"""

    try:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_content)
        print(f"Updated INDEX.md -> {index_path}")
    except Exception as e:
        print(f"Error writing INDEX.md: {e}", file=sys.stderr)
        return False

    return True


def main():
    parser = argparse.ArgumentParser(description="Update Geek Empire Knowledge Base Index & Catalog")
    default_vault = os.environ.get("GEEK_EMPIRE_PATH", os.getcwd())
    parser.add_argument("--vault-path", default=default_vault, help="Path to Geek Empire knowledge base directory")
    
    args = parser.parse_args()
    success = update_catalog_and_index(args.vault_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
