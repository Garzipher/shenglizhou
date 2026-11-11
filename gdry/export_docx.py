"""Create the GDRY Word download without modifying the original DOCX."""
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
import argparse
import hashlib
import json
import sys
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}

def tag(name):
    return '{' + W + '}' + name

def paragraph(template, text, emphasis=None, bullet=False):
    p = deepcopy(template)
    props = p.find(tag('pPr'))
    run_props = deepcopy(template.find(tag('r')).find(tag('rPr')))
    for child in list(p):
        if child is not props:
            p.remove(child)
    def run(value, bold=False):
        r = etree.SubElement(p, tag('r'))
        rp = deepcopy(run_props)
        b = rp.find(tag('b'))
        if b is None:
            b = etree.SubElement(rp, tag('b'))
        b.set(tag('val'), '1' if bold else '0')
        r.append(rp)
        parts = value.split('\t')
        for i, part in enumerate(parts):
            if i:
                etree.SubElement(r, tag('tab'))
            if part:
                t = etree.SubElement(r, tag('t'))
                t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                t.text = part
    if bullet:
        run('•\t')
    if emphasis:
        assert emphasis in text
        before, _, after = text.partition(emphasis)
        run(before)
        run(emphasis, True)
        run(after)
    else:
        run(text)
    return p

def build(font_dir, font_deps=None):
    if font_deps:
        sys.path.insert(0, str(font_deps))
    from fontTools import subset
    from fontTools.ttLib import TTFont
    source = ROOT / 'site/files/Zhou_Shengli_Resume.docx'
    target = ROOT / 'site/variants/gdry/Zhou_Shengli_Resume_GDRY.docx'
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    profile = json.loads((ROOT / 'gdry/profile.json').read_text(encoding='utf-8'))
    with ZipFile(source) as z:
        tree = etree.fromstring(z.read('word/document.xml'))
        body = tree.find(tag('body'))
        # Keep the compact template on one page after adding the platform entry.
        margins = body.find(tag('sectPr')).find(tag('pgMar'))
        margins.set(tag('bottom'), '300')
        ps = body.findall(tag('p'))
        assert len(ps) == 27 and ''.join(ps[0].itertext()).startswith('周圣力')
        replacements = [deepcopy(p) for p in ps[:3]]
        summary = paragraph(ps[9], profile['summary'])
        pr = summary.find(tag('pPr'))
        for name in ['tabs', 'ind']:
            item = pr.find(tag(name))
            if item is not None:
                pr.remove(item)
        spacing = pr.find(tag('spacing'))
        spacing.set(tag('before'), '280')
        spacing.set(tag('after'), '0')
        replacements.append(summary)
        education = [deepcopy(p) for p in ps[3:7]]
        education[0].find(tag('pPr')).find(tag('spacing')).set(tag('before'), '180')
        replacements.extend(education)
        replacements.append(deepcopy(ps[7]))
        for i, job in enumerate(profile['work']):
            replacements.append(deepcopy(ps[[8, 11, 15][i]]))
            for j, (text, bold) in enumerate(job['bullets']):
                replacements.append(paragraph(ps[9 if j == 0 else 10], text, bold, True))
        replacements.append(deepcopy(ps[18]))
        replacements.append(deepcopy(ps[19]))
        replacements.append(paragraph(ps[20], profile['project']['skills']))
        for i, (text, bold) in enumerate(profile['project']['bullets']):
            replacements.append(paragraph(ps[21 if i == 0 else 22], text, bold, True))
        replacements.append(paragraph(ps[24], '专业技能', '专业技能'))
        for i, (label, text) in enumerate(profile['skills']):
            replacements.append(paragraph(ps[25 if i == 0 else 26], label + '：' + text, label + '：', True))
        for p in ps:
            body.remove(p)
        for i, p in enumerate(replacements):
            body.insert(i, p)
        contents = etree.tostring(tree, encoding='UTF-8', xml_declaration=True, standalone=True)
        required = {ord(c) for text in tree.xpath('//w:t/text()', namespaces=NS) for c in text if not c.isspace()} | set(range(32, 127))
        font_table = etree.fromstring(z.read('word/fontTable.xml'))
        font_parts = {}
        for role, filename in [('Regular', 'regular'), ('Bold', 'semibold')]:
            entry = font_table.xpath('//w:font[@w:name="Noto Serif SC"]/w:embed' + role, namespaces=NS)[0]
            key = bytes.fromhex(entry.get(tag('fontKey')).strip('{}').replace('-', ''))[::-1]
            font = TTFont(font_dir / (filename + '.ttf'), recalcTimestamp=False)
            assert required <= set(font.getBestCmap())
            sub = subset.Subsetter(options=subset.Options())
            sub.populate(unicodes=required)
            sub.subset(font)
            assert required <= set(font.getBestCmap())
            output = BytesIO()
            font.save(output)
            data = bytearray(output.getvalue())
            for i in range(32):
                data[i] ^= key[i % 16]
            font_parts['word/fonts/resume-' + filename + '.odttf'] = bytes(data)
        target.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(target, 'w') as out:
            for entry in z.infolist():
                replacement = contents if entry.filename == 'word/document.xml' else font_parts.get(entry.filename)
                out.writestr(entry, replacement if replacement is not None else z.read(entry.filename))
    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
    with ZipFile(source) as before, ZipFile(target) as after:
        assert before.namelist() == after.namelist()
        preserved = [name for name in before.namelist() if name != 'word/document.xml' and name not in font_parts]
        assert all(before.read(name) == after.read(name) for name in preserved)
    print(json.dumps({'word': str(target), 'preserved_package_parts': len(preserved), 'original_unchanged': True}, ensure_ascii=False))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--font-dir', required=True, type=Path)
    parser.add_argument('--font-deps', type=Path)
    args = parser.parse_args()
    build(args.font_dir, args.font_deps)
