#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geek Empire Skill - Lightweight Hybrid Search Engine Module
Provides fast, zero-dependency natural language search with status Matrix parsing,
relevance scoring, snippet extraction, match reasoning, and agent re-ranking API.
"""

import argparse
import glob
import json
import math
import os
import re
import sys

# Standard 6 categories for Geek Empire
CATEGORIES = [
    "01_AI工具与工作流",
    "02_网络与故障排查",
    "03_自动化与编程",
    "04_商业运营与管理",
    "05_教学课程与案例",
    "06_品牌发布成品"
]

# Common Synonym & Jargon Mapping for Fuzzy Expansion
SYNONYM_MAP = {
    "转圈": ["卡死", "超时", "超时卡死", "502", "挂起", "加载慢", "耗时"],
    "翻墙": ["vpn", "代理", "梯子", "proxy", "节点", "飞鸟"],
    "乱码": ["bom", "utf-8-sig", "gbk", "黑块", "问号", "显示异常", "编码"],
    "内存崩溃": ["oom", "oomkilled", "内存泄漏", "内存溢出", "99%", "卡顿"],
    "表格": ["excel", "csv", "xlsx", "wps", "sheet"],
    "报错": ["error", "exception", "failed", "502", "137", "crash", "故障"],
    "账号": ["token", "key", "auth", "密码", "登录"],
    "代码": ["code", "script", "脚本", "程序", "python", "node"],
}


def tokenize(text):
    """
    Multilingual tokenizer extracting English words, Chinese characters, 
    and bi-grams/tri-grams for CJK text processing without external dependencies.
    """
    if not text:
        return []
    text = text.lower()
    
    # Extract English/number words and CJK single characters
    words = re.findall(r'[a-zA-Z0-9_-]+|[\u4e00-\u9fa5]', text)
    
    tokens = []
    cjk_chars = []
    
    for w in words:
        if re.match(r'[\u4e00-\u9fa5]', w):
            cjk_chars.append(w)
            tokens.append(w)
        else:
            tokens.append(w)
            
    # Generate bi-grams for Chinese words to handle fuzzy compound nouns
    for i in range(len(cjk_chars) - 1):
        tokens.append(cjk_chars[i] + cjk_chars[i+1])
        
    # Generate tri-grams for longer phrasing
    for i in range(len(cjk_chars) - 2):
        tokens.append(cjk_chars[i] + cjk_chars[i+1] + cjk_chars[i+2])

    return tokens


def expand_query_terms(query):
    """Expand query tokens using synonym maps for typo and colloquial resilience."""
    raw_tokens = tokenize(query)
    expanded = set(raw_tokens)
    
    query_lower = query.lower()
    for key, syns in SYNONYM_MAP.items():
        if key in query_lower or any(s in query_lower for s in syns):
            expanded.add(key)
            for s in syns:
                expanded.add(s)
                
    return list(expanded)


def parse_markdown_asset(filepath):
    """
    Reads Markdown file and extracts YAML metadata, verification matrix,
    review status, and content sections.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return None

    # Parse YAML Frontmatter
    fm_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
    fm_text = fm_match.group(1) if fm_match else ""

    doc_id_match = re.search(r'doc_id:\s*["\']?(GE-[A-Za-z0-9_-]+)["\']?', fm_text)
    title_match = re.search(r'title:\s*["\']?([^"\']+)["\']?', fm_text)
    status_match = re.search(r'status:\s*["\']?([^"\']+)["\']?', fm_text)
    pub_match = re.search(r'publish_status:\s*["\']?([^"\']+)["\']?', fm_text)
    cat_match = re.search(r'category:\s*["\']?([^"\']+)["\']?', fm_text)
    kw_match = re.search(r'keywords:\s*\[(.*?)\]', fm_text)

    keywords = []
    if kw_match:
        keywords = [k.strip().strip('"').strip("'") for k in kw_match.group(1).split(",") if k.strip()]

    # Extract Verification Status Matrix
    verification_status = status_match.group(1).upper() if status_match else "UNVERIFIED"
    review_status = pub_match.group(1).upper() if pub_match else "INTERNAL"

    # Extract specific status matrix rows from markdown table if present
    matrix = {
        "verified": [],
        "unverified": [],
        "failed": [],
        "pending": []
    }

    matrix_rows = re.findall(r'\|.*?(✅|⚠️|❌|⏳).*?\|', content)
    for line in content.split("\n"):
        if "|" in line and ("VERIFIED" in line or "✅" in line):
            matrix["verified"].append(line.strip())
        elif "|" in line and ("UNVERIFIED" in line or "⚠️" in line):
            matrix["unverified"].append(line.strip())
        elif "|" in line and ("FAILED" in line or "❌" in line):
            matrix["failed"].append(line.strip())
        elif "|" in line and ("PENDING" in line or "⏳" in line):
            matrix["pending"].append(line.strip())

    return {
        "filepath": os.path.abspath(filepath),
        "doc_id": doc_id_match.group(1) if doc_id_match else "GE-UNASSIGNED",
        "title": title_match.group(1) if title_match else os.path.basename(filepath),
        "category": cat_match.group(1) if cat_match else "01_AI工具与工作流",
        "verification_status": verification_status,
        "review_status": review_status,
        "keywords": keywords,
        "content": content,
        "matrix": matrix,
        "title_tokens": tokenize(title_match.group(1) if title_match else ""),
        "keyword_tokens": tokenize(" ".join(keywords)),
        "body_tokens": tokenize(content)
    }


