# 供货征集表 wp-supply-intake：手机填表，数据和照片直接进你自己的 WordPress 后台

一个 WordPress 小插件。装上后你的网站多出一个网址（`你的网址/supply/`），把它发到微信、Messenger、Facebook，对方用手机就能填写：有什么品种、种了多少、能供什么、按什么单位报价、配几张照片。点「提交」后，数据进你的网站后台，可以汇总、筛选、导出 Excel。

示例场景是**花卉种苗 / 鲜切花供货征集**，字段可以让 AI 助手按你的行业改。

## 解决什么问题
- 在群里一条条问报价、再手抄进表格：发一个链接，对方自己填
- 单位混乱（棵 / 苗 / 支）：每种供货方式单独一行报价，单位固定
- 现成表单平台一次只能填一条，没有拼音选品种、自动汇总：这里都有
- 不想让对方“生成图片再发回给我”：提交即进后台；对方想留底可以下载长图

## 功能
- 手机优先；填到一半关掉，内容还在（存在对方手机浏览器里）
- 品种分三类：商业栽培品种 / 高单价进口品种 / 独家新品种；输入拼音首字母弹出候选
- 每个品种可多选：原棵（元/棵）、分株苗（元/苗）、鲜切花（元/支，含花苞直径、枝长、采收期）
- 照片选填（每张单独上传，不怕一次太大失败），可写文字描述代替
- 汇总页：已填几个品种 / 几亩，还差什么一目了然
- 独家新品种附一份简版合作协议，可下载为 Word
- 后台：按提交人查看、全部品种总表、筛选（只看鲜切花 / 种苗 / 新品种）、按品种合并、导出 CSV（Excel 直接打开）、删除

## 安装（3 步）
1. 下载 [`zip/wp-supply-intake-v1.1.0.zip`](../zip/wp-supply-intake-v1.1.0.zip)（sha256 见同目录）
2. WordPress 后台 → 插件 → 安装插件 → 上传插件 → 选这个 zip → 启用
3. 打开 `你的网址/supply/`。如果是 404：到「设置 → 固定链接」页面打开一次（不用改任何东西），或者先用 `你的网址/?pw_supply=1`

更新：上传新的 zip，选「使用上传的版本替换当前版本」。

## 改成你自己的
- 品种列表、品牌名、协议文字都在 `pw-supply-intake/form.html` 里；把文件交给 WorkBuddy、Claude 等 AI 助手，说清你要收什么字段即可
- 协议里的乙方名称、电话已留空，按需填写

## 注意
- 服务器在国外时，国内微信里打开会慢几秒
- 微信内置浏览器一般不让下载文件，所以设计成“对方只管提交”
- 防刷：每个 IP 每小时最多 30 次提交，带隐藏防机器人字段

## English
A tiny WordPress plugin that serves a mobile-first supplier intake form at `/supply/`. Submissions (text + photos) land in your own WP admin as private posts, with a merged table view, filters and CSV export. Example use case: flower nursery / cut-flower supply collection. Install: Plugins → Add New → Upload `zip/wp-supply-intake-v1.1.0.zip`, activate, visit `/supply/` (re-save Permalinks if you get a 404).

## License
MIT（见仓库根目录 LICENSE）

## 更新记录
- 1.1.0：三类品种；原棵 / 分株苗 / 鲜切花可多选、各自按棵 / 苗 / 支报价；后台总表筛选、按品种合并、导出 CSV、删除
