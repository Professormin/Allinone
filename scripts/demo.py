"""Create an original two-slide mathematics example and teacher DOCX."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from build_prep import build


def create_demo(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    font = ImageFont.load_default(size=24)
    for index, slope in enumerate((1, 2), 1):
        image = Image.new('RGB', (1200, 675), '#FFF0E2')
        draw = ImageDraw.Draw(image)
        draw.text((55, 30), f'Linear functions: y = {slope}x + 1', fill='#332A29', font=font)
        origin = (330, 420)
        def point(x, y):
            return (origin[0] + 75*x, origin[1] - 75*y)
        draw.line([point(-3, 0), point(3.5, 0)], fill='#332A29', width=3)
        draw.line([point(0, -2.5), point(0, 4)], fill='#332A29', width=3)
        draw.text(point(3.5, 0), 'x', fill='#332A29', font=font)
        draw.text(point(0, 4.4), 'y', fill='#332A29', font=font)
        for x in range(-3, 4):
            px, py = point(x, 0)
            draw.line([(px, py-5), (px, py+5)], fill='#332A29', width=2)
            draw.text((px-5, py+10), str(x), fill='#332A29', font=font)
        xmin, xmax = max(-3, -3/slope), min(3, 3/slope)
        draw.line([point(xmin, slope*xmin+1), point(xmax, slope*xmax+1)], fill='#3D6FB5', width=5)
        for x in (0, 1):
            px, py = point(x, slope*x+1)
            draw.ellipse((px-7, py-7, px+7, py+7), fill='#C8372D')
            draw.text((px+12, py), f'({x}, {slope*x+1})', fill='#C8372D', font=font)
        draw.text((710, 220), 'When x increases by 1,', fill='#332A29', font=font)
        draw.text((710, 270), f'y increases by {slope}.', fill='#332A29', font=font)
        image.save(output / f'slide-{index}.png')
    data = {
        'title': '一次函数：教师备课示例',
        'subtitle': '演示材料 · 两页图解条目，并非完整课件',
        'intro': [{'heading': '从变化量理解斜率', 'paragraphs': ['先比较两点的横纵坐标变化，再引入斜率。一次函数 y=kx+b 中，k 表示 x 每增加1时 y 的变化量。'], 'image': 'slide-1.png'}],
        'slides': []
    }
    for index, slope in enumerate((1, 2), 1):
        data['slides'].append(dict(title=f'y={slope}x+1', image=f'slide-{index}.png', source_note='原创教学示意；知识依据为一次函数定义 y=kx+b。', section='一次函数与斜率', depth='能由两点说明斜率', meaning=f'x 增加1，y 增加{slope}。', method=f'标出(0,1)与(1,{slope+1})，比较坐标差。', caution='图中横纵坐标采用相同单位长度；截距不是斜率。', answer=f'k=({slope+1}−1)/(1−0)={slope}。'))
    manifest = output / 'prep.json'
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    build(manifest, None, output / 'teacher.docx')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    print(create_demo(parser.parse_args().output))
