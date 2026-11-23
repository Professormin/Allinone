#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Benchmark & Precision Test Suite for Geek Empire Hybrid Search Engine
Tests 20 distinct simulated knowledge assets against 20 realistic fuzzy user queries,
measuring Top-1 and Top-3 accuracy rates, disambiguation, and status matrix parsing.
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

# Import search engine module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
from search import KnowledgeSearchEngine

# 20 Distinct Knowledge Asset Test Cards
SIMULATED_CARDS = [
    {
        "doc_id": "GE-2026-001",
        "category": "02_网络与故障排查",
        "title": "Windows 飞鸟 VPN 与 WorkBuddy Codex CLI 代理冲突及恢复 SOP",
        "keywords": ["飞鸟VPN", "Codex CLI", "HTTP 502", "代理配置", "WorkBuddy", "转圈超时"],
        "status": "VERIFIED",
        "publish_status": "INTERNAL",
        "content": """---
doc_id: "GE-2026-001"
title: "Windows 飞鸟 VPN 与 WorkBuddy Codex CLI 代理冲突及恢复 SOP"
status: "VERIFIED"
category: "02_网络与故障排查"
publish_status: "INTERNAL"
keywords: ["飞鸟VPN", "Codex CLI", "HTTP 502", "代理配置", "WorkBuddy", "转圈超时"]
---
# Windows 飞鸟 VPN 与 WorkBuddy Codex CLI 代理冲突及恢复 SOP

## 现象描述
用户在 Windows 上打开飞鸟 VPN 翻墙时，WorkBuddy 软件一直转圈超时，报 HTTP CONNECT failed 502 错误。

## 验证状态
| 验证项 | 状态 | 说明 |
| :--- | :---: | :--- |
| **飞鸟 VPN 端口重定向** | ✅ VERIFIED | 设置 $env:HTTP_PROXY = "http://127.0.0.1:17070" 后网络恢复。 |
| **Codex CLI 真正解决** | ⏳ PENDING | Codex CLI 依然因为终端 TTY 交互限制存在偶发超时，尚未彻底解决。 |
| **修改全局注册表** | ❌ FAILED | 修改系统的 ProxyServer 导致全网断网。 |
"""
    },
    {
        "doc_id": "GE-2026-002",
        "category": "01_AI工具与工作流",
        "title": "Python pandas 导出 CSV 在 Windows Excel 双击乱码排查",
        "keywords": ["pandas", "CSV乱码", "utf-8-sig", "BOM", "Excel乱码"],
        "status": "VERIFIED",
        "publish_status": "INTERNAL",
        "content": """---
doc_id: "GE-2026-002"
title: "Python pandas 导出 CSV 在 Windows Excel 双击乱码排查"
status: "VERIFIED"
category: "01_AI工具与工作流"
publish_status: "INTERNAL"
keywords: ["pandas", "CSV乱码", "utf-8-sig", "BOM", "Excel乱码"]
---
# Python pandas 导出 CSV 在 Windows Excel 双击乱码排查

## 现象与解决
在 Windows 下用 pandas to_csv 生成表格，双击打开全是问号和黑块乱码。
使用 utf-8-sig 编码替代普通的 utf-8 写入 BOM 头即可正常显示。
"""
    },
    {
        "doc_id": "GE-2026-003",
        "category": "03_自动化与编程",
        "title": "Docker 容器 Node.js 服务内存泄漏 OOMKilled 137 崩溃排查",
        "keywords": ["Docker", "Memory Leak", "Node.js", "OOMKilled", "cgroups", "137"],
        "status": "VERIFIED",
        "publish_status": "INTERNAL",
        "content": """---
doc_id: "GE-2026-003"
title: "Docker 容器 Node.js 服务内存泄漏 OOMKilled 137 崩溃排查"
status: "VERIFIED"
category: "03_自动化与编程"
publish_status: "INTERNAL"
keywords: ["Docker", "Memory Leak", "Node.js", "OOMKilled", "cgroups", "137"]
---
# Docker 容器 Node.js 服务内存泄漏 OOMKilled 137 崩溃排查

## 现象与解决
Node 服务运行 6 小时后无故卡死崩溃，退出码 137。
在 Dockerfile 中设置 NODE_OPTIONS="--max-old-space-size=1536"，限制 V8 堆内存上限解决。
"""
    },
    {
        "doc_id": "GE-2026-004",
        "category": "02_网络与故障排查",
        "title": "Nginx 反向代理 WebSocket 报 1006 异常断开连接修复",
        "keywords": ["Nginx", "WebSocket", "1006", "Upgrade", "Connection", "timeout"],
        "status": "VERIFIED",
        "publish_status": "INTERNAL",
        "content": """---
doc_id: "GE-2026-004"
title: "Nginx 反向代理 WebSocket 报 1006 异常断开连接修复"
status: "VERIFIED"
category: "02_网络与故障排查"
publish_status: "INTERNAL"
keywords: ["Nginx", "WebSocket", "1006", "Upgrade", "Connection", "timeout"]
---
# Nginx 反向代理 WebSocket 报 1006 异常断开连接修复

## 现象与配置
前端长连接每隔 60 秒自动断开并抛出 Code 1006。
在 Nginx location 增加 proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "Upgrade"; 以及调整 proxy_read_timeout 3600s。
"""
    },
    {
        "doc_id": "GE-2026-005",
        "category": "03_自动化与编程",
        "title": "Git 重置本地修改误删文件通过 git reflog 紧急恢复",
        "keywords": ["Git", "git reset", "git reflog", "代码找回", "误删文件", "恢复"],
        "status": "VERIFIED",
        "publish_status": "INTERNAL",
        "content": """---
doc_id: "GE-2026-005"
title: "Git 重置本地修改误删文件通过 git reflog 紧急恢复"
status: "VERIFIED"
category: "03_自动化与编程"
publish_status: "INTERNAL"
keywords: ["Git", "git reset", "git reflog", "代码找回", "误删文件", "恢复"]
---
# Git 重置本地修改误删文件通过 git reflog 紧急恢复

## 解决步骤
执行 git reset --hard 后未提交的代码消失。
通过 git reflog 查找之前的 commit hash，运行 git checkout -b recovery_branch <hash> 救回代码。
"""
    },
    {
        "doc_id": "GE-2026-006",
        "category": "01_AI工具与工作流",
        "title": "Claude Artifacts 生成前端 React 组件跨域 CORS 拦截调试",
        "keywords": ["Claude", "Artifacts", "CORS", "React", "跨域", "Fetch"],
        "status": "UNVERIFIED",
        "publish_status": "INTERNAL",
        "content": """---
doc_id: "GE-2026-006"
title: "Claude Artifacts 生成前端 React 组件跨域 CORS 拦截调试"
status: "UNVERIFIED"
category: "01_AI工具与工作流"
publish_status: "INTERNAL"
keywords: ["Claude", "Artifacts", "CORS", "React", "跨域", "Fetch"]
---
# Claude Artifacts 生成前端 React 组件跨域 CORS 拦截调试

## 现象
嵌入网页中的 Claude 组件调用本地 API 报 Blocked by CORS policy。
需要在后端服务响应头补全 Access-Control-Allow-Origin: *。
"""
    },
    {
        "doc_id": "GE-2026-007",
        "category": "04_商业运营与管理",
        "title": "美国芍药苗圃进口海关植物检疫证书与 CITES 资质申请指南",
        "keywords": ["芍药", "苗圃", "海关", "检疫证书", "CITES", "进口合规"],
        "status": "VERIFIED",
        "publish_status": "READY_TO_PUBLISH",
        "content": """---
doc_id: "GE-2026-007"
title: "美国芍药苗圃进口海关植物检疫证书与 CITES 资质申请指南"
status: "VERIFIED"
category: "04_商业运营与管理"
publish_status: "READY_TO_PUBLISH"
keywords: ["芍药", "苗圃", "海关", "检疫证书", "CITES", "进口合规"]
---
# 美国芍药苗圃进口海关植物检疫证书资质指南

海外裸根芍药/牡丹进出口必须附带 USDA 签署的 Phytosanitary Certificate 及相关检验合格编号。
"""
    },
    {
        "doc_id": "GE-2026-008",
        "category": "03_自动化与编程",
        "title": "Python Playwright 爬虫无头模式被 Cloudflare 5秒盾拦截 bypass",
        "keywords": ["Playwright", "Cloudflare", "5秒盾", "反爬", "stealth", "headless"],
        "status": "VERIFIED",
        "publish_status": "INTERNAL",
        "content": """---
doc_id: "GE-2026-008"
title: "Python Playwright 爬虫无头模式被 Cloudflare 5秒盾拦截 bypass"
status: "VERIFIED"
category: "03_自动化与编程"
publish_status: "INTERNAL"
keywords: ["Playwright", "Cloudflare", "5秒盾", "反爬", "stealth", "headless"]
---
# Python Playwright 爬虫无头模式被 Cloudflare 5秒盾拦截 bypass

使用 playwright-stealth 扩展及配置 user-agent 绕过 Cloudflare 机器人安全检测。
"""
    },
    {
        "doc_id": "GE-2026-009",
        "category": "02_网络与故障排查",
        "title": "Linux SSH 登录耗时长卡顿 DNS 域名反向解析 timeout 优化",
        "keywords": ["SSH", "Linux", "UseDNS", "登录慢", "卡顿", "timeout"],
        "status": "VERIFIED",
        "publish_status": "INTERNAL",
        "content": """---
doc_id: "GE-2026-009"
title: "Linux SSH 登录耗时长卡顿 DNS 域名反向解析 timeout 优化"
status: "VERIFIED"
category: "02_网络与故障排查"
publish_status: "INTERNAL"
keywords: ["SSH", "Linux", "UseDNS", "登录慢", "卡顿", "timeout"]
---
# Linux SSH 登录耗时长卡顿 DNS 域名反向解析 timeout 优化

SSH 远程连接输入密码后卡顿 10 秒以上。
修改 /etc/ssh/sshd_config 设置 UseDNS no 和 GSSAPIAuthentication no 解决。
"""
    },
    {
        "doc_id": "GE-2026-010",
        "category": "01_AI工具与工作流",
        "title": "WorkBuddy AI 自定义 MCP 服务器配置与端口占用释放",
        "keywords": ["WorkBuddy", "MCP", "端口占用", "netstat", "taskkill"],
        "status": "VERIFIED",
        "publish_status": "INTERNAL",
        "content": """---
doc_id: "GE-2026-010"
title: "WorkBuddy AI 自定义 MCP 服务器配置与端口占用释放"
status: "VERIFIED"
category: "01_AI工具与工作流"
publish_status: "INTERNAL"
keywords: ["WorkBuddy", "MCP", "端口占用", "netstat", "taskkill"]
---
# WorkBuddy AI 自定义 MCP 服务器配置与端口占用释放

MCP 插件无法建立连接，显示 address already in use。
在 Windows 命令提示符中使用 netstat -ano | findstr <port> 找到 PID 后用 taskkill /F /PID 清理。
"""
    },
    {
        "doc_id": "GE-2026-011",
        "category": "05_教学课程与案例",
        "title": "Python 自动化脚本排期 Windows 计划任务 Task Scheduler 设置",
        "keywords": ["Windows", "计划任务", "Task Scheduler", "定时任务", "Python"],
        "status": "VERIFIED",
        "publish_status": "INTERNAL",
        "content": """---
doc_id: "GE-2026-011"
title: "Python 自动化脚本排期 Windows 计划任务 Task Scheduler 设置"
status: "VERIFIED"
category: "05_教学课程与案例"
publish_status: "INTERNAL"
keywords: ["Windows", "计划任务", "Task Scheduler", "定时任务", "Python"]
---
# Python 自动化脚本排期 Windows 计划任务设置 SOP

在 Windows 任务计划程序中配置触发器与操作，指定正确的起始于 (起始路径) 目录以防止相对路径报错。
"""
    },
    {
        "doc_id": "GE-2026-012",
        "category": "03_自动化与编程",
        "title": "PostgreSQL 数据库并发死锁 Deadlock Detected 锁冲突排查",
        "keywords": ["PostgreSQL", "Deadlock", "死锁", "lock", "pg_stat_activity"],
        "status": "VERIFIED",
        "publish_status": "INTERNAL",
        "content": """---
doc_id: "GE-2026-012"
title: "PostgreSQL 数据库并发死锁 Deadlock Detected 锁冲突排查"
status: "VERIFIED"
category: "03_自动化与编程"
publish_status: "INTERNAL"
keywords: ["PostgreSQL", "Deadlock", "死锁", "lock", "pg_stat_activity"]
---
# PostgreSQL 数据库并发死锁 Deadlock Detected 锁冲突排查

查询 pg_stat_activity 视图杀死长期持锁不释放的 backend PID。
"""
    },
    {
        "doc_id": "GE-2026-013",
        "category": "04_商业运营与管理",
        "title": "Stripe 海外跨境支付信用卡拒付 Chargeback 申诉 SOP",
        "keywords": ["Stripe", "Chargeback", "拒付", "风控", "信用卡", "申诉"],
        "status": "VERIFIED",
        "publish_status": "INTERNAL",
        "content": """---
doc_id: "GE-2026-013"
title: "Stripe 海外跨境支付信用卡拒付 Chargeback 申诉 SOP"
status: "VERIFIED"
category: "04_商业运营与管理"
publish_status: "INTERNAL"
keywords: ["Stripe", "Chargeback", "拒付", "风控", "信用卡", "申诉"]
---
# Stripe 海外跨境支付信用卡拒付 Chargeback 申诉 SOP

整理物流追踪单号、签收凭证与客户沟通邮件提交给 Stripe Dispute Center。
"""
    },
    {
        "doc_id": "GE-2026-014",
        "category": "02_网络与故障排查",
        "title": "HTTPS 证书过期 certbot Let's Encrypt 自动续期失败修复",
        "keywords": ["HTTPS", "certbot", "SSL", "Let's Encrypt", "证书过期"],
        "status": "VERIFIED",
        "publish_status": "INTERNAL",
        "content": """---
doc_id: "GE-2026-014"
title: "HTTPS 证书过期 certbot Let's Encrypt 自动续期失败修复"
status: "VERIFIED"
category: "02_网络与故障排查"
publish_status: "INTERNAL"
keywords: ["HTTPS", "certbot", "SSL", "Let's Encrypt", "证书过期"]
---
# HTTPS 证书过期 certbot Let's Encrypt 自动续期失败修复

使用 certbot renew --dry-run 排查 80 端口验证冲突问题。
"""
    },
    {
        "doc_id": "GE-2026-015",
        "category": "01_AI工具与工作流",
        "title": "Cursor AI 编辑器规则文件 .cursorrules 配置指南",
        "keywords": ["Cursor", ".cursorrules", "Prompt", "AI规则", "编辑器"],
        "status": "VERIFIED",
        "publish_status": "INTERNAL",
        "content": """---
doc_id: "GE-2026-015"
title: "Cursor AI 编辑器规则文件 .cursorrules 配置指南"
status: "VERIFIED"
category: "01_AI工具与工作流"
publish_status: "INTERNAL"
keywords: ["Cursor", ".cursorrules", "Prompt", "AI规则", "编辑器"]
---
# Cursor AI 编辑器规则文件 .cursorrules 配置指南

在根目录配置 .cursorrules 限制模型生成代码时的代码规范与框架依赖。
"""
    },
    {
        "doc_id": "GE-2026-016",
        "category": "03_自动化与编程",
        "title": "Node.js npm install 依赖下载超时报错 ETIMEDOUT 国内镜像源切换",
        "keywords": ["npm", "Node.js", "ETIMEDOUT", "镜像源", "淘宝源", "npmmirror"],
        "status": "VERIFIED",
        "publish_status": "INTERNAL",
        "content": """---
doc_id: "GE-2026-016"
title: "Node.js npm install 依赖下载超时报错 ETIMEDOUT 国内镜像源切换"
status: "VERIFIED"
category: "03_自动化与编程"
publish_status: "INTERNAL"
keywords: ["npm", "Node.js", "ETIMEDOUT", "镜像源", "淘宝源", "npmmirror"]
---
# Node.js npm install 依赖下载超时报错 ETIMEDOUT 国内镜像源切换

运行 npm config set registry https://registry.npmmirror.com 解决连接官方源超时问题。
"""
    },
    {
        "doc_id": "GE-2026-017",
        "category": "02_网络与故障排查",
        "title": "Windows 系统防火墙拦截端口导致局域网无法访问 HTTP 服务",
        "keywords": ["Windows防火墙", "端口开放", "局域网", "8080", "入站规则"],
        "status": "VERIFIED",
        "publish_status": "INTERNAL",
        "content": """---
doc_id: "GE-2026-017"
title: "Windows 系统防火墙拦截端口导致局域网无法访问 HTTP 服务"
status: "VERIFIED"
category: "02_网络与故障排查"
publish_status: "INTERNAL"
keywords: ["Windows防火墙", "端口开放", "局域网", "8080", "入站规则"]
---
# Windows 系统防火墙拦截端口导致局域网无法访问 HTTP 服务

高级安全 Windows 防火墙中创建入站规则，放行 TCP 端口（如 8080）。
"""
    },
    {
        "doc_id": "GE-2026-018",
        "category": "05_教学课程与案例",
        "title": "Markdown 文档语法指南与 Obsidian 双向链接实践案例",
        "keywords": ["Markdown", "Obsidian", "双向链接", "笔记", "知识库"],
        "status": "VERIFIED",
        "publish_status": "INTERNAL",
        "content": """---
doc_id: "GE-2026-018"
title: "Markdown 文档语法指南与 Obsidian 双向链接实践案例"
status: "VERIFIED"
category: "05_教学课程与案例"
publish_status: "INTERNAL"
keywords: ["Markdown", "Obsidian", "双向链接", "笔记", "知识库"]
---
# Markdown 文档语法指南与 Obsidian 双向链接实践案例

演示如何在 Obsidian 中通过 [[文稿名称]] 建立网状知识索引。
"""
    },
    {
        "doc_id": "GE-2026-019",
        "category": "04_商业运营与管理",
        "title": "Shopify 独立站域名 DNS 解析与 Cloudflare CDN 托管指南",
        "keywords": ["Shopify", "DNS", "Cloudflare", "CDN", "域名解析"],
        "status": "VERIFIED",
        "publish_status": "INTERNAL",
        "content": """---
doc_id: "GE-2026-019"
title: "Shopify 独立站域名 DNS 解析与 Cloudflare CDN 托管指南"
status: "VERIFIED"
category: "04_商业运营与管理"
publish_status: "INTERNAL"
keywords: ["Shopify", "DNS", "Cloudflare", "CDN", "域名解析"]
---
# Shopify 独立站域名 DNS 解析与 Cloudflare CDN 托管指南

修改 NS 服务器指向 Cloudflare 并配置 A 记录指向 Shopify IP 23.227.38.65。
"""
    },
    {
        "doc_id": "GE-2026-020",
        "category": "06_品牌发布成品",
        "title": "极客帝国 GEEK EMPIRE 品牌品牌资产系统发布公告 v0.1",
        "keywords": ["极客帝国", "GEEK EMPIRE", "发布", "开源", "Skill"],
        "status": "VERIFIED",
        "publish_status": "PUBLISHED",
        "content": """---
doc_id: "GE-2026-020"
title: "极客帝国 GEEK EMPIRE 品牌品牌资产系统发布公告 v0.1"
status: "VERIFIED"
category: "06_品牌发布成品"
publish_status: "PUBLISHED"
keywords: ["极客帝国", "GEEK EMPIRE", "发布", "开源", "Skill"]
---
# 极客帝国 GEEK EMPIRE 品牌品牌资产系统发布公告 v0.1

把实践经验，沉淀为可复制的能力。正式公开发布 geek-empire-skill 0.1 版本。
"""
    }
]

