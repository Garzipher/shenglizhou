"""Build only resume-gdry.html and its own stylesheet/fonts."""
from pathlib import Path
from html import escape
import argparse
import hashlib
import json
import re
import sys
from lxml import html

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
ASSETS = SITE / 'variants/gdry'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def bullets(values):
    result = []
    for text, emphasis in values:
        assert emphasis in text
        before, _, after = text.partition(emphasis)
        result.append('<li>' + escape(before) + '<strong>' + escape(emphasis) + '</strong>' + escape(after) + '</li>')
    return '<ul class="resume-bullets">' + ''.join(result) + '</ul>'


def replace_body(element, markup):
    for child in list(element):
        element.remove(child)
    element.text = None
    for child in html.fragments_fromstring(markup):
        element.append(child)


def build(font_dir, font_deps):
    if font_deps:
        sys.path.insert(0, str(font_deps))
    from fontTools import subset
    from fontTools.ttLib import TTFont
    profile = json.loads((ROOT / 'gdry/profile.json').read_text(encoding='utf-8'))
    document = html.fromstring((SITE / 'resume.html').read_bytes())
    sheet = document.xpath('//div[@class="resume-sheet"]')[0]
    sections = sheet.xpath('./section')
    assert len(sections) == 4
    work = ''
    for job in profile['work']:
        work += '<div class="resume-entry"><div class="resume-entry-row"><strong>' + escape(job['company']) + '</strong>'
        work += '<span class="resume-role">' + escape(job['role']) + '</span><time>' + escape(job['start'] + ' – ' + job['end']) + '</time></div>'
        work += bullets(job['bullets']) + '</div>'
    replace_body(sections[1], '<h2>工作经历</h2>' + work)
    project = profile['project']
    body = '<h2>项目经历</h2><div class="resume-entry"><div class="resume-entry-row resume-project-row"><strong>' + escape(project['name']) + '</strong>'
    body += '<span class="resume-role">' + escape(project['role']) + '</span></div><p class="resume-technologies">' + escape(project['skills']) + '</p>'
    body += bullets(project['bullets']) + '</div>'
    replace_body(sections[2], body)
    skills = '<h2>专业技能</h2><ul class="resume-bullets resume-skills">'
    for label, value in profile['skills']:
        skills += '<li><strong>' + escape(label) + '：</strong>' + escape(value) + '</li>'
    replace_body(sections[3], skills + '</ul>')
    sheet.insert(1, html.fromstring('<p class="resume-gdry-summary">' + escape(profile['summary']) + '</p>'))
    downloads = []
    for label, filename in [('PDF', 'Zhou_Shengli_Resume_GDRY.pdf'), ('Word', 'Zhou_Shengli_Resume_GDRY.docx')]:
        path = ASSETS / filename
        href = 'variants/gdry/' + filename
        if path.exists():
            href += '?v=' + digest(path)
        downloads.append('<a class="resume-download" href="' + href + '" download="周圣力_个人简历_GDRY.' + path.suffix[1:] + '">下载简历（' + label + '）</a>')
    replace_body(document.xpath('//div[@class="resume-actions"]')[0], ''.join(downloads))
    for switch in document.xpath('//a[contains(@class,"language-switch")]'):
        switch.getparent().remove(switch)
    for link in document.xpath('//link[@rel="alternate"]'):
        link.getparent().remove(link)
    for script in document.xpath('//script[contains(@src,"fast-navigation.js")]'):
        script.getparent().remove(script)
    for link in document.xpath('//a[@href="resume.html" and @aria-current="page"]'):
        link.set('href', 'resume-gdry.html')
    document.get_element_by_id('main').set('data-page', 'resume')
    document.get_element_by_id('main').set('data-variant', 'gdry')
    document.find('head/title').text = '周圣力 - 项目管理与实施交付方向简历'
    document.xpath('//meta[@name="description"]')[0].set('content', profile['summary'])
    ASSETS.mkdir(parents=True, exist_ok=True)
    required = set(ord(char) for char in document.text_content() if not char.isspace()) | set(range(32, 127))
    for filename in ['regular', 'semibold']:
        existing = ASSETS / ('resume-serif-' + filename + '.woff2')
        if existing.exists() and required <= set(TTFont(existing).getBestCmap()):
            continue
        font = TTFont(font_dir / (filename + '.ttf'), recalcTimestamp=False)
        assert required <= set(font.getBestCmap()), filename + ': missing source glyphs'
        sub = subset.Subsetter(options=subset.Options())
        sub.populate(unicodes=required)
        sub.subset(font)
        font.flavor = 'woff2'
        font.save(ASSETS / ('resume-serif-' + filename + '.woff2'))
    icon = SITE / 'assets/fonts/resume-icons.woff2'
    (ASSETS / icon.name).write_bytes(icon.read_bytes())
    css = (SITE / 'assets/css/site.css').read_text(encoding='utf-8')
    for filename in ['resume-icons.woff2', 'resume-serif-regular.woff2', 'resume-serif-semibold.woff2']:
        css = re.sub(r'\.\./fonts/' + re.escape(filename) + r'(?:\?[^\)\"\x27]*)?', filename + '?v=' + digest(ASSETS / filename), css)
    css += '.resume-sheet .resume-gdry-summary{margin:0 0 14px;font-size:inherit;line-height:inherit;color:var(--resume-ink);}\n'
    css += '@media(min-width:46.876em){.resume-sheet .resume-header-with-photo{min-height:106px;}}\n'
    stylesheet = ASSETS / 'resume-gdry.css'
    stylesheet.write_bytes(css.encode('utf-8'))
    document.xpath('//link[@rel="stylesheet"]')[0].set('href', 'variants/gdry/resume-gdry.css?v=' + digest(stylesheet))
    for preload, filename in zip(document.xpath('//link[@rel="preload" and @as="font"]'), ['regular', 'semibold']):
        font = ASSETS / ('resume-serif-' + filename + '.woff2')
        preload.set('href', 'variants/gdry/' + font.name + '?v=' + digest(font))
    output = SITE / 'resume-gdry.html'
    output.write_bytes((html.tostring(document, encoding='unicode', doctype='<!doctype html>') + '\n').encode('utf-8'))
    print(json.dumps({'page': str(output), 'font_characters': len(required), 'new_assets': 4}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--font-dir', required=True, type=Path)
    parser.add_argument('--font-deps', type=Path)
    args = parser.parse_args()
    build(args.font_dir, args.font_deps)
