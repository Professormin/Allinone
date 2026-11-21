# -*- coding: utf-8 -*-
"""
Suiji 随手记 —— Windows 全局快捷键快速收集工具（Quick Capture）
https://github.com/Professormin/suiji     MIT License

按 Ctrl+Alt+J，在任何软件里把一句话、截图、文件扔进本地文件夹，自动带时间戳。
不联网、不用账号、不花 AI token，只用 Python 标准库。

用法：
  双击 Suiji.exe（或 pythonw suiji.py）  首次运行选保存文件夹，并自动开机自启；之后弹出输入框
  Ctrl+Alt+J                            任意窗口弹出输入框
      · 打字，Enter 保存，Shift+Enter 换行，Esc 取消
      · Ctrl+V：文字 / 截图（存成 PNG）/ 复制的文件
      · 文件、文件夹可直接拖进窗口
  suiji.py 一句话                        命令行直接存
  suiji.py --stdin < 文本               给脚本或 AI 调用（多行原样）
  suiji.py --merge                      把 _收件箱 里的 .txt 并入月文件
  suiji.py --folder                     重新选择保存文件夹
  suiji.py --uninstall                  取消开机自启

保存结构（<保存文件夹> 由你选择）：
  <保存文件夹>/YYYY-MM.md                         每条一行：- MM-DD HH:MM 内容 + 附件链接
  <保存文件夹>/input/YYYY-MM/YYYY-MM-DD_HHMMSS_原文件名   附件（复制，不动原文件）
  <保存文件夹>/_收件箱/*.txt                       手机等其他设备丢进来的文字，下次保存时自动并入
"""
import os
import sys
import json
import shutil
from datetime import datetime, timezone, timedelta

VERSION = "1.0.0"
APP = "Suiji"
BJ = timezone(timedelta(hours=8))   # 时间戳用北京时间；需要本地时间可改成 None
FROZEN = getattr(sys, "frozen", False)
HERE = os.path.dirname(sys.executable if FROZEN else os.path.abspath(__file__))
APPDATA_DIR = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), APP)
PORTABLE_CFG = os.path.join(HERE, "config.json")
USER_CFG = os.path.join(APPDATA_DIR, "config.json")


def now():
    return datetime.now(BJ) if BJ else datetime.now().astimezone()


# ---------------- 配置 ----------------
def cfg_path():
    return PORTABLE_CFG if os.path.exists(PORTABLE_CFG) else USER_CFG


