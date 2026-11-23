#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geek Empire Skill v0.2 - Natural Language Intention & Multi-Topic Splitter
Analyzes conversation text to:
1. Detect natural language intent (Reviewed Capture vs Quick Capture vs Search vs Inbox View).
2. Segment multiple distinct topics in a single conversation context.
3. Clean user expressions into User Intent Layer (preserving all independent requirements).
4. Track requirement revisions and corrections.
"""

import json
import re


# Intent Trigger Indicators
INTENT_PATTERNS = {
    "pinned_insight": [
        "@极客帝国 "
    ],
    "reviewed_archive": [
        "帮我整理", "我看看", "查看后保存", "审核后保存", "整理一下", "预览归档", "这两个事情分开保存",
        "要看一眼", "检查再存", "帮我提取"
    ],
    "quick_archive": [
        "没时间", "先存", "快点存", "快速保存", "放进去吧", "没空看", "先放着", "等会看", "直接存", "快速归档"
    ],
    "search": [
        "之前", "以前", "找找", "怎么处理的", "怎么解决的", "查找", "搜一下", "那个问题", "上次那个"
    ],
    "inbox": [
        "没审核", "未审核", "查看收件箱", "查看inbox", "看下未看", "处理未审"
    ],
    "promote": [
        "正式保存", "这条可以了", "审核通过", "转正式", "可以入库"
    ]
}


def detect_user_action_intent(user_text):
    """
    Detects user intent from natural language without requiring rigid commands or slash prefixes.
    Checks for exact Pinned Insights '@极客帝国 <text>' first.
    """
    text_strip = user_text.strip()
    
    # Priority Check: Pinned Insights '@极客帝国 + 任意非命令文字'
    if text_strip.startswith("@极客帝国"):
        remainder = re.sub(r'^@极客帝国\s*', '', text_strip).strip()
        # If remainder does NOT match explicit commands like "归档", "查找", "搜索", "快速归档"
        explicit_cmds = ["归档", "查找", "搜索", "快速归档", "未审核", "查看收件箱", "整理"]
        if remainder and not any(cmd in remainder for cmd in explicit_cmds):
            return "pinned_insight", remainder

    text_lower = user_text.lower()
    for action, patterns in INTENT_PATTERNS.items():
        if action == "pinned_insight":
            continue
        for p in patterns:
            if p in text_lower:
                return action, p

    return "general_chat", None


def extract_pinned_insight_package(user_text, source_ai="unknown"):
    """
    Extracts Pinned Insight from '@极客帝国 <text>', preserves exact verbatim sentence,
    sets priority: high, review_status: unreviewed, and auto-suggests category.
    """
    remainder = re.sub(r'^@极客帝国\s*', '', user_text.strip()).strip()
    if not remainder:
        return None

    # Auto category suggestion based on content
    category = "01_AI工具与工作流"
    text_lower = remainder.lower()
    if any(k in text_lower for k in ["代理", "502", "vpn", "网络", "故障", "报错"]):
        category = "02_网络与故障排查"
    elif any(k in text_lower for k in ["python", "node", "code", "script", "代码", "编程"]):
        category = "03_自动化与编程"
    elif any(k in text_lower for k in ["商业", "客户", "定价", "成本", "运营"]):
        category = "04_商业运营与管理"
    elif any(k in text_lower for k in ["教学", "教程", "案例", "SOP", "表达"]):
        category = "05_教学课程与案例"

    # Extract keywords automatically from content
    words = re.findall(r'[a-zA-Z0-9_-]+|[\u4e00-\u9fa5]{2,4}', remainder)
    keywords = list(set(words[:5])) if words else ["重点摘录", "PinnedInsight"]

    title = f"Pinned Insight: {remainder[:25]}..." if len(remainder) > 25 else f"Pinned Insight: {remainder}"

    user_intent_cleaned = f"• 用户原句摘录 (来源: {source_ai}): “{remainder}”\n• 归属声明: 用户本人点赞/收藏的重点摘录，非 AI 事实验证结论。"

    return {
        "title": title,
        "category": category,
        "priority": "high",
        "review_status": "unreviewed",
        "verification_status": "unverified",
        "source_ai": source_ai,
        "keywords": keywords,
        "pinned_quote": remainder,
        "background": f"用户重点摘录内容 (原文): {remainder}",
        "user_intent_cleaned": user_intent_cleaned,
        "verified_summary": "无 (此内容为用户重点摘录，未自动认定为已验证事实)",
        "sop_steps": "无 (摘录卡片，后期生成正式卡片时参考)"
    }


def extract_user_intent_layer(conversation_turns):
    """
    Identifies user statements vs AI responses vs external quotes,
    filters filler words / verbal ticks, and extracts the User Intent Layer.
    PRESERVES all independent requirements and explicit corrections!
    """
    cleaned_requirements = []
    corrections = []
    
    # Natural verbal cues indicating requirements and corrections
    req_cues = ["我想", "我希望", "你帮我", "以后都要", "另外还需要", "必须要", "必须", "要求"]
    correction_cues = ["不对", "我的意思是", "我要的是", "算了", "不要那个", "不要", "这个不写", "改成", "纠正", "不是这样"]

    for turn in conversation_turns:
        role = turn.get("role", "user")
        content = turn.get("content", "").strip()

        if role == "user":
            # Clean verbal ticks like "呃", "嗯", "那个"
            cleaned = re.sub(r'^(呃|嗯|那个|就是|我说|对吧|哈)\s*[,，]?\s*', '', content)
            cleaned = re.sub(r'(对吧|是吧|哈)\s*$', '', cleaned)

            # Check for corrections
            if any(cue in cleaned for cue in correction_cues):
                corrections.append(f"• 纠正/修改记录: {cleaned}")
            elif any(cue in cleaned for cue in req_cues) or len(cleaned) > 5:
                cleaned_requirements.append(f"• 用户显式要求: {cleaned}")

    cleaned_intent_text = "\n".join(cleaned_requirements) if cleaned_requirements else "用户通过自然语言表达了相关分析与解决需求。"
    revisions_text = "\n".join(corrections) if corrections else "无显式需求更正历史。"

    return cleaned_intent_text, revisions_text


def split_multi_topics(conversation_context):
    """
    Identifies topic boundaries in conversation and splits into distinct topic segments.
    Returns list of topic blocks for independent handoff package creation.
    """
    # Simple semantic boundary splitter for multi-topic conversations
    topic_keywords = [
        ("网络与代理", ["代理", "502", "vpn", "网络", "超时", "转圈", "port", "17070"]),
        ("数据与表格", ["excel", "csv", "乱码", "pandas", "utf-8", "bom"]),
        ("容器与部署", ["docker", "node", "oom", "137", "cgroups", "内存"]),
        ("通用开发", ["git", "code", "bug", "脚本", "python"])
    ]

    segments = []
    lines = conversation_context.split("\n")
    
    current_topic = "01_AI工具与工作流"
    current_lines = []

    for line in lines:
        matched_cat = None
        for cat_name, kw_list in topic_keywords:
            if any(kw in line.lower() for kw in kw_list):
                matched_cat = cat_name
                break

        if matched_cat and matched_cat != current_topic and current_lines:
            # Segment boundary
            segments.append({
                "topic_name": current_topic,
                "text": "\n".join(current_lines)
            })
            current_lines = [line]
            current_topic = matched_cat
        else:
            current_lines.append(line)

    if current_lines:
        segments.append({
            "topic_name": current_topic,
            "text": "\n".join(current_lines)
        })

    return segments