# 20 Realistic Test Queries with typos, colloquial expressions, missing terminology
TEST_QUERIES = [
    {
        "query": "之前那个 AI 软件一直转圈，好像是网络代理有问题，最后怎么处理的？",
        "expected_id": "GE-2026-001",
        "note": "口语化 + 错别字/忘记软件名（飞鸟/Codex）"
    },
    {
        "query": "用 python 把表格导成 csv 之后用 excel 点开全都是乱码黑块",
        "expected_id": "GE-2026-002",
        "note": "口语化 + 忘记 utf-8-sig 专业术语"
    },
    {
        "query": "node 服务在 docker 容器里面跑了几个小时突然报错 137 挂掉",
        "expected_id": "GE-2026-003",
        "note": "故障现象 + 错误码 137"
    },
    {
        "query": "nginx 代理 websocket 总是隔一会就抛出 1006 链接断开",
        "expected_id": "GE-2026-004",
        "note": "网络协议 + 错误码 1006"
    },
    {
        "query": "不小心运行了 git reset 把本地还没提交的代码弄丢了怎么恢复",
        "expected_id": "GE-2026-005",
        "note": "忘记 git reflog 术语"
    },
    {
        "query": "Claude 的组件嵌入网页提示 CORS 被跨域拦截了",
        "expected_id": "GE-2026-006",
        "note": "中英文混用"
    },
    {
        "query": "芍药苗圃国外进口需要准备什么海关植物检疫文件",
        "expected_id": "GE-2026-007",
        "note": "业务场景描述"
    },
    {
        "query": "playwright 爬虫开启无头模式之后过不去 Cloudflare 五秒盾",
        "expected_id": "GE-2026-008",
        "note": "爬虫 + 反爬术语"
    },
    {
        "query": "服务器 linux 用 ssh 连上去卡顿很久才能输入密码",
        "expected_id": "GE-2026-009",
        "note": "忘记 UseDNS 属性名称"
    },
    {
        "query": "WorkBuddy 提示端口被占用 address already in use 怎么释放 PID",
        "expected_id": "GE-2026-010",
        "note": "英文报错 + 端口清理"
    },
    {
        "query": "Windows 怎么把 python 脚本配置成定时任务自动运行",
        "expected_id": "GE-2026-011",
        "note": "忘记 Task Scheduler 英文名"
    },
    {
        "query": "postgres 数据库报 Deadlock Detected 死锁怎么查看持锁进程",
        "expected_id": "GE-2026-012",
        "note": "数据库故障"
    },
    {
        "query": "Stripe 收到老外信用卡 Chargeback 拒付怎么提交资料申诉",
        "expected_id": "GE-2026-013",
        "note": "跨境支付 + 拒付申诉"
    },
    {
        "query": "https 网页打不开提示 certbot SSL 证书过期怎么续期",
        "expected_id": "GE-2026-014",
        "note": "证书过期的解决"
    },
    {
        "query": "Cursor 项目根目录的提示词规则配置文件叫什么名字",
        "expected_id": "GE-2026-015",
        "note": "忘记 .cursorrules 文件名"
    },
    {
        "query": "npm 运行 install 一直提示 ETIMEDOUT 超时怎么切国内淘宝镜像源",
        "expected_id": "GE-2026-016",
        "note": "包管理器网络超时"
    },
    {
        "query": "局域网访问不了我电脑上的 8080 端口，是不是 windows 防火墙挡了",
        "expected_id": "GE-2026-017",
        "note": "端口与防火墙规则"
    },
    {
        "query": "Obsidian 笔记软件怎么建立双向链接网状索引",
        "expected_id": "GE-2026-018",
        "note": "笔记软件双向链接"
    },
    {
        "query": "Shopify 独立站配置 Cloudflare 域名 A 记录应该指向什么 IP",
        "expected_id": "GE-2026-019",
        "note": "电商域名配置"
    },
    {
        "query": "极客帝国 GEEK EMPIRE 品牌系统的首个开源 Skill 版本是多少",
        "expected_id": "GE-2026-020",
        "note": "品牌公告查询"
    }
]


