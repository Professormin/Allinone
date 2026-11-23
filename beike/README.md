# 备课 Skill · Beike

面向各学科教师的 AI 备课流程：把学习目标、教材或旧课件，整理成**图解课件 + 逐页教师备课对照表**。

[下载最新版](https://github.com/Professormin/beike/releases/latest) · [源码](https://github.com/Professormin/beike) · [反馈问题](https://github.com/Professormin/beike/issues)

学科、年级、课时、风格和输出目录都可配置。数学、历史、文学、自然科学和职业培训可沿用流程，具体内容由 AI 结合资料生成并核对。

## 能做什么

- 图解原理、过程、关系与证据，避免只堆文字。
- 完整展示计算或论证步骤，配合练习与教师答案。
- 教师表先讲主线，再逐页对应课件；有旧课件时附原页缩略图。
- 默认目标为 PPTX、课件 PDF、教师 DOCX/PDF；实际生成取决于宿主可用的文件制作和渲染工具。

这是 **AI 工作流技能**，不是单独运行就能自动生成全套课件的应用。附带 Python 脚本可独立生成教师 DOCX；不要求私人模板、Office 或付费 API 才能运行该示例。完整课件/PDF 需要宿主提供相应能力。

## 安装

下载并解压版本化 ZIP，得到 `beike/` 文件夹。

也可下载源代码：`git clone https://github.com/Professormin/beike.git`。

- **Codex**：复制到个人技能目录 `~/.codex/skills/beike/`，或设置了 CODEX_HOME 时的 `$CODEX_HOME/skills/beike/`。重新打开会话后调用 `$beike`。
- **Claude Code 等支持 SKILL.md 的工具**：按其技能安装机制放置整个文件夹；路径与调用语法以该工具为准。此版本未逐个平台验证。
- **其他 AI**：提供 `SKILL.md` 和相关 references，要求按流程完成任务；是否能生成 Office 文件取决于该 AI 的能力。

也可用随附的安全复制脚本指定目录（不会覆盖已有安装）：

```bash
python scripts/install.py --target /your/skills/beike
```

## 调用示例

> 用 $beike 做八年级“一次函数”45分钟课。学生已经学过坐标系。请做图解课件和教师备课对照表，保存到当前项目的 output。

> 用 $beike 做高中历史“工业革命”的一课，使用时间轴和史料对照，区分史实与解释。

> 用 $beike 根据上传的旧课件继续下一课，沿用它的风格，计算写全步骤，教师表逐页对应。

## 本地脚本演示（Python 3.10+）

在解压后的 `beike` 目录运行：

```bash
python -m pip install -r requirements.txt
python scripts/demo.py --output ./demo-output
```

它生成原创一次函数示意图、输入 JSON 和一份含两页幻灯片条目的教师 DOCX。该演示验证文件工作流，不是完整课件，图片英文标注用于避免演示依赖特定中文字体。已生成的目录请换新名字，防止覆盖。

自己的已审核内容：

```bash
python scripts/build_prep.py --input prep.json --output teacher.docx
```

可选 `--template reference.docx` 继承用户自己的页面与样式。字段说明见 [输入格式](references/prep-schema.md)。导出 PDF 后仍需逐页检查。

## 测试、打包、许可

```bash
python -m unittest discover -s tests -v
python scripts/package.py --output ./dist
```

打包使用明确文件清单，排除个人配置、生成结果、测试缓存和私有课件。公开发布方法见 [PUBLISHING.md](PUBLISHING.md)。当前版本见 [VERSION](VERSION)。

MIT 许可，允许使用、修改和再分发，见 [LICENSE](LICENSE)。用户提供的教材、图片和课件保留原权利，**不随本技能获得再分发许可**。
