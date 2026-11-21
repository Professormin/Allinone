# 课程配置

设置均为可选，优先使用当前对话。以下是交给 AI 的配置例，不是 build_prep.py 的命令输入。

```json
{
  "subject": "数学",
  "topic": "一次函数的图像",
  "audience": "八年级，已学坐标系",
  "duration_minutes": 45,
  "goals": ["理解斜率", "用两点画出一次函数"],
  "mode": "ordinary",
  "style": {"reference": null, "palette": "cream-blue", "font": "使用当前系统支持的通用中文字体"},
  "outputs": ["pptx", "slides-pdf", "teacher-docx", "teacher-pdf"],
  "output_directory": "./output"
}
```

`mode` 可用普通教学、互动课堂、复习或用户描述。`style.reference` 可指用户有权使用的本地课件；没有也能工作。输出目录相对当前项目解析，不包含创作者的机器路径。语言跟随使用者；字重、字号随投影、纸张和学生年龄调整。

同一流程可用于小学自然、大学化学、历史、文学或职业培训。学科特有的正确性标准必须重新确定，不能只替换标题。
