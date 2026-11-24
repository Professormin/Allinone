# codex-proxy-fix

**一键修复：Windows 上开着加速器，浏览器能上网，Codex 却连不上。**

## 为什么会这样

Codex 优先读取用户环境变量 `HTTP_PROXY / HTTPS_PROXY / ALL_PROXY`。这些变量里写的是一个旧端口（比如 `socks5h://127.0.0.1:18120`）。加速器（飞鸟加速、Clash 等）重启后会换端口，但只会自动更新 Windows 系统代理，不会去改这些环境变量。结果就是浏览器正常，Codex 却把请求发到了一个已经没有程序监听的端口。

## 它做什么

1. 备份当前的 4 个用户级代理变量，存到程序旁边的 `backups\` 文件夹。
2. 读取加速器设置的 Windows 系统代理端口，用 curl 测试能不能连通。
3. 测试通过后，把 `HTTP_PROXY / HTTPS_PROXY / ALL_PROXY` 改成 `http://127.0.0.1:端口`，把 `NO_PROXY` 改成 `localhost,127.0.0.1,::1`。

它只改当前用户的这 4 个环境变量，不写注册表，不改防火墙，也不需要管理员权限。

## 使用

1. 先打开加速器并连上节点。
2. 到 [Releases](https://github.com/Professormin/allinone/releases?q=codex-proxy-fix) 下载 `fix_codex_proxy.exe`，双击运行。看到绿色的 `Done.` 就说明改好了。
3. **完全退出 Codex**（托盘图标也要退出，或者在任务管理器里结束进程），再重新打开。

加速器重启后 Codex 又连不上的话，再双击运行一次就行。

### 命令行参数（exe 和 ps1 都支持）

| 参数 | 作用 |
|---|---|
| `-DryRun` | 只预览会改什么，不实际修改 |
| `-Clear` | 删除这 4 个变量，让 Codex 直接跟随系统代理 |
| `-Restore <备份文件>` | 恢复成某次备份的值 |

不想用 exe 的话，也可以直接运行脚本：

```
powershell -ExecutionPolicy Bypass -File "完整路径\fix_codex_proxy.ps1"
```

## 发新版

改完脚本后把本目录的 `VERSION` 改成新版本号并推送到 main，GitHub Actions 会自动编译 exe 并发布 Release `codex-proxy-fix-v版本`。

## 注意

- exe 是用 [ps2exe](https://github.com/MScholtes/PS2EXE) 在 GitHub Actions 上从本目录的 `fix_codex_proxy.ps1` 自动编译出来的，没有代码签名，Windows Defender 或 SmartScreen 可能会报警告。介意的话可以直接用 ps1 脚本，内容完全一样，代码也都在这个仓库里。
- 已经打开的程序会继续用旧的变量值，必须重启后才会生效。

## License

MIT，见仓库根目录 [LICENSE](../LICENSE)。