class KnowledgeSearchEngine:
    def __init__(self, vault_path):
        self.vault_path = os.path.abspath(vault_path)
        self.docs = []
        self.reload()

    def reload(self):
        """Scans vault and loads all valid Markdown knowledge assets."""
        self.docs = []
        if not os.path.exists(self.vault_path):
            return

        ignore_files = {"README.md", "README.zh-CN.md", "INDEX.md", "SKILL.md"}
        ignore_dirs = {"templates", "assets", "examples", "tests", "scripts", ".git", ".workbuddy-ai"}

        for root, dirs, files in os.walk(self.vault_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                if file.endswith(".md") and file not in ignore_files:
                    full_p = os.path.join(root, file)
                    asset = parse_markdown_asset(full_p)
                    if asset:
                        self.docs.append(asset)

    def search(self, query, top_k=3, filter_category=None):
        """
        Executes weighted relevance search against document title, keywords, and body.
        Applies BM25-style frequency scoring with section weights.
        """
        if not query or not self.docs:
            return []

        expanded_tokens = expand_query_terms(query)
        raw_query_tokens = set(tokenize(query))

        results = []

        for doc in self.docs:
            if filter_category and doc["category"] != filter_category:
                continue

            score = 0.0
            matched_terms = set()
            reason_parts = []

            # 1. Title match (Weight: 5.0)
            title_hits = [t for t in expanded_tokens if t in doc["title_tokens"]]
            if title_hits:
                unique_title = list(set(title_hits))
                score += len(unique_title) * 5.0
                matched_terms.update(unique_title)
                reason_parts.append(f"标题匹配 ({', '.join(unique_title[:3])})")

            # 2. Keywords match (Weight: 4.0)
            kw_hits = [t for t in expanded_tokens if t in doc["keyword_tokens"]]
            if kw_hits:
                unique_kw = list(set(kw_hits))
                score += len(unique_kw) * 4.0
                matched_terms.update(unique_kw)
                reason_parts.append(f"关键词匹配 ({', '.join(unique_kw[:3])})")

            # 3. Body text match (Weight: 1.0 with diminishing return)
            body_hits = [t for t in expanded_tokens if t in doc["body_tokens"]]
            if body_hits:
                unique_body = set(body_hits)
                matched_terms.update(unique_body)
                tf_score = sum(1.0 + math.log(doc["body_tokens"].count(t)) for t in unique_body)
                score += tf_score * 1.2
                reason_parts.append(f"正文匹配 {len(unique_body)} 个特征词")

            # 4. Exact raw phrase match bonus
            clean_q = re.sub(r'[^\w\u4e00-\u9fa5]', '', query.lower())
            clean_body = re.sub(r'[^\w\u4e00-\u9fa5]', '', doc["content"].lower())
            if len(clean_q) > 2 and clean_q in clean_body:
                score += 8.0
                reason_parts.append("包含连续短语匹配")

            if score > 0:
                snippet = self._extract_relevant_snippet(doc["content"], raw_query_tokens or expanded_tokens)
                
                # Check for warnings in solution status
                status_warning = None
                if doc["verification_status"] != "VERIFIED":
                    status_warning = f"⚠️ 该方案验证状态为 [{doc['verification_status']}]，请勿直接作为事实命令参考。"

                results.append({
                    "doc_id": doc["doc_id"],
                    "title": doc["title"],
                    "category": doc["category"],
                    "verification_status": doc["verification_status"],
                    "review_status": doc["review_status"],
                    "filepath": doc["filepath"],
                    "rel_path": os.path.relpath(doc["filepath"], self.vault_path).replace("\\", "/"),
                    "relevance_score": round(score, 2),
                    "matched_terms": list(matched_terms),
                    "match_reason": " + ".join(reason_parts) if reason_parts else "相关文本匹配",
                    "snippet": snippet,
                    "status_warning": status_warning,
                    "matrix_summary": doc["matrix"]
                })

        # Sort descending by relevance score
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:top_k]

    def search_for_agent(self, query, top_k=5):
        """
        Agent Secondary Re-ranking & Context Ingestion Interface.
        Returns full structured details for LLM Agent prompt evaluation.
        """
        candidates = self.search(query, top_k=top_k)
        
        agent_context = {
            "query": query,
            "total_candidates": len(candidates),
            "candidates": candidates,
            "instructions_for_agent": (
                "1. Check candidate verification_status: Do NOT present 'FAILED' or 'UNVERIFIED' attempts as facts.\n"
                "2. Check matrix_summary: Distinguish what succeeded (Verified) vs what remained unresolved (Pending).\n"
                "3. Provide the user with exact file paths and short actionable SOPs."
            )
        }
        return agent_context

    def _extract_relevant_snippet(self, content, tokens, max_len=250):
        """Extracts the paragraph containing highest density of matching query tokens."""
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip() and not p.startswith("---")]
        if not paragraphs:
            return content[:max_len] + "..."

        best_p = paragraphs[0]
        max_score = -1

        for p in paragraphs:
            p_tokens = tokenize(p)
            score = sum(1 for t in tokens if t in p_tokens)
            if score > max_score:
                max_score = score
                best_p = p

        clean_snippet = re.sub(r'[\r\n]+', ' ', best_p)
        if len(clean_snippet) > max_len:
            return clean_snippet[:max_len] + "..."
        return clean_snippet


