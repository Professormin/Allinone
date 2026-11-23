# 随手记 Suiji

**按 Ctrl+Alt+J，在任何软件里把一句话、截图、文件随手扔进本地文件夹，自动带时间戳。**

在几个软件之间来回切换的时候，总会冒出几件想先留着、回头再说的事：一个想法、一张截图、一个刚下载的文件。随手记就是为这种时刻做的。按一下快捷键，扔进去，回车，接着干刚才的事。过几天要找，按日期翻就行。

- 🔑 **全局快捷键**：不用切窗口，在哪个软件里都能用
- 📋 **什么都能收**：直接打字；Ctrl+V 粘贴文字、截图、复制的文件；也可以把文件或文件夹拖进窗口
- 🕒 **自动时间戳**：每条记录带日期和时间，附件按 `2026-11-21_153012_原文件名` 命名
- 📁 **纯本地、纯文件**：存成普通的 Markdown 文件加原文件，用 Obsidian、记事本都能打开，不会被哪个软件锁住
- 🔒 **不联网、不用注册、不花 AI token**，只有一个 Python 文件，代码可以随便看

> 类别：效率工具 / 快速捕获（Quick Capture）/ 收件箱工具

## 安装（30 秒）

1. 到 [Releases](https://github.com/Professormin/allinone/releases/latest) 下载 `Suiji.exe`
2. 双击运行，选一个文件夹用来保存记录（例如你的 Obsidian 库里新建一个“随手记”文件夹）
3. 看到“已就绪”提示，就装好了。以后开机会自动在后台运行

> ⚠️ 第一次运行时，Windows 可能弹出蓝色的“Windows 已保护你的电脑”。这是因为这个小工具没有购买代码签名证书。点 **更多信息 → 仍要运行** 即可。不放心的话，可以直接看源码 `suiji.py`，或者用下面的方法从源码运行。

## 使用

| 操作 | 效果 |
|---|---|
| `Ctrl+Alt+J` | 在任意窗口弹出输入框 |
| 打字后按 `Enter` | 保存并关闭 |
| `Shift+Enter` | 换行 |
| `Ctrl+V` | 粘贴文字、截图（存成 PNG）或复制的文件 |
| 把文件拖进窗口 | 作为附件保存（复制一份，原文件不动） |
| `Esc` / 点 × | 取消，不保存 |

## 保存在哪

```
你选的文件夹/
├─ 2026-11.md                         ← 每月一个文件，每条一行
├─ input/2026-11/
│   ├─ 2026-11-21_153012_截图.png
│   └─ 2026-11-21_160455_报价单.pdf
└─ _收件箱/                            ← 手机等其他设备存的 .txt 放这里，下次保存时自动并入
```

`2026-11.md` 里的样子：

```markdown
- 11-21 15:30 这个配色可以用在封面 ![2026-11-21_153012_截图.png](<input/2026-11/2026-11-21_153012_截图.png>)
- 11-21 16:04 [2026-11-21_160455_报价单.pdf](<input/2026-11/2026-11-21_160455_报价单.pdf>)
```

在 Obsidian 里打开，图片直接显示，文件点一下就能打开。

**找最近几天的东西**：在 `input` 文件夹里按名称排序就是按时间排；在资源管理器的搜索框输入 `2026-11-2`，能筛出 20 到 29 号存的文件。

## 从源码运行（不想用 exe 的话）

需要 Windows 和 Python 3.8 以上版本（[python.org](https://www.python.org/downloads/)，安装时勾选 tcl/tk）。不需要安装任何第三方库。

```bat
pythonw suiji.py
```

第一次运行会让你选文件夹，并设置开机自启。

**命令行用法**（适合脚本或 AI 助手调用）：

```bat
python suiji.py 要存的一句话
python suiji.py --stdin < note.txt   & rem 多行原样保存
python suiji.py --folder             & rem 重新选择保存文件夹
python suiji.py --uninstall          & rem 取消开机自启
```

**便携模式**：在 `Suiji.exe` 或 `suiji.py` 旁边放一个 `config.json`，内容为 `{"folder": "D:\\你的文件夹"}`，就会优先用它，适合放在 U 盘里。默认配置保存在 `%APPDATA%\Suiji\config.json`。

## 自己打包 exe

```bat
build.bat
```

会自动安装 [PyInstaller](https://pyinstaller.org)，生成 `dist\Suiji.exe`。

## 卸载

1. 运行 `Suiji.exe --uninstall`（或 `python suiji.py --uninstall`）
2. 在任务管理器里结束 `Suiji.exe` 或 `pythonw.exe`
3. 删除 exe。你保存的记录都在你选的文件夹里，不受影响

## 常见问题

- **按快捷键没反应**：双击一次 `Suiji.exe` 就会重新启动后台。如果提示“Ctrl+Alt+J 被占用”，说明别的软件（输入法、聊天软件等）用了同一个快捷键。
- **日志在哪**：`%APPDATA%\Suiji\daemon.log` 和 `popup.log`。

---

## English

**Suiji** is a tiny Windows quick-capture tool. Press **Ctrl+Alt+J** anywhere, type a note or paste a screenshot or copied files (or drag files in), press Enter, and it is appended with a timestamp to a monthly Markdown file in a local folder you choose. Attachments are copied to `input/YYYY-MM/` with timestamped names. No network, no account, no AI tokens, Python standard library only. Download `Suiji.exe` from Releases, run it once, pick a folder, and you are done.

## License

[MIT](../LICENSE)
