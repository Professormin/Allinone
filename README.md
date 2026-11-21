# Remotion Story Studio 0.1.0

可安装的 Codex Skill：可编辑霓虹文字、多字体字形路径，以及根据剧情和角色参考图制作动态漫画。角色、画幅、素材与输出位置可配置。

## 安装

Python 3.10+；创建视频项目还需 Node.js 22.13+（推荐24）和 npm，首次安装需联网。
解压 ZIP 得到 remotion-story-studio 文件夹，运行：

```sh
python remotion-story-studio/scripts/install_skill.py
```

默认安装到 CODEX_HOME/skills（未设置时为用户目录 .codex/skills），不会覆盖已有同名 Skill。也可以用 `--destination <skills-directory>` 指定技能目录。
新会话调用 `$remotion-story-studio`。没有兼容的图像生成工具时，文字视频仍可运行，故事图片需用户提供；不要求用户提交API密钥才能运行本地模板。

## 可运行示例

```sh
python remotion-story-studio/scripts/create_project.py --output ./my-video --install
cd my-video
npm run typecheck
npm run dev
npm run render:neon
npm run render:story
```

NeonText：编辑 text、font、color1、color2、drawSeconds。示例用 SVG 字形路径，不需要 Skia 原生依赖；已有 Skia 工程的接入方式在 references/text-paths.md。
StoryComic：编辑每镜头的 image、caption、seconds；总时长自动计算。内置故事示例是自制几何图形，仅用于验证图片编排、字幕和镜头，不冒充AI角色图。
输出在新项目 out/。字体首次从 Google Fonts 官方仓库下载，授权文件在 public/fonts。下载失败会报告错误，修复后可以用 `--refresh-fonts` 重试。网络不可用时可用 `--skip-fonts` 建立工程，再自行提供字体并配置 manifest。

## 角色故事

在聊天里提交剧情和你有权使用的角色图；Skill 拆分镜、调用会话内可用生图工具、检查一致性，再用 Remotion 编排导出。默认是动态漫画（图片推拉和字幕），不是连续角色动作视频。浏览器面板没有独立的生图 API。
私人角色配置示例见 examples/character.example.json；不要把真实资料提交到公开仓库。

## 验证与打包

```sh
python remotion-story-studio/scripts/verify_package.py
python -m unittest discover -s remotion-story-studio/tests -v
python remotion-story-studio/scripts/package.py --output ./dist
```

下载发布流程见 PUBLISHING.md。MIT 仅覆盖本包原创代码与文档；Remotion 的使用许可按其官方条款，字体按随附许可证。

Render scripts scope TMP/TEMP/TMPDIR to the generated project work/temp directory. Parent system settings are not changed.
