# 教师表 JSON

`build_prep.py` 使用 python-docx。文件路径相对 JSON 所在目录解析。无需原模板；传入 `--template reference.docx` 时只继承样式、纸张和边距，清除旧正文及页眉页脚。原件不改，输出存在则拒绝覆盖。

顶层：`title`、`intro`、`slides` 必填；`subtitle`、`pronunciation` 可选。

- `intro`：`heading`、`paragraphs` 字符串数组、可选 `image`。
- `pronunciation`：每项 `[术语, 读法与含义]`。
- `slides`：`title`、`image`、`section`、`depth`、`meaning`、`method`、`caution` 必填；`answer` 可选。
- 每页需 `sources` 或 `source_note` 至少一项。`sources` 为数组，每项 `label` 和 `image`（真正原课缩略图）；无旧课件使用 `source_note` 写“自编”及知识依据，不编造原页。

脚本不研究内容、不判断科学正确性、不导出 PDF；应由使用者或 AI 先完成内容和图片，再运行排版。完整最小例由 `scripts/demo.py` 创建。
