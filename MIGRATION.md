# 仓库迁移记录（溯源用）

> **给以后推送这些工具的人或 AI：** 下面这些工具原来各有一个独立仓库，**2026-11-23 起全部并进 `Professormin/allinone`（GitHub 实名 `Allinone`）的子目录，原仓库已删除。** 推送、发布、写安装链接之前，先对照这张表改成新路径。

| 原仓库（已删除，除标注外） | 现在的位置 | 迁移日期 | 说明 |
| --- | --- | --- | --- |
| `Professormin/suiji` | 仓库本身改名为 `Professormin/Allinone`；随手记代码在 [`suishouji/`](suishouji/) | 2026-11-23 | 改名而非删除，旧地址 GitHub 会自动跳转；Suiji.exe 的 Release 留在本仓库，新版标签用 `suishouji-v版本` |
| `Professormin/beike` | [`beike/`](beike/) | 2026-11-23 | 已删除。安装包在 [`zip/`](zip/) |
| `Professormin/video-material-inbox` | [`video-material-inbox/`](video-material-inbox/)；演示网页在 [`docs/video-material-inbox/`](docs/video-material-inbox/) | 2026-11-23 | 已删除。网页新地址 https://professormin.github.io/Allinone/video-material-inbox/ ；安装包在 `zip/` |
| `Professormin/remotion-story-studio` | [`remotion-story-studio/`](remotion-story-studio/) | 2026-11-23 | 已删除。安装包在 `zip/` |
| `Professormin/Geek-Empire` | [`geek-empire/`](geek-empire/) | 2026-11-23 | 已删除。目录名改成全小写 |
| `Professormin/safe-duplicate-cleaner` | [`safe-duplicate-cleaner/`](safe-duplicate-cleaner/) | 2026-11-23 | 已删除 |
| （从未单独建仓）`suiwen`、`yijuhua-guidang` | [`suiwen/`](suiwen/)、[`yijuhua-guidang/`](yijuhua-guidang/) | 2026-11-23 | 旧 README 里写过的 `Professormin/suiwen`、`Professormin/yijuhua-guidang` 地址从未存在 |

## 旧地址换新地址的写法

- 仓库主页：`https://github.com/Professormin/<旧名>` → `https://github.com/Professormin/allinone/tree/main/<子目录>`
- 文件：`.../<旧名>/blob/main/<文件>` → `.../allinone/blob/main/<子目录>/<文件>`
- 下载最新版：`.../<旧名>/releases/latest` → `https://github.com/Professormin/allinone/raw/main/zip/<安装包名>`
- 用 GitHub API 上传文件：路径前面加子目录，比如 `repos/Professormin/allinone/contents/<子目录>/<文件>`；不要再往仓库根目录传
- 建 Release：标签名带上工具名，比如 `beike-v0.2.0`，避免和别的工具撞名

## 没迁过来的东西

- 原仓库的 Release 页面：最新版安装包已放进 `zip/`；全部旧版本和发布说明备份在 iris 本机 `D:\00_Professormin\00_mybrian\tools\allinone-原仓库发布备份.zip`
- 原仓库的版本标签名（如 `v0.1.5`）：对应的提交都在本仓库历史里，标签名本身没搬
- 原仓库的提交记录：已用 git subtree 完整保留，`git log -- <子目录>` 可查

## 以后再挪仓库

任何工具换了仓库或子目录，都在这张表里加一行，并在仓库首页 README 顶部的「仓库迁移」提示里能看到。
