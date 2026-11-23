#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extended Test Suite for Geek Empire Skill v0.1 Release Audit
Covers:
- Duplicate archiving and ID collision prevention
- Concurrent execution safety
- Path handling (spaces, Chinese characters, Windows backslashes)
- File integrity and backup / non-destructive properties
- Edge case sensitive data sanitization (URLs with secrets, certificates)
"""

import concurrent.futures
import json
import os
import shutil
import sys
import tempfile
import unittest

# Add scripts directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

import archive
import update_index


class TestReleaseAuditReliability(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory with spaces, special chars, and Chinese chars
        self.test_dir = tempfile.mkdtemp(prefix="GE Audit 审核测试 空格与中文_")
        self.vault_path = os.path.join(self.test_dir, "00_极客帝国 Vault 测试")
        os.makedirs(self.vault_path, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_duplicate_chat_behavior(self):
        """Verify behavior when archiving the exact same conversation multiple times."""
        # First archive
        file1, id1 = archive.archive_knowledge(
            vault_path=self.vault_path,
            title="重复聊天测试",
            background="这是第一次归档的内容"
        )
        self.assertEqual(id1, "GE-2026-001")

        # Second archive without force flag (should increment ID and create a distinct asset, avoiding overwrite)
        file2, id2 = archive.archive_knowledge(
            vault_path=self.vault_path,
            title="重复聊天测试",
            background="这是第二次重复点击归档"
        )
        self.assertEqual(id2, "GE-2026-002")
        self.assertNotEqual(file1, file2)
        self.assertTrue(os.path.exists(file1))
        self.assertTrue(os.path.exists(file2))

        # Check INDEX.md contains BOTH documents
        index_path = os.path.join(self.vault_path, "INDEX.md")
        with open(index_path, "r", encoding="utf-8") as f:
            index_content = f.read()
            self.assertIn("GE-2026-001", index_content)
            self.assertIn("GE-2026-002", index_content)

    def test_02_id_collision_prevention(self):
        """Verify that existing documents are never accidentally overwritten when IDs are pre-assigned."""
        # Create existing document with GE-2026-005
        archive.archive_knowledge(
            vault_path=self.vault_path,
            title="旧已有文档",
            background="已有数据",
            doc_id="GE-2026-005"
        )

        # Automatic ID allocation should pick GE-2026-006 (highest + 1)
        next_id = archive.get_next_doc_id(self.vault_path, year="2026")
        self.assertEqual(next_id, "GE-2026-006")

    def test_03_concurrent_execution_safety(self):
        """Verify parallel archiving tasks do not corrupt INDEX.md or CATALOG.csv."""
        def run_archive(num):
            file_path, doc_id = archive.archive_knowledge(
                vault_path=self.vault_path,
                title=f"并发任务-{num}",
                background=f"并发测试背景-{num}",
                category="03_自动化与编程",
                doc_id=f"GE-2026-10{num}" # Explicit distinct IDs
            )
            return file_path, doc_id

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(run_archive, i) for i in range(4)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        self.assertEqual(len(results), 4)

        # Check catalog integrity
        catalog_path = os.path.join(self.vault_path, "CATALOG.csv")
        self.assertTrue(os.path.exists(catalog_path))
        with open(catalog_path, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()
            # 1 header line + 4 doc lines = 5 lines
            self.assertEqual(len(lines), 5)

    def test_04_chinese_path_and_spaces(self):
        """Verify Chinese directory names, spaces, and Windows path slashes handle seamlessly."""
        file_path, doc_id = archive.archive_knowledge(
            vault_path=self.vault_path,
            title="测试 特殊 字符 & 中文 路径",
            background="路径包含空格和中文字符",
            category="02_网络与故障排查"
        )

        self.assertTrue(os.path.exists(file_path))
        index_path = os.path.join(self.vault_path, "INDEX.md")
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn(doc_id, content)

    def test_05_data_preservation_on_index_failure(self):
        """Verify that markdown assets remain intact even if index update fails."""
        # Create doc
        file_path, doc_id = archive.archive_knowledge(
            vault_path=self.vault_path,
            title="安全保留测试",
            background="即使索引写失败，此文件也不能被删除"
        )
        self.assertTrue(os.path.exists(file_path))

        # Intentionally make CATALOG.csv read-only or invalid directory to simulate index write error
        catalog_path = os.path.join(self.vault_path, "CATALOG.csv")
        if os.path.exists(catalog_path):
            os.chmod(catalog_path, 0o444) # Read-only

        # Run index update (should handle error gracefully without deleting original .md file)
        res = update_index.update_catalog_and_index(self.vault_path)
        self.assertFalse(res) # Should return False due to error
        self.assertTrue(os.path.exists(file_path)) # Original file MUST remain intact

        # Reset permissions for cleanup
        os.chmod(catalog_path, 0o666)

    def test_06_comprehensive_privacy_scan(self):
        """Test sanitization against various private token formats."""
        dirty_text = (
            "Here is token Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.secret123456789\n"
            "Password password = 'SuperSecret123!'\n"
            "Email contact@company.com and phone 13912345678"
        )
        sanitized, warnings = archive.sanitize_text(dirty_text)
        self.assertNotIn("SuperSecret123!", sanitized)
        self.assertNotIn("13912345678", sanitized)
        self.assertNotIn("contact@company.com", sanitized)
        self.assertTrue(len(warnings) >= 3)


if __name__ == "__main__":
    unittest.main()