def main():
    parser = argparse.ArgumentParser(description="Search Geek Empire Knowledge Assets")
    parser.add_argument("query", nargs="+", help="Natural language search query")
    parser.add_argument("--vault-path", default=os.environ.get("GEEK_EMPIRE_PATH", os.getcwd()), help="Path to knowledge vault")
    parser.add_argument("--top-k", type=int, default=3, help="Max results to return")
    parser.add_argument("--format", choices=["cli", "json"], default="cli", help="Output format")

    args = parser.parse_args()
    query_str = " ".join(args.query)

    engine = KnowledgeSearchEngine(args.vault_path)

    if args.format == "json":
        data = engine.search_for_agent(query_str, top_k=args.top_k)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        results = engine.search(query_str, top_k=args.top_k)
        if not results:
            print(f"❌ 未找到与 '{query_str}' 相关的极客帝国知识资产。")
            sys.exit(0)

        print(f"\n🔍 极客帝国知识检索结果 (查询: '{query_str}')\n" + "="*60)
        for i, r in enumerate(results, 1):
            print(f"\n[{i}] [{r['doc_id']}] {r['title']}")
            print(f"    📂 分类: {r['category']} | 标定状态: {r['verification_status']} | 审核: {r['review_status']}")
            print(f"    🎯 匹配理由: {r['match_reason']}")
            print(f"    🔗 文档路径: {r['rel_path']}")
            if r['status_warning']:
                print(f"    {r['status_warning']}")
            print(f"    📝 相关片段: {r['snippet']}")
        print("\n" + "="*60)


if __name__ == "__main__":
    main()
