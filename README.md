# allinone

**iris 的效率工具和 AI 技能系列。每个子目录是一个独立的工具，可以单独拿走用。**

> **📦 仓库迁移（2026-11-23）：** 原来的独立仓库 `suiji`、`beike`、`video-material-inbox`、`remotion-story-studio`、`Geek-Empire`、`safe-duplicate-cleaner` 已全部并进本仓库的子目录，原仓库已删除（`suiji` 是改名成了本仓库）。推送或发布前请先看 [迁移记录 MIGRATION.md](MIGRATION.md)，按新路径操作。

技能都按通用的 Agent Skills 格式写（`SKILL.md` + 脚本），Claude、Codex、Cursor、Gemini CLI 等都能装；不支持技能的 AI（ChatGPT、豆包等）把 `SKILL.md` 正文贴进自定义指令也能用。脚本只用 Python 标准库。

| 目录 | 是什么 | 一句话说明 |
| --- | --- | --- |
| [`suishouji/`](suishouji/) | Windows 小工具 | 随手记：按 Ctrl+Alt+J，在任何软件里把一句话、截图、文件扔进本地文件夹，自动带时间戳 |
| [`suiwen/`](suiwen/) | AI 技能 | 随手问：一次性问题都在一个置顶对话里问，默认每题独立；说「存档」写成知识卡片存进本地 |
| [`yijuhua-guidang/`](yijuhua-guidang/) | AI 技能 | 一句话归档：发一句话就存进本地笔记库，不复述不追问，只回文件路径 |
| [`geek-empire/`](geek-empire/) | AI 技能 | 极客帝国：把 AI 对话整理成结构化知识卡片，自动编号、分类、脱敏、建索引；附视频脚本创作技能组 |
| [`video-material-inbox/`](video-material-inbox/) | AI 技能 | 视频素材匣：把截图、文件和链接按主题收好，做视频时随时找回 |
| [`remotion-story-studio/`](remotion-story-studio/) | AI 技能 | Remotion 故事工作室：可编辑霓虹文字，按剧情和角色参考图做动态漫画视频 |
| [`beike/`](beike/) | AI 技能 | 备课：把学习目标、教材或旧课件整理成图解课件 + 逐页教师备课对照表 |
| [`safe-duplicate-cleaner/`](safe-duplicate-cleaner/) | 电脑小工具 | 安全查重清理：先保护完整项目文件夹，重复文件隔离而不直接删除 |
| [`web-gallery-grabber/`](web-gallery-grabber/) | 电脑小工具 + AI 技能 | 网页图库一键存图：一个网页上的图全部下载原图，按图下的名字命名，附下载清单 |
| [`codex-proxy-fix/`](codex-proxy-fix/) | Windows 小工具 | Codex 代理修复：开着加速器 Codex 却连不上网时双击一下，把失效的代理变量同步到加速器当前端口 |

每个子目录都保留了原仓库的提交记录，用 `git log -- <目录名>` 能看到。

## 复制这句话安装某个技能

```text
请帮我安装「随手问」：https://github.com/Professormin/allinone/tree/main/suiwen
```

把链接换成上表里对应的目录即可。

## 下载打包好的版本

所有安装包都放在 [`zip/`](zip/)（附 sha256 校验值）：suiwen、yijuhua-guidang、beike、video-material-inbox、remotion-story-studio、web-gallery-grabber。Claude 网页 / 桌面版直接上传对应的 zip。随手记的 `Suiji.exe` 在 [Releases](https://github.com/Professormin/allinone/releases/latest)。Codex 代理修复的 `fix_codex_proxy.exe` 在 [Releases](https://github.com/Professormin/allinone/releases?q=codex-proxy-fix)（标签 `codex-proxy-fix-v版本`）。

视频素材匣的演示网页在 [`docs/video-material-inbox/`](docs/video-material-inbox/)，开启 GitHub Pages 后地址是 https://professormin.github.io/Allinone/video-material-inbox/ 。

## 新增工具的约定

- 每个工具一个子目录，目录名用拼音或英文短横线（如 `yijuhua-guidang`）。
- 技能目录里放 `SKILL.md`、`README.md`、`VERSION`，脚本放 `scripts/`；改完重新打包 `zip/<目录名>.zip`。
- 许可证统一用根目录的 [MIT](LICENSE)（原来自带 LICENSE 的子目录保留各自的副本）。
