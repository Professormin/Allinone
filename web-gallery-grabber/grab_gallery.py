#!/usr/bin/env python3
"""网页图库一键存图：读一个网页里的全部图片，下载原图，按图片说明文字命名，并输出清单。

只用 Python 标准库。用法：
    python grab_gallery.py <网页地址> <保存文件夹> [--names 命名对照.csv] [--only /gallery/] [--min-kb 15]

命名规则（按优先级）：
  1. --names 对照表里有的：用表里的新名字（两列：原说明文字,新文件名）
  2. 图片的 alt / title / 图注文字
  3. 原文件名
同名的第二张自动加 _2、_3。默认跳过 gif 动图和 logo / icon / loader 之类的网站装饰图。输出：保存文件夹里的 00_清单.csv（序号、名字、原图链接、来源页、状态）。
"""
import argparse, csv, os, re, sys, time, urllib.parse, urllib.request
from html.parser import HTMLParser

UA = {"User-Agent": "Mozilla/5.0 (gallery-grabber; personal reference use)"}
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif")
SKIP = r"logo|loader|icon|avatar|sprite|placeholder|spinner|banner"


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items, self._a = [], None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a":
            self._a = a.get("href", "")
        elif tag == "img":
            src = a.get("data-src") or a.get("data-lazy-src") or a.get("src") or ""
            name = (a.get("alt") or a.get("title") or "").strip()
            link = self._a if self._a and self._a.lower().split("?")[0].endswith(IMG_EXT) else ""
            self.items.append({"name": name, "src": link or src})

    def handle_endtag(self, tag):
        if tag == "a":
            self._a = None


def clean(name):
    name = re.sub(r"\s+", " ", name).strip()
    return re.sub(r'[\\/:*?"<>|]', "-", name)[:150] or "image"


def fetch(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("outdir")
    ap.add_argument("--names", help="命名对照表 CSV：原说明文字,新文件名")
    ap.add_argument("--min-kb", type=int, default=15, help="小于这个大小的图当作图标/缩略图跳过")
    ap.add_argument("--only", help="只要原图链接里含这段文字的图，例如 /gallery/")
    args = ap.parse_args()

    mapping = {}
    if args.names:
        with open(args.names, encoding="utf-8-sig") as f:
            for row in csv.reader(f):
                if len(row) >= 2:
                    mapping[clean(row[0]).lower()] = row[1].strip()

    p = Parser()
    p.feed(fetch(args.url).decode("utf-8", "replace"))
    os.makedirs(args.outdir, exist_ok=True)
    seen, used, rows = set(), {}, []
    for it in p.items:
        src = urllib.parse.urljoin(args.url, it["src"])
        if not src.lower().split("?")[0].endswith(IMG_EXT) or src in seen:
            continue
        seen.add(src)
        low = src.lower()
        if (args.only and args.only.lower() not in low) or low.split("?")[0].endswith(".gif") or re.search(SKIP, low):
            continue
        raw = clean(it["name"]) if it["name"] else clean(urllib.parse.unquote(os.path.splitext(os.path.basename(src))[0]))
        base = clean(mapping.get(raw.lower(), raw))
        n = used.get(base, 0) + 1
        used[base] = n
        fname = base + ("" if n == 1 else f"_{n}") + os.path.splitext(src.split("?")[0])[1].lower()
        try:
            data = fetch(src)
            if len(data) < args.min_kb * 1024:
                status = "跳过（太小，多半是图标）"
            else:
                with open(os.path.join(args.outdir, fname), "wb") as f:
                    f.write(data)
                status = "已下载"
        except Exception as e:
            status = f"失败：{e}"
        rows.append([len(rows) + 1, fname, raw, src, args.url, status])
        print(rows[-1][0], status, fname)
    with open(os.path.join(args.outdir, "00_清单.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["序号", "保存文件名", "网页上的说明文字", "原图链接", "来源页", "状态"])
        w.writerows(rows)
    ok = sum(r[5] == "已下载" for r in rows)
    print(f"完成：{ok} 张已下载，清单在 {os.path.join(args.outdir, '00_清单.csv')}")


if __name__ == "__main__":
    sys.exit(main())
