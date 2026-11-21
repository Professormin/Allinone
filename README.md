# 视频素材匣 · Video Material Inbox

一个按主题积累视频素材的 Codex Skill。平时粘截图、拖文件或贴路径，等需要做视频时再调取。可取得的原件按字节复制，其他来源保留可追溯的索引。

## 安装

从 [GitHub Releases](https://github.com/Professormin/video-material-inbox/releases) 下载并解压。把整个 `video-material-inbox` 目录放到个人 `~/.agents/skills/`，或项目内的 `.agents/skills/`。重新打开 Codex 后用 `$video-material-inbox` 调用。需要 Codex 能读写目标目录，复制附件原件还需要界面提供源文件或原始字节。无需额外运行时依赖。

## 示例

1. `$video-material-inbox 收素材：秋季园艺。保存到当前工作区的 video-materials。`
2. 拖进一张原图，附一句 `这张放片头`。下一条消息可以只粘本地路径。
3. `看一下素材`。在新聊天中也可以说 `$video-material-inbox 打开秋季园艺，看一下素材`，并提供原素材根目录。
4. `用秋季园艺的素材做一个 30 秒横屏视频。`

运行结果在主题目录，索引是 `index.jsonl`，原件副本在 `files/`。素材留在调用时指定的位置，发布包只含 Skill、说明和许可证。界面仅提供图片预览时，索引会注明取得的版本。

MIT License.
