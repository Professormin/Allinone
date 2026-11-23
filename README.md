# allinone

**iris 的效率工具和 AI 技能合集。每个子目录是一个独立的工具，可以单独拿走用。**

技能都按通用的 Agent Skills 格式写（`SKILL.md` + 脚本），Claude、Codex、Cursor、Gemini CLI 等都能装；不支持技能的 AI（ChatGPT、豆包等）把 `SKILL.md` 正文贴进自定义指令也能用。脚本只用 Python 标准库。

| 目录 | 是什么 | 一句话说明 |
| --- | --- | --- |
| [`suiji/`](suiji/) | Windows 小工具 | 随手记：按 Ctrl+Alt+J，在任何软件里把一句话、截图、文件扔进本地文件夹，自动带时间戳 |
| [`suiwen/`](suiwen/) | AI 技能 | 随手问：一次性问题都在一个置顶对话里问，默认每题独立；说「存档」写成知识卡片存进本地 |
| [`yijuhua-guidang/`](yijuhua-guidang/) | AI 技能 | 一句话归档：发一句话就存进本地笔记库，不复述不追问，只回文件路径 |

## 复制这句话安装某个技能

```text
请帮我安装「随手问」：https://github.com/Professormin/allinone/tree/main/suiwen
```

把链接换成上表里对应的目录即可。Claude 网页 / 桌面版直接上传 [`zip/`](zip/) 里打包好的 zip。

## 新增工具的约定

- 每个工具一个子目录，目录名用拼音或英文短横线（如 `yijuhua-guidang`）。
- 技能目录里放 `SKILL.md`、`README.md`、`VERSION`，脚本放 `scripts/`；改完重新打包 `zip/<目录名>.zip`。
- 许可证统一用根目录的 [MIT](LICENSE)。
