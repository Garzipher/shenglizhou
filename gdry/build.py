"""Build independent GDRY pages and their own stylesheet/fonts."""
from pathlib import Path
from html import escape
import argparse
import hashlib
import json
import re
import sys
from lxml import html
from pages import build_pages

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
    skills = '<h2>专业技能</h2><div class="template-one-abilities">'
    for label, width in [('需求理解与业务沟通', 78), ('功能规划与方案梳理', 72), ('交互验收与问题跟进', 84), ('上线保障与交付验证', 80)]:
        skills += '<div class="ability-row"><span>' + escape(label) + '</span><i aria-hidden="true" style="--fill:' + str(width) + '%"></i></div>'
    skills += '<p class="ability-tools"><strong>AI 与技术工具：</strong>Codex Agent、Skill、Python、Pytest、Midscene、Apifox、SQL / MySQL、Linux、Git、Jenkins<br><strong>语言能力：</strong>英语四级</p></div><ul class="resume-bullets resume-skills">'
    for label, value in profile['skills']:
        skills += '<li><strong>' + escape(label) + '：</strong>' + escape(value) + '</li>'
    replace_body(sections[3], skills + '</ul>')
    summary = '<section class="resume-section template-one-summary"><h2>个人总结</h2><p>具备医疗、企业 QMS 与车载系统测试及交付经验，关注业务需求理解、功能验证与上线保障，能够结合业务场景梳理问题并跟进解决。参与个人项目需求与功能规划、UI 方案及交互验收，运用 AI 工具和自动化技术支持协作与迭代。</p></section>'
    sheet.insert(sheet.index(sections[3]), html.fromstring(summary))
    sheet.insert(1, html.fromstring('<p class="resume-gdry-summary">' + escape(profile['summary']) + '</p>'))
    first = html.Element('div', {'class': 'resume-paper resume-paper-first'})
    second = html.Element('div', {'class': 'resume-paper resume-paper-second'})
    for node in list(sheet):
        (second if node is sections[2] or len(second) else first).append(node)
    sheet.extend([first, second])
    downloads = []
    for label, filename in [('PDF', 'Zhou_Shengli_Resume_GDRY_Template1.pdf'), ('Word', 'Zhou_Shengli_Resume_GDRY_Template1.docx')]:
        path = ASSETS / filename
        href = 'variants/gdry/' + filename
        if path.exists():
            href += '?v=' + digest(path)
        downloads.append('<a class="resume-download" href="' + href + '" download="周圣力_个人简历_GDRY.' + path.suffix[1:] + '">下载简历（' + label + '）</a>')
    selector = '<label class="template-picker">简历模板 <select id="resume-template" aria-label="选择简历模板"><option value="1">简历模板 1</option><option value="2">简历模板 2</option></select></label>'
    replace_body(document.xpath('//div[@class="resume-actions"]')[0], selector + ''.join(downloads))
    sheet.set('data-template', '1')
    script = html.Element('script', src='variants/gdry/template-switch.js?v=' + digest(ASSETS / 'template-switch.js'))
    script.set('defer', 'defer')
    document.find('body').append(script)
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
    document.find('head/title').text = '周圣力 - 项目管理与实施交付'
    document.xpath('//meta[@name="description"]')[0].set('content', profile['summary'])
    ASSETS.mkdir(parents=True, exist_ok=True)
    documents = build_pages(SITE, profile, document)
    required = {ord(char) for page in documents.values() for char in page.text_content() if not char.isspace()} | set(range(32, 127))
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
    css += 'body[data-variant="gdry"] #site-nav .masthead__menu-home-item{display:table-cell!important;}\n'
    css += (ROOT / 'gdry/template.css').read_text(encoding='utf-8')
    stylesheet = ASSETS / 'resume-gdry.css'
    stylesheet.write_bytes(css.encode('utf-8'))
    for filename, page in documents.items():
        page.xpath('//link[@rel="stylesheet"]')[0].set('href', 'variants/gdry/resume-gdry.css?v=' + digest(stylesheet))
        for preload, weight in zip(page.xpath('//link[@rel="preload" and @as="font"]'), ['regular', 'semibold']):
            font = ASSETS / ('resume-serif-' + weight + '.woff2')
            preload.set('href', 'variants/gdry/' + font.name + '?v=' + digest(font))
        output = SITE / filename
        output.write_bytes((html.tostring(page, encoding='unicode', doctype='<!doctype html>') + '\n').encode('utf-8'))
    print(json.dumps({'pages': sorted(documents), 'font_characters': len(required), 'new_assets': 4}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--font-dir', required=True, type=Path)
    parser.add_argument('--font-deps', type=Path)
    args = parser.parse_args()
    build(args.font_dir, args.font_deps)