class TestSearchPrecisionBenchmark(unittest.TestCase):

    def setUp(self):
        # Create temp vault with 20 distinct cards
        self.test_dir = tempfile.mkdtemp(prefix="GE_Benchmark_")
        self.vault_path = os.path.join(self.test_dir, "vault")
        os.makedirs(self.vault_path, exist_ok=True)

        for card in SIMULATED_CARDS:
            cat_dir = os.path.join(self.vault_path, card["category"])
            os.makedirs(cat_dir, exist_ok=True)
            file_path = os.path.join(cat_dir, f"{card['doc_id']}_Card.md")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(card["content"])

        self.engine = KnowledgeSearchEngine(self.vault_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_benchmark_precision_20_queries(self):
        """Runs 20 fuzzy queries and calculates exact Top-1 and Top-3 accuracy rates."""
        top1_hits = 0
        top3_hits = 0
        failures = []

        print("\n" + "="*70)
        print("🔍 RUNNING GE-SEARCH PRECISION BENCHMARK (20 CARDS x 20 FUZZY QUERIES)")
        print("="*70)

        for idx, t in enumerate(TEST_QUERIES, 1):
            q = t["query"]
            exp = t["expected_id"]
            results = self.engine.search(q, top_k=3)

            result_ids = [r["doc_id"] for r in results]

            is_top1 = len(result_ids) > 0 and result_ids[0] == exp
            is_top3 = exp in result_ids

            if is_top1:
                top1_hits += 1
            if is_top3:
                top3_hits += 1
            else:
                failures.append({
                    "query_id": idx,
                    "query": q,
                    "expected": exp,
                    "got_ids": result_ids,
                    "note": t["note"]
                })

            status_str = "✅ TOP-1" if is_top1 else ("⚠️ TOP-3" if is_top3 else "❌ MISSED")
            print(f"[{idx:02d}] {status_str} | Query: '{q}' -> Top-1: {result_ids[0] if result_ids else 'NONE'} (Expected: {exp})")

        top1_rate = (top1_hits / len(TEST_QUERIES)) * 100
        top3_rate = (top3_hits / len(TEST_QUERIES)) * 100

        print("="*70)
        print(f"🎯 BENCHMARK SUMMARY:")
        print(f"   Top-1 Accuracy: {top1_hits}/{len(TEST_QUERIES)} ({top1_rate:.1f}%)")
        print(f"   Top-3 Accuracy: {top3_hits}/{len(TEST_QUERIES)} ({top3_rate:.1f}%)")
        print("="*70)

        self.assertGreaterEqual(top1_rate, 85.0, "Top-1 accuracy must be >= 85%")
        self.assertGreaterEqual(top3_rate, 95.0, "Top-3 accuracy must be >= 95%")

    def test_02_status_matrix_and_review_extraction(self):
        """Verifies review_status, verification_status, and matrix rows are correctly parsed."""
        results = self.engine.search("飞鸟 VPN", top_k=1)
        self.assertEqual(len(results), 1)
        res = results[0]

        self.assertEqual(res["doc_id"], "GE-2026-001")
        self.assertEqual(res["verification_status"], "VERIFIED")
        self.assertEqual(res["review_status"], "INTERNAL")
        self.assertIn("verified", res["matrix_summary"])
        self.assertTrue(len(res["matrix_summary"]["verified"]) > 0)
        self.assertTrue(len(res["matrix_summary"]["pending"]) > 0)

    def test_03_agent_rerank_interface(self):
        """Verifies search_for_agent JSON payload structure."""
        payload = self.engine.search_for_agent("Docker 内存", top_k=2)
        self.assertIn("query", payload)
        self.assertIn("candidates", payload)
        self.assertTrue(len(payload["candidates"]) >= 1)
        self.assertEqual(payload["candidates"][0]["doc_id"], "GE-2026-003")


if __name__ == "__main__":
    unittest.main()
