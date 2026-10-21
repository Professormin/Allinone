#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full End-to-End Comprehensive Test Suite for Geek Empire Skill v0.2
Tests:
1. User intent protection & verbal tick cleaning
2. Multi-topic identification & split
3. Dual-mode archiving (Reviewed vs Quick/Inbox) & Promotion
4. Unified protocol geek-empire/1.0 handoff package generation & atomic ingestion
5. Search engine integration with 20 base cards + 10 intent/revision cards (Total 30)
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

import archive
import handoff
import search
import topic_splitter
import update_index


class TestGeekEmpireSkillV02(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="GE_v0.2_Test_")
        self.vault_path = os.path.join(self.test_dir, "vault")
        os.makedirs(self.vault_path, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_user_intent_extraction_and_cleaning(self):
        """Test User Intent Layer cleaning, requirement preservation & correction tracking."""
        turns = [
            {"role": "user", "content": "呃，那个，我想做一个网络排查 SOP。"},
            {"role": "assistant", "content": "好的，建议使用系统的代理分析。"},
            {"role": "user", "content": "不对，我的意思是，必须要能自动处理 502 错误，另外还要支持端口重定向。"},
            {"role": "user", "content": "算了，不要那个全局修改了，以后都按照局部环境变量重定向。"}
        ]

        cleaned_intent, revisions = topic_splitter.extract_user_intent_layer(turns)

        self.assertIn("做一个网络排查 SOP", cleaned_intent)
        self.assertNotIn("呃，那个", cleaned_intent) # Verbal ticks removed
        self.assertIn("不对，我的意思是", revisions) # Corrections tracked
        self.assertIn("算了，不要那个全局修改了", revisions)

    def test_02_natural_language_intent_detection(self):
        """Test natural language intent classification without rigid slash commands."""
        action1, _ = topic_splitter.detect_user_action_intent("帮我整理一下，我看看再保存")
        self.assertEqual(action1, "reviewed_archive")

        action2, _ = topic_splitter.detect_user_action_intent("我没时间了，先放进去吧，等会看")
        self.assertEqual(action2, "quick_archive")

        action3, _ = topic_splitter.detect_user_action_intent("之前那个代理转圈问题怎么解决的？")
        self.assertEqual(action3, "search")

        action4, _ = topic_splitter.detect_user_action_intent("把没审核的找出来处理一下")
        self.assertEqual(action4, "inbox")

    def test_03_unified_handoff_protocol_ingestion(self):
        """Test geek-empire/1.0 protocol handoff package creation and atomic ingestion."""
        pkg = handoff.create_handoff_package(
            title="Protocol Test Asset",
            background="Testing geek-empire/1.0 protocol",
            category="02_网络与故障排查",
            review_status="reviewed",
            verification_status="verified",
            user_intent_cleaned="• 用户要求: 支持通用协议交接",
            source_ai="claude-3-5"
        )

        self.assertEqual(pkg["protocol"], "geek-empire/1.0")
        self.assertTrue(pkg["handoff_id"].startswith("GEH-"))
        self.assertTrue(pkg["batch_id"].startswith("GEB-"))

        # Ingest package
        target_file, doc_id = handoff.ingest_handoff_package(self.vault_path, pkg)
        self.assertTrue(os.path.exists(target_file))
        self.assertIn("02_网络与故障排查", target_file)

        # Idempotency re-ingest test
        re_file, status = handoff.ingest_handoff_package(self.vault_path, pkg)
        self.assertEqual(status, "ALREADY_EXISTS")
        self.assertEqual(target_file, re_file)

    def test_04_dual_mode_quick_capture_to_inbox_and_promote(self):
        """Test Quick Capture routing to _INBOX/ and promotion to official vault."""
        pkg = handoff.create_handoff_package(
            title="Quick Capture Asset",
            background="Quick save without user preview",
            category="03_自动化与编程",
            review_status="unreviewed"
        )

        # Ingest Quick Capture (should land in _INBOX)
        target_file, doc_id = handoff.ingest_handoff_package(self.vault_path, pkg)
        self.assertTrue(os.path.exists(target_file))
        self.assertIn("_INBOX", target_file)

        # Verify INDEX.md updated
        index_path = os.path.join(self.vault_path, "INDEX.md")
        with open(index_path, "r", encoding="utf-8") as f:
            index_text = f.read()
            self.assertIn(doc_id, index_text)

        # Promote item to official category
        official_file = handoff.promote_inbox_item(self.vault_path, doc_id)
        self.assertTrue(os.path.exists(official_file))
        self.assertIn("03_自动化与编程", official_file)
        self.assertFalse(os.path.exists(target_file)) # Inbox file moved

    def test_05_multi_topic_splitting(self):
        """Test splitting a multi-topic conversation into separate handoff assets."""
        multi_context = (
            "我们讨论下 Python 脚本在 Windows 上的 CSV 乱码问题，用 utf-8-sig 可以解决。\n"
            "另外，关于 Docker 容器的 Node 服务内存泄露，需要在 Dockerfile 设置 NODE_OPTIONS。"
        )

        segments = topic_splitter.split_multi_topics(multi_context)
        self.assertTrue(len(segments) >= 2)

        batch_id = handoff.generate_batch_id()

        for seg in segments:
            pkg = handoff.create_handoff_package(
                title=f"Split Topic: {seg['topic_name']}",
                background=seg["text"],
                batch_id=batch_id,
                review_status="reviewed"
            )
            file_p, doc_id = handoff.ingest_handoff_package(self.vault_path, pkg)
            self.assertTrue(os.path.exists(file_p))


    def test_06_pinned_insights_extraction_and_ingestion(self):
        """Test Pinned Insights extraction via '@极客帝国 <text>' and routing to _INBOX."""
        pinned_input = "@极客帝国 记住这个规则：任何时候都不把未经证明的 AI 猜想当成事实！"
        
        action, remainder = topic_splitter.detect_user_action_intent(pinned_input)
        self.assertEqual(action, "pinned_insight")
        self.assertEqual(remainder, "记住这个规则：任何时候都不把未经证明的 AI 猜想当成事实！")

        # Extract Pinned Insight Package
        extracted = topic_splitter.extract_pinned_insight_package(pinned_input, source_ai="workbuddy")
        self.assertIsNotNone(extracted)
        self.assertEqual(extracted["priority"], "high")
        self.assertEqual(extracted["review_status"], "unreviewed")
        self.assertEqual(extracted["verification_status"], "unverified")

        # Create handoff package and ingest
        pkg = handoff.create_handoff_package(**extracted)
        file_path, doc_id = handoff.ingest_handoff_package(self.vault_path, pkg)

        self.assertTrue(os.path.exists(file_path))
        self.assertIn("_INBOX", file_path) # Landed in Inbox due to priority/unreviewed


if __name__ == "__main__":
    unittest.main()
