"""Build a source-paired teacher preparation DOCX from reviewed JSON."""
import argparse
import json
from copy import deepcopy
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt


def build(input_path, template, output):
    input_path, output = map(Path, (input_path, output))
    template = Path(template) if template else None
    if output.exists():
        raise FileExistsError(f'Refusing to overwrite: {output}')
    data = json.loads(input_path.read_text(encoding='utf-8-sig'))
    if not data.get('title') or not data.get('intro') or not data.get('slides'):
        raise ValueError('title, intro, and slides are required')

    def image_path(value):
        path = Path(value)
        path = path if path.is_absolute() else input_path.parent / path
        if not path.is_file():
            raise FileNotFoundError(path)
        return path

    for item in data['intro']:
        if not item.get('heading') or not item.get('paragraphs'):
            raise ValueError('Each intro needs heading and paragraphs')
        if item.get('image'):
            image_path(item['image'])
    for index, slide in enumerate(data['slides'], 1):
        for key in ('title', 'image', 'section', 'depth', 'meaning', 'method', 'caution'):
            if not slide.get(key):
                raise ValueError(f'Slide {index} missing {key}')
        image_path(slide['image'])
        if not slide.get('sources') and not slide.get('source_note'):
            raise ValueError(f'Slide {index} needs sources or source_note')
        for source in slide.get('sources', []):
            if not source.get('label'):
                raise ValueError(f'Slide {index} source missing label')
            image_path(source['image'])

    doc = Document(template) if template else Document()
    if not template:
        doc.styles['Normal'].font.size = Pt(11)
    section = deepcopy(doc.sections[0]._sectPr)
    for element in list(doc._element.body):
        doc._element.body.remove(element)
    doc._element.body.append(section)
    # Remove inherited lesson-specific running headings from the new document.
    for part in (doc.sections[0].header, doc.sections[0].footer,
                 doc.sections[0].first_page_header, doc.sections[0].first_page_footer,
                 doc.sections[0].even_page_header, doc.sections[0].even_page_footer):
        for element in list(part._element):
            part._element.remove(element)
        part.add_paragraph('')
    usable = doc.sections[0].page_width - doc.sections[0].left_margin - doc.sections[0].right_margin

    def paragraph(label, value):
        p = doc.add_paragraph()
        p.add_run(label + '：').bold = True
        p.add_run(value)

    doc.add_heading(data['title'], 0)
    doc.add_paragraph(data.get('subtitle', '教师用，勿发学生'))
    doc.add_heading('一、开课前先讲顺', 1)
    for item in data['intro']:
        doc.add_heading(item['heading'], 2)
        for value in item['paragraphs']:
            doc.add_paragraph(value)
        if item.get('image'):
            doc.add_picture(str(image_path(item['image'])), width=int(usable * .85))
    if data.get('pronunciation'):
        doc.add_heading('读音备注', 2)
        table = doc.add_table(rows=0, cols=2)
        for label, meaning in data['pronunciation']:
            cells = table.add_row().cells
            cells[0].text, cells[1].text = label, meaning
    for index, slide in enumerate(data['slides'], 1):
        doc.add_page_break()
        if index == 1:
            doc.add_heading('二、对着课件备课', 1)
        doc.add_heading(f'第 {index} 页 · {slide["title"]}', 2)
        table = doc.add_table(rows=1, cols=2)
        table.autofit = False
        for column in table.columns:
            column.width = int(usable / 2)
        left, right = table.rows[0].cells
        left.paragraphs[0].add_run('本次课件').bold = True
        left.add_paragraph().add_run().add_picture(str(image_path(slide['image'])), width=int(usable / 2 - Inches(.15)))
        if slide.get('source_note'):
            right.add_paragraph(slide['source_note'])
        for source in slide.get('sources', []):
            right.add_paragraph(source['label'])
            right.add_paragraph().add_run().add_picture(str(image_path(source['image'])), width=int(usable / 2 - Inches(.15)))
        for label, key in [('对应章节', 'section'), ('讲到', 'depth'), ('这页在说', 'meaning'), ('讲法', 'method'), ('注意', 'caution'), ('答案', 'answer')]:
            if slide.get(key):
                paragraph(label, slide[key])
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)
    return len(data['slides'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--template')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(f'Created {args.output}; slide entries: {build(args.input, args.template, args.output)}')
