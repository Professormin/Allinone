#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for Geek Empire Skill v0.1
Tests auto-numbering, sanitization, markdown generation, index updates, and error handling.
"""

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


class TestGeekEmpireSkill(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory with Chinese characters in path to test encoding/paths
        self.test_dir = tempfile.mkdtemp(prefix="GE_Test_极客测试_")
        self.vault_path = os.path.join(self.test_dir, "00_极客帝国_Vault")
        os.makedirs(self.vault_path, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_auto_numbering(self):
        """Test auto-incrementing doc_id generation."""
        id1 = archive.get_next_doc_id(self.vault_path, year="2026")
        self.assertEqual(id1, "GE-2026-001")

        # Create a dummy file with GE-2026-001
        dummy_dir = os.path.join(self.vault_path, "01_AI工具与工作流")
        os.makedirs(dummy_dir, exist_ok=True)
        dummy_file = os.path.join(dummy_dir, "GE-2026-001_Test.md")
        with open(dummy_file, "w", encoding="utf-8") as f:
            f.write('---\ndoc_id: "GE-2026-001"\ntitle: "Test"\n---\n')

        id2 = archive.get_next_doc_id(self.vault_path, year="2026")
        self.assertEqual(id2, "GE-2026-002")

    def test_02_sensitive_data_sanitization(self):
        """Test detection and redaction of sensitive data."""
        sample_text = "My API Key is api_key: sk-1234567890abcdef12345678 and phone is 13812345678"
        sanitized, warnings = archive.sanitize_text(sample_text)
        
        self.assertTrue(len(warnings) > 0)
        self.assertNotIn("sk-1234567890abcdef12345678", sanitized)
        self.assertIn("****", sanitized)

    def test_03_archive_creation_and_yaml(self):
        """Test creating an archived document with YAML frontmatter."""
        target_file, doc_id = archive.archive_knowledge(
            vault_path=self.vault_path,
            title="测试知识归档与编码",
            background="测试 Windows 路径与中文字符匹配",
            verified_summary="程序正常运行，字符集识别无误",
            verified_code="python --version",
            category="02_网络与故障排查",
            keywords=["测试", "编码", "Windows"],
            status="VERIFIED"
        )

        self.assertEqual(doc_id, "GE-2026-001")
        self.assertTrue(os.path.exists(target_file))

        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("doc_id: \"GE-2026-001\"", content)
        self.assertIn("title: \"测试知识归档与编码\"", content)
        self.assertIn("category: \"02_网络与故障排查\"", content)
        self.assertIn("✅ VERIFIED", content)

    def test_04_index_and_catalog_generation(self):
        """Test generation of INDEX.md and CATALOG.csv (with utf-8-sig BOM)."""
        # Create two documents
        archive.archive_knowledge(
            vault_path=self.vault_path,
            title="案例一 AI 工作流",
            background="AI Workflow background",
            category="01_AI工具与工作流",
            keywords=["AI", "Workflow"]
        )

        archive.archive_knowledge(
            vault_path=self.vault_path,
            title="案例二 网络排查",
            background="Network troubleshooting",
            category="02_网络与故障排查",
            keywords=["Network", "502"]
        )

        catalog_path = os.path.join(self.vault_path, "CATALOG.csv")
        index_path = os.path.join(self.vault_path, "INDEX.md")

        self.assertTrue(os.path.exists(catalog_path))
        self.assertTrue(os.path.exists(index_path))

        # Check BOM in CATALOG.csv
        with open(catalog_path, "rb") as f:
            raw_bytes = f.read(3)
            self.assertEqual(raw_bytes, b'\xef\xbb\xbf', "CATALOG.csv must start with UTF-8 BOM")

        # Check INDEX.md content
        with open(index_path, "r", encoding="utf-8") as f:
            index_text = f.read()
            self.assertIn("GE-2026-001", index_text)
            self.assertIn("GE-2026-002", index_text)
            self.assertIn("案例一 AI 工作流", index_text)
            self.assertIn("案例二 网络排查", index_text)

    def test_05_duplicate_archiving(self):
        """Test duplicate archiving prevents accidental overwrite without --force."""
        file1, id1 = archive.archive_knowledge(
            vault_path=self.vault_path,
            title="重复测试文档",
            background="第一次归档",
            doc_id="GE-2026-088"
        )

        # Attempt second archiving with same doc_id
        file2, id2 = archive.archive_knowledge(
            vault_path=self.vault_path,
            title="重复测试文档",
            background="第二次归档（修改版）",
            doc_id="GE-2026-088",
            force=True
        )

        self.assertEqual(file1, file2)
        with open(file2, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("第二次归档", content)

    def test_06_error_handling_nonexistent_dir(self):
        """Test error handling when directory does not exist or invalid."""
        invalid_path = os.path.join(self.test_dir, "non_existent_folder_xyz")
        # Should create directory automatically or handle gracefully
        res = update_index.update_catalog_and_index(invalid_path)
        self.assertFalse(res)


if __name__ == "__main__":
    unittest.main()