def load_cfg():
    try:
        with open(cfg_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_cfg(cfg):
    p = cfg_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def note_dir():
    """优先级：环境变量 SUIJI_DIR > config.json 的 folder > 未设置(None)"""
    d = os.environ.get("SUIJI_DIR") or load_cfg().get("folder")
    return d or None


def choose_folder(parent=None):
    import tkinter as tk
    from tkinter import filedialog, messagebox
    own = parent is None
    if own:
        parent = tk.Tk()
        parent.withdraw()
        parent.attributes("-topmost", True)
    messagebox.showinfo("随手记", "请选择一个文件夹，用来保存你随手记下的文字、截图和文件。\n\n"
                        "建议放在 Obsidian 库或经常备份的位置。", parent=parent)
    d = filedialog.askdirectory(parent=parent, title="随手记：选择保存文件夹")
    if own:
        parent.destroy()
    if not d:
        return None
    d = os.path.normpath(d)
    cfg = load_cfg()
    cfg["folder"] = d
    save_cfg(cfg)
    return d


def log_dir():
    os.makedirs(APPDATA_DIR, exist_ok=True)
    return APPDATA_DIR


def log(name, m):
    try:
        with open(os.path.join(log_dir(), name), "a", encoding="utf-8") as f:
            f.write(now().strftime("%m-%d %H:%M:%S ") + m + "\n")
    except Exception:
        pass


def _dirs():
    d = note_dir()
    if not d:
        raise RuntimeError("还没有选择保存文件夹，请双击 Suiji 运行一次")
    return d, os.path.join(d, "_收件箱"), os.path.join(d, "input")


IMG_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")


# ---------------- 存文字 ----------------
def month_file(dt):
    NOTE_DIR = _dirs()[0]
    path = os.path.join(NOTE_DIR, dt.strftime("%Y-%m") + ".md")
    if not os.path.exists(path):
        os.makedirs(NOTE_DIR, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("---\ntags: [随手记]\n---\n# 随手记 %s\n\n" % dt.strftime("%Y-%m"))
    return path


def format_line(text, dt, links=()):
    lines = text.strip("\r\n").replace("\r\n", "\n").split("\n") if text.strip() else [""]
    first = lines[0]
    if links:
        first = (first + " " if first else "") + " ".join(links)
    out = "- %s %s\n" % (dt.strftime("%m-%d %H:%M"), first)
    for extra in lines[1:]:
        out += "  " + extra + "\n"
    return out


def append(text, dt=None, links=()):
    if not (text and text.strip()) and not links:
        return None
    dt = dt or now()
    path = month_file(dt)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    with open(path, "a", encoding="utf-8") as f:
        if content and not content.endswith("\n"):
            f.write("\n")
        f.write(format_line(text or "", dt, links))
    return path


def merge_inbox():
    INBOX = _dirs()[1]
    if not os.path.isdir(INBOX):
        return 0
    done_dir = os.path.join(INBOX, "_已并入")
    files = [os.path.join(INBOX, n) for n in os.listdir(INBOX) if n.lower().endswith(".txt")]
    files.sort(key=os.path.getmtime)
    n = 0
    for fp in files:
        with open(fp, "r", encoding="utf-8-sig", errors="replace") as f:
            text = f.read()
        dt = datetime.fromtimestamp(os.path.getmtime(fp), BJ) if BJ else datetime.fromtimestamp(os.path.getmtime(fp)).astimezone()
        if append(text, dt):
            n += 1
        os.makedirs(done_dir, exist_ok=True)
        target = os.path.join(done_dir, os.path.basename(fp))
        if os.path.exists(target):
            target = target[:-4] + dt.strftime("_%Y%m%d%H%M%S") + ".txt"
        os.replace(fp, target)
    return n


# ---------------- 存附件 ----------------
def _unique(path):
    base, ext = os.path.splitext(path)
    i = 2
    while os.path.exists(path):
        path = "%s_%d%s" % (base, i, ext)
        i += 1
    return path


def store_attachments(items, dt):
    """items: [("file", 路径) | ("png", 临时png路径)] → 返回 markdown 链接列表"""
    if not items:
        return []
    NOTE_DIR, _, INPUT_DIR = _dirs()
    folder = os.path.join(INPUT_DIR, dt.strftime("%Y-%m"))
    os.makedirs(folder, exist_ok=True)
    stamp = dt.strftime("%Y-%m-%d_%H%M%S")
    links = []
    for kind, src in items:
        if kind == "png":
            name = stamp + "_截图.png"
            dst = _unique(os.path.join(folder, name))
            shutil.move(src, dst)
        else:
            name = stamp + "_" + os.path.basename(src.rstrip("\\/"))
            dst = _unique(os.path.join(folder, name))
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        rel = os.path.relpath(dst, NOTE_DIR).replace("\\", "/")
        label = os.path.basename(dst)
        if dst.lower().endswith(IMG_EXT):
            links.append("![%s](<%s>)" % (label, rel))
        else:
            links.append("[%s](<%s>)" % (label, rel))
    return links


def dib_to_ppm(dib):
    """把剪贴板 CF_DIB 位图转成 PPM 字节（支持 24/32 位，常见截图格式）"""
    import struct
    hsize, w, h, _planes, bpp, comp = struct.unpack_from("<IiiHHI", dib, 0)
    clr_used = struct.unpack_from("<I", dib, 32)[0]
    if bpp not in (24, 32):
        raise ValueError("暂不支持 %d 位图片" % bpp)
    off = hsize
    if comp == 3 and hsize == 40:
        off += 12  # BI_BITFIELDS 的 3 个颜色掩码
    off += clr_used * 4
    stride = ((w * bpp + 31) // 32) * 4
    step = bpp // 8
    rows = range(abs(h) - 1, -1, -1) if h > 0 else range(abs(h))
    out = bytearray(b"P6\n%d %d\n255\n" % (w, abs(h)))
    for r in rows:
        row = dib[off + r * stride: off + r * stride + w * step]
        rgb = bytearray(w * 3)
        rgb[0::3] = row[2::step]
        rgb[1::3] = row[1::step]
        rgb[2::3] = row[0::step]
        out += rgb
    return bytes(out)


# ---------------- Windows 剪贴板 / 拖放（ctypes，免安装） ----------------
def _win():
    import ctypes
    from ctypes import wintypes
    u32, k32, sh32 = ctypes.windll.user32, ctypes.windll.kernel32, ctypes.windll.shell32
    u32.GetClipboardData.restype = ctypes.c_void_p
    u32.GetClipboardData.argtypes = [wintypes.UINT]
    k32.GlobalLock.restype = ctypes.c_void_p
    k32.GlobalLock.argtypes = [ctypes.c_void_p]
    k32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    k32.GlobalSize.restype = ctypes.c_size_t
    k32.GlobalSize.argtypes = [ctypes.c_void_p]
    sh32.DragQueryFileW.argtypes = [ctypes.c_void_p, wintypes.UINT, wintypes.LPWSTR, wintypes.UINT]
    sh32.DragQueryFileW.restype = wintypes.UINT
    sh32.DragFinish.argtypes = [ctypes.c_void_p]
    return ctypes, wintypes, u32, k32, sh32


def _hdrop_files(sh32, ctypes, hdrop):
    n = sh32.DragQueryFileW(hdrop, 0xFFFFFFFF, None, 0)
    files = []
    for i in range(n):
        ln = sh32.DragQueryFileW(hdrop, i, None, 0)
        buf = ctypes.create_unicode_buffer(ln + 1)
        sh32.DragQueryFileW(hdrop, i, buf, ln + 1)
        files.append(buf.value)
    return files


def read_clipboard_attachment():
    """返回 ("files", [路径]) / ("dib", 字节) / None（剪贴板是文字时）"""
    ctypes, wintypes, u32, k32, sh32 = _win()
    CF_DIB, CF_HDROP = 8, 15
    if not u32.OpenClipboard(None):
        plog("打开剪贴板失败")
        return None
    try:
        fmts, f = [], 0
        while True:
            f = u32.EnumClipboardFormats(f)
            if not f:
                break
            fmts.append(f)
        plog("剪贴板格式：%s" % fmts[:20])
        if u32.IsClipboardFormatAvailable(CF_HDROP):
            h = u32.GetClipboardData(CF_HDROP)
            return ("files", _hdrop_files(sh32, ctypes, h)) if h else None
        if u32.IsClipboardFormatAvailable(CF_DIB):
            h = u32.GetClipboardData(CF_DIB)
            p = k32.GlobalLock(h)
            try:
                data = ctypes.string_at(p, k32.GlobalSize(h))
            finally:
                k32.GlobalUnlock(h)
            return ("dib", data)
        return None
    finally:
        u32.CloseClipboard()


def enable_drop(root, on_files):
    """让 Tk 窗口接收资源管理器拖进来的文件"""
    ctypes, wintypes, u32, k32, sh32 = _win()
    WM_DROPFILES, GWLP_WNDPROC = 0x0233, -4
    LRESULT = ctypes.c_ssize_t
    WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
    setp = getattr(u32, "SetWindowLongPtrW", u32.SetWindowLongW)
    setp.restype = ctypes.c_void_p
    setp.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_void_p]
    u32.CallWindowProcW.restype = LRESULT
    u32.CallWindowProcW.argtypes = [ctypes.c_void_p, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    pending = []

    def poll():
        if pending:
            got = pending[:]
            del pending[:]
            on_files(got)
        root.after(150, poll)
    root.after(150, poll)
    root.update_idletasks()
    hwnds = [int(root.wm_frame(), 16), root.winfo_id()]
    keep = []
    for hwnd in hwnds:
        sh32.DragAcceptFiles(hwnd, True)
        old = [None]

        def proc(h, msg, wp, lp, old=old):
            if msg == WM_DROPFILES:
                try:
                    files = _hdrop_files(sh32, ctypes, wp)
                    sh32.DragFinish(wp)
                    plog("收到拖放：%s" % files)
                    pending.extend(files)
                except Exception:
                    import traceback
                    plog("拖放读取出错：" + traceback.format_exc())
                return 0
            return u32.CallWindowProcW(old[0], h, msg, wp, lp)

        cb = WNDPROC(proc)
        old[0] = setp(hwnd, GWLP_WNDPROC, ctypes.cast(cb, ctypes.c_void_p))
        keep.append(cb)
    root._drop_keep = keep  # 防止回调被回收


# ---------------- 弹窗 ----------------
def plog(m):
    log("popup.log", m)


def popup():
    import tkinter as tk
    import tempfile
    root = tk.Tk()
    root.title("随手记")
    root.attributes("-topmost", True)
    w, h = 600, 220
    root.geometry("%dx%d+%d+%d" % (w, h, (root.winfo_screenwidth() - w) // 2,
                                    (root.winfo_screenheight() - h) // 3))
    tk.Label(root, text="Enter 保存 · Shift+Enter 换行 · Esc 取消 · Ctrl+V 可粘截图/文件 · 文件可直接拖进来",
             fg="#666").pack(anchor="w", padx=10, pady=(8, 2))
    info = tk.Label(root, text="", fg="#2a7", anchor="w", justify="left", wraplength=560)
    info.pack(side="bottom", fill="x", padx=10, pady=(2, 8))
    box = tk.Text(root, height=3, font=("Microsoft YaHei", 12), wrap="word")
    box.pack(fill="both", expand=True, padx=10)
    items = []  # [("file", path) | ("png", tmp)]

    def refresh():
        names = [("截图" if k == "png" else os.path.basename(p.rstrip("\\/"))) for k, p in items]
        info.config(text=("📎 %d 个附件：" % len(items) + "、".join(names)) if items else "")

    def grab_focus():
        """拖放后焦点还留在资源管理器，这里把弹窗抢回前台，保证 Enter 是按给弹窗的"""
        try:
            import ctypes
            u32 = ctypes.windll.user32
            hwnd = int(root.wm_frame(), 16)
            u32.keybd_event(0x12, 0, 0, 0)       # 按一下 Alt，Windows 才允许抢前台
            u32.keybd_event(0x12, 0, 2, 0)
            u32.ShowWindow(hwnd, 5)
            u32.SetForegroundWindow(hwnd)
        except Exception:
            pass
        root.lift()
        root.focus_force()
        box.focus_set()
        box.mark_set("insert", "end-1c")

    def add_files(files):
        plog("加入附件：%s" % files)
        for f in files:
            items.append(("file", f))
        refresh()
        grab_focus()

    def paste(event=None):
        import traceback
        try:
            got = read_clipboard_attachment()
            plog("Ctrl+V 剪贴板结果：%s" % (got[0] if got else "文字/空"))
        except Exception:
            plog("Ctrl+V 出错：" + traceback.format_exc())
            got = None
        if not got:
            return None  # 普通文字，交给默认粘贴
        kind, data = got
        if kind == "files":
            add_files(data)
        else:
            try:
                ppm = os.path.join(tempfile.gettempdir(), "suiji_clip.ppm")
                with open(ppm, "wb") as f:
                    f.write(dib_to_ppm(data))
                img = tk.PhotoImage(file=ppm)
                png = tempfile.mktemp(suffix=".png", prefix="suiji_")
                img.write(png, format="png")
                os.remove(ppm)
                items.append(("png", png))
                refresh()
            except Exception as e:
                info.config(text="截图没粘上：%s" % e, fg="#c33")
        return "break"

    def save(event=None):
        text = box.get("1.0", "end")
        dt = now()
        try:
            merge_inbox()
            links = store_attachments(items, dt)
            path = append(text, dt, links)
        except Exception as e:
            root.destroy()
            from tkinter import messagebox
            messagebox.showerror("随手记", "没存上：%s\n\n原文：\n%s" % (e, text))
            return "break"
        root.destroy()
        if path:
            show_toast("已存 → " + path + ("（附件 %d 个）" % len(links) if links else ""))
        return "break"

    def newline(event=None):
        box.insert("insert", "\n")
        return "break"

    box.bind("<Return>", save)
    root.bind("<Return>", save)
    root.bind("<KP_Enter>", save)
    box.bind("<Shift-Return>", newline)
    box.bind("<Control-v>", paste)
    box.bind("<Control-V>", paste)
    root.bind("<Escape>", lambda e: root.destroy())
    try:
        enable_drop(root, add_files)
        plog("拖放已开启")
    except Exception:
        import traceback
        plog("拖放开启失败：" + traceback.format_exc())
    root.after(50, lambda: (root.lift(), root.focus_force(), box.focus_force()))
    root.mainloop()


def show_toast(msg):
    import tkinter as tk
    t = tk.Tk()
    t.overrideredirect(True)
    t.attributes("-topmost", True)
    tk.Label(t, text=msg, bg="#333", fg="white", padx=12, pady=8).pack()
    t.update_idletasks()
    t.geometry("+%d+%d" % (t.winfo_screenwidth() - t.winfo_width() - 20,
                           t.winfo_screenheight() - t.winfo_height() - 60))
    t.after(1800, t.destroy)
    t.mainloop()


# ---------------- 后台快捷键 / 自启 ----------------
MUTEX = "Suiji_hotkey_daemon_v1"


def self_cmd(*args):
    """启动自己的命令行：exe 用自己，脚本用 pythonw"""
    if FROZEN:
        return [sys.executable] + list(args)
    pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.exists(pyw):
        pyw = sys.executable
    return [pyw, os.path.abspath(__file__)] + list(args)


def daemon_running():
    import ctypes
    k32 = ctypes.windll.kernel32
    h = k32.OpenMutexW(0x00100000, False, MUTEX)   # SYNCHRONIZE
    if h:
        k32.CloseHandle(h)
        return True
    return False


def start_daemon():
    import subprocess
    if not daemon_running():
        subprocess.Popen(self_cmd("--daemon"), close_fds=True)


def set_autostart(on=True):
    import winreg
    import subprocess
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
    try:
        if on:
            winreg.SetValueEx(key, APP, 0, winreg.REG_SZ, subprocess.list2cmdline(self_cmd("--daemon")))
        else:
            try:
                winreg.DeleteValue(key, APP)
            except FileNotFoundError:
                pass
    finally:
        winreg.CloseKey(key)


def daemon():
    """后台常驻：注册全局快捷键 Ctrl+Alt+J，按下就弹出输入框"""
    import ctypes
    import subprocess
    import traceback
    from ctypes import wintypes
    try:
        k32, u32 = ctypes.windll.kernel32, ctypes.windll.user32
        k32.CreateMutexW(None, False, MUTEX)
        if k32.GetLastError() == 183:
            return
        log("daemon.log", "启动 v%s %s" % (VERSION, " ".join(self_cmd())))
        ok = u32.RegisterHotKey(None, 1, 0x2 | 0x1 | 0x4000, 0x4A)   # Ctrl+Alt+J，不重复触发
        log("daemon.log", "注册 Ctrl+Alt+J 结果=%s 错误码=%s" % (ok, k32.GetLastError()))
        if not ok:
            u32.MessageBoxW(None, "Ctrl+Alt+J 被别的软件占用了，随手记快捷键没注册上。\n"
                                  "请关闭占用它的软件后重新运行 Suiji。", "随手记", 0x30)
            return
        msg = wintypes.MSG()
        while u32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == 0x0312:
                subprocess.Popen(self_cmd(), close_fds=True)
    except Exception:
        log("daemon.log", "出错：" + traceback.format_exc())


def first_run_setup():
    """双击运行时：确保选了文件夹、开机自启、后台在跑。返回 True 表示可以继续弹窗"""
    from tkinter import messagebox
    import tkinter as tk
    first = note_dir() is None
    if first and not choose_folder():
        return False
    try:
        set_autostart(True)
    except Exception as e:
        log("daemon.log", "设置开机自启失败：%s" % e)
    running = daemon_running()
    start_daemon()
    if first or not running:
        r = tk.Tk()
        r.withdraw()
        r.attributes("-topmost", True)
        messagebox.showinfo("随手记", "已就绪！\n\n以后在任何窗口按 Ctrl+Alt+J 就能随手记。\n"
                            "文字、截图、文件都能存，Enter 保存。\n\n保存位置：%s" % note_dir(), parent=r)
        r.destroy()
        return False
    return True


def main():
    args = sys.argv[1:]
    if args == ["--daemon"]:
        daemon()
        return
    if args == ["--uninstall"]:
        set_autostart(False)
        print("已取消开机自启。后台进程可在任务管理器结束，或重启电脑后不再运行。")
        return
    if args == ["--folder"]:
        print("保存文件夹：%s" % choose_folder())
        return
    if args == ["--version"]:
        print(VERSION)
        return
    if args == ["--merge"]:
        print("已并入 %d 条" % merge_inbox())
        return
    if args == ["--stdin"]:
        data = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        merge_inbox()
        path = append(data)
        print("已存 → " + path if path else "没存上：内容为空")
        return
    if args:
        merge_inbox()
        path = append(" ".join(args))
        print("已存 → " + path if path else "没存上：内容为空")
        return
    # 无参数：由快捷键调起时直接弹窗；双击运行时先做一次初始化检查
    if note_dir() is None or not daemon_running():
        if not first_run_setup():
            return
    popup()


if __name__ == "__main__":
    main()
