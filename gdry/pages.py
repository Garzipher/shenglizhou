"""Build the independent Chinese GDRY page collection from its resume profile."""
from html import escape
from urllib.parse import urlsplit, urlunsplit
from lxml import html

ROUTES = {
    '首页': 'index-gdry.html',
    '关于': 'about-gdry.html',
    '技能': 'skills-gdry.html',
    '项目': 'projects-gdry.html',
    '经历': 'career-gdry.html',
    '简历': 'resume-gdry.html',
}


def fill(element, markup):
    for child in list(element):
        element.remove(child)
    element.text = None
    for child in html.fragments_fromstring(markup):
        element.append(child)


def emphasized(text, phrase):
    assert phrase in text
    before, _, after = text.partition(phrase)
    return escape(before) + '<strong>' + escape(phrase) + '</strong>' + escape(after)


def prepare(document, filename, description):
    document.find('body').set('data-variant', 'gdry')
    button = document.xpath('//nav[@id="site-nav"]/button')[0]
    button.set('class', 'hidden')
    button.set('aria-expanded', 'false')
    mapping = {key + '.html': key + '-gdry.html'
               for key in ['index', 'skills', 'projects', 'career', 'resume']}
    for node in document.xpath('//a[@href]'):
        value = urlsplit(node.get('href'))
        if not value.scheme and not value.netloc and value.path in mapping:
            node.set('href', urlunsplit(('', '', mapping[value.path], value.query, value.fragment)))
    for node in document.xpath('//nav//a'):
        label = ''.join(node.itertext()).strip()
        if label in ROUTES:
            node.set('href', ROUTES[label])
            node.attrib.pop('aria-current', None)
            if ROUTES[label] == filename:
                node.set('aria-current', 'page')
    for node in document.xpath('//a[contains(@class,"language-switch")] | //link[@rel="alternate"] | //script[contains(@src,"fast-navigation.js")]'):
        node.getparent().remove(node)
    main = document.get_element_by_id('main')
    main.set('data-variant', 'gdry')
    main.set('data-page', filename.removesuffix('-gdry.html'))
    label = next(label for label, route in ROUTES.items() if route == filename)
    document.find('head/title').text = '周圣力 - ' + label + ' | GDRY'
    if filename == 'resume-gdry.html':
        document.find('head/title').text = '周圣力 - 项目管理与实施交付方向简历'
    document.xpath('//meta[@name="description"]')[0].set('content', description)
    return document


def build_pages(site, profile, resume_document):
    def template(name):
        return html.fromstring((site / (name + '.html')).read_bytes())
    def content(document):
        return document.xpath('//section[@class="page-content"]')[0]
    documents = {'resume-gdry.html': resume_document}

    home = template('index')
    section = content(home)
    intro = section.xpath('./p')
    intro[0].text = '周圣力，毕业于岭南师范学院数据科学与大数据技术专业。' + profile['summary']
    intro[1].text = '工作中围绕业务流程开展需求评审、测试设计、版本回归和问题跟进，配合实施团队验证医院上线与私有化交付结果。'
    intro[2].text = '个人项目 RainSoul 从自己的长篇写作需求出发，负责需求拆分、UI 方案和验收要求，通过 Codex Agent 推进实现，并跟进 Git 版本迭代与问题修复。'
    documents['index-gdry.html'] = home

    about = template('index')
    fill(content(about), '<h1>关于我</h1><p>' + escape(intro[0].text) + '</p>'
         + '<h1>工作方式</h1><p>' + escape(intro[1].text) + '</p>'
         + '<p>使用 Codex Agent 配置、迭代测试 Skill，统一用例、缺陷证据与输出模板，并复核结果；结合自动化脚本完成业务回归与接口验证。</p>'
         + '<h1>个人项目</h1><p>' + escape(intro[2].text) + '</p>'
         + '<p><a href="career-gdry.html">查看工作经历</a> · <a href="projects-gdry.html">查看项目经历</a> · <a href="resume-gdry.html">查看完整简历</a></p>')
    documents['about-gdry.html'] = about

    career = template('career')
    headers = content(career).xpath('./ul[contains(@class,"date-ul")]')
    assert len(headers) == len(profile['work'])
    section = content(career)
    for child in list(section):
        section.remove(child)
    section.text = None
    for header, job in zip(headers, profile['work']):
        title = header.xpath('.//div[@class="content-div"]/strong')[0]
        title.text = job['role'] + '，' + job['company']
        section.append(header)
        points = html.fromstring('<ul>' + ''.join('<li>' + emphasized(*item) + '</li>' for item in job['bullets']) + '</ul>')
        section.append(points)
    documents['career-gdry.html'] = career

    skills = template('skills')
    groups = [
        ('业务与交付', '业务流程梳理、需求评审、交付验证、版本回归及问题跟进。'),
        ('迭代验证', '测试方案与数据准备、业务场景与用例设计、缺陷复现与复测、版本公告及热修复跟进。'),
        ('接口与数据', 'Apifox、SQL / MySQL；接口验证、业务结果核对及基础并发验证。'),
        ('自动化与 AI 应用', 'Python、Pytest、Playwright、Allure、Midscene；Codex Agent、测试 Skill 配置、用例及缺陷证据模板。'),
        ('系统与设备', 'Linux、Git、Jenkins、uiautomator2、ADB、CAN、ZCANPRO；嵌入式验证与台架压测。'),
    ]
    fill(content(skills), '<h1 id="technical-skills">专业技能</h1><ul>'
         + ''.join('<li><strong>' + escape(label) + '：</strong>' + escape(text) + '</li>' for label, text in groups)
         + '</ul><h1 id="language">语言能力</h1><ul><li>' + escape(profile['skills'][1][1]) + '</li></ul>')
    documents['skills-gdry.html'] = skills

    projects = template('projects')
    project = profile['project']
    blocks = ''
    for title, item in zip(['项目背景', '开发协作与验收', '数据与安全'], project['bullets']):
        blocks += '<div style="margin-left:15px;margin-bottom:10px;"><strong style="color:#0077b6;">' + title + '</strong><p style="margin:5px 0 10px 10px;">' + emphasized(*item) + '</p></div>'
    fill(content(projects), '<ul class="date-ul"><li style="line-height:1.8;"><div style="margin-bottom:15px;"><strong style="font-size:1.1rem;color:#023e8a;">'
         + escape(project['name']) + '</strong></div><div class="project-skills" style="color:#555;margin-bottom:15px;">'
         + escape(project['skills']) + '</div>' + blocks + '</li></ul>')
    documents['projects-gdry.html'] = projects
    return {filename: prepare(document, filename, profile['summary']) for filename, document in documents.items()}
