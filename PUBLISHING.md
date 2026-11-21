# 可重复的公开发布流程

本文件描述发布方法，不代表某次版本已经上线。实际公开链接应以托管平台验证结果为准。

## 首次发布

1. 在维护者账户创建独立公开仓库，例如 `beike`，只上传本工具。不改变其他仓库的可见性。
2. 安装依赖，运行测试和示例，检查教师 DOCX 及示意图。修改版本号后重新打包。
3. 检查待发布文件清单，排除私有教材、学生信息、个人配置、凭据、生成的教学资料和硬编码个人路径。许可证仅覆盖自己有权发布的代码和文字。
4. 推送工具源代码；通过 GitHub Release 上传版本化 ZIP 和 SHA256。下载 ZIP 解压即为 `beike/`，可直接安装。
5. 使用未登录的下载请求验证公开访问、ZIP 内容、校验和及示例运行，再公布地址。

## 命令示例

在本工具目录执行；先用 GitHub CLI `gh auth login` 登录。将 `YOUR_ACCOUNT/beike` 替换为自己的仓库，勿把令牌写进命令或仓库。

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/demo.py --output ./demo-output
python scripts/package.py --output ./dist
git init -b main
git add SKILL.md README.md LICENSE VERSION requirements.txt PUBLISHING.md .gitignore agents references scripts tests
git commit -m "Release Beike 0.1.0"
gh repo create YOUR_ACCOUNT/beike --public --source . --remote origin --push
gh release create v0.1.0 dist/beike-v0.1.0.zip dist/beike-v0.1.0.sha256 --repo YOUR_ACCOUNT/beike --target main --title "Beike 0.1.0" --notes "Cross-subject lesson preparation skill and teacher document generator."
```

已有仓库则配置 origin 并正常 push，不重复创建。后续版本更新 VERSION、测试、打包、提交，再建立新 tag/Release；不要覆盖旧下载包。

若连接器只能写已有仓库，就先由维护者建好仓库，再用连接器上传。若无法创建 Release，可先发布源代码及版本 ZIP 到仓库的 `downloads/`，验证 raw 下载，并明确称为“仓库下载包”，不要称为 Release。

记录：版本、仓库 URL、提交 SHA、Release 或下载 URL、ZIP SHA256、测试结果、公开访问验证结果。此格式也可用于后续其他公众工具。
