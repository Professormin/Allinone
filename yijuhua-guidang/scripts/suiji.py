#!/usr/bin/env python3
"""随手记：一句话即归档。只用 Python 标准库，Windows / macOS / Linux 通用，任何能跑命令的 AI 都能调用。

用法
  python suiji.py "要存的一句话"                 追加到 <根目录>/00_随手记/YYYY-MM.md
  python suiji.py --title 主题 --dir 子文件夹 "长内容"   单独存成 <根目录>/<子文件夹>/YYYY-MM-DD_主题.md
  echo 内容 | python suiji.py -                  从标准输入读（适合多行、带引号的内容）
  python suiji.py --inbox                        把 00_随手记/_收件箱/ 里的 .txt/.md 全部并入月文件
根目录：--root 参数 > 环境变量 SUIJI_ROOT >没设就用本脚本所在 tools 文件夹的上一级。
收件箱：环境变量 SUIJI_INBOX（比如 iCloud / OneDrive 同步到电脑的文件夹）；没设就用 00_随手记/_收件箱。
成功时最后一行打印 OK <文件完整路径>；失败打印 FAIL <原因> 并返回非 0。
"""
import argparse, datetime as dt, os, re, shutil, sys
from pathlib import Path

TZ = dt.timezone(dt.timedelta(hours=8))  # 北京时间


def root() -> Path:
    env = os.environ.get("SUIJI_ROOT")
    return Path(env) if env else Path(__file__).resolve().parent.parent.parent


def month_file(r: Path, now: dt.datetime) -> Path:
    p = r / "00_随手记" / f"{now:%Y-%m}.md"
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"---\ntags: [随手记]\n---\n# 随手记 {now:%Y-%m}\n\n", encoding="utf-8")
    return p


def append_line(text: str, now: dt.datetime, src: str = "") -> Path:
    p = month_file(root(), now)
    body = text.strip().replace("\r\n", "\n").replace("\n", "<br>")
    tag = f"（{src}）" if src else ""
    line = f"- {now:%m-%d %H:%M}{tag} {body}\n"
    with p.open("a", encoding="utf-8") as f:
        f.write(line)
    if line not in p.read_text(encoding="utf-8"):
        raise OSError("写入后回读没找到这一条")
    return p


def save_note(text: str, title: str, sub: str, now: dt.datetime) -> Path:
    safe = re.sub(r'[\\/:*?"<>|#\s]+', "_", title).strip("_") or "未命名"
    d = root() / sub
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{now:%Y-%m-%d}_{safe}.md"
    n = 2
    while p.exists():
        p = d / f"{now:%Y-%m-%d}_{safe}_{n}.md"; n += 1
    p.write_text(f"---\n存档日期: {now:%Y-%m-%d}\ntags: [随手记]\n---\n# {title}\n\n{text.strip()}\n", encoding="utf-8")
    if p.stat().st_size == 0:
        raise OSError("文件是空的")
    return p


def inbox(now: dt.datetime) -> list:
    box = Path(os.environ["SUIJI_INBOX"]) if os.environ.get("SUIJI_INBOX") else root() / "00_随手记" / "_收件箱"
    done = root() / "00_随手记" / "_收件箱" / "_已并入"
    box.mkdir(parents=True, exist_ok=True)
    out = []
    for f in sorted(box.iterdir()):
        if f.is_file() and f.suffix.lower() in (".txt", ".md"):
            t = f.read_text(encoding="utf-8", errors="replace").strip()
            if t:
                when = dt.datetime.fromtimestamp(f.stat().st_mtime, TZ)
                out.append(append_line(t, when, "收件箱"))
            done.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), str(done / f.name))
    return out


def read_stdin() -> str:
    raw = sys.stdin.buffer.read()
    for enc in ("utf-8-sig", "gbk"):  # Windows 管道常见 GBK
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="随手记：一句话即归档")
    ap.add_argument("text", nargs="?", help="要存的内容；用 - 表示从标准输入读")
    ap.add_argument("--title", help="有主题的长内容：单独存一个文件")
    ap.add_argument("--dir", default="00_随手记", help="单独存文件时放进哪个子文件夹（相对根目录）")
    ap.add_argument("--root", help="笔记库根目录（优先级最高）")
    ap.add_argument("--inbox", action="store_true", help="合并 _收件箱 里的文件")
    a = ap.parse_args()
    if a.root:
        os.environ["SUIJI_ROOT"] = a.root
    now = dt.datetime.now(TZ)
    try:
        if a.inbox:
            got = inbox(now)
            print(f"OK 收件箱并入 {len(got)} 条" + (f" → {got[-1]}" if got else ""))
            return 0
        text = read_stdin() if a.text in (None, "-") else a.text
        if not text or not text.strip():
            print("FAIL 内容是空的"); return 2
        p = save_note(text, a.title, a.dir, now) if a.title else append_line(text, now)
        print(f"OK {p}")
        return 0
    except Exception as e:  # 存不上必须明说
        print(f"FAIL {e}"); return 1


if __name__ == "__main__":
    sys.exit(main())
