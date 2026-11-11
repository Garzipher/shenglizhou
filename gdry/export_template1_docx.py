"""Create the navy template Word download from the GDRY profile."""
from pathlib import Path
import json
from docx import Document
from docx.shared import Mm, Pt, RGBColor
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from io import BytesIO
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
profile = json.loads((ROOT / 'gdry/profile.json').read_text(encoding='utf-8'))
doc = Document()
s = doc.sections[0]
s.page_width, s.page_height = Mm(210), Mm(297)
s.left_margin = s.right_margin = Mm(12)
s.top_margin = Mm(14)
s.bottom_margin = Mm(14)
style = doc.styles['Normal']
style.font.name = 'Microsoft YaHei'
style._element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
style.font.size = Pt(10.5)
style.paragraph_format.space_after = Pt(0)
style.paragraph_format.line_spacing = 1.25

def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd'); shd.set(qn('w:fill'), color); tcPr.append(shd)

def para(text='', bold=False, size=None, color=None, before=0, after=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(before); p.paragraph_format.space_after = Pt(after)
    run = p.add_run(text); run.bold = bold
    if size: run.font.size = Pt(size)
    if color: run.font.color.rgb = RGBColor.from_string(color)
    return p

def heading(text):
    p=para('●  '+text,True,10,'22374A',before=5,after=3)
    p.paragraph_format.keep_with_next = True
    if text == '项目经历':
        p.paragraph_format.page_break_before = True
    pPr=p._p.get_or_add_pPr(); borders=OxmlElement('w:pBdr'); bottom=OxmlElement('w:bottom')
    for k,v in {'val':'single','sz':'5','space':'3','color':'22374A'}.items(): bottom.set(qn('w:'+k),v)
    borders.append(bottom);pPr.append(borders)

def bullet(text, emphasis):
    p=doc.add_paragraph(); p.paragraph_format.left_indent=Mm(4); p.paragraph_format.first_line_indent=Mm(-3)
    p.add_run('•  ')
    before,_,after=text.partition(emphasis)
    p.add_run(before);p.add_run(emphasis).bold=True;p.add_run(after)

table=doc.add_table(rows=1, cols=2)
table.autofit=False;table.columns[0].width=Mm(31);table.columns[1].width=Mm(155)
left,right=table.rows[0].cells
left.width=Mm(31);right.width=Mm(155)
for cell in (left,right):shade(cell,'22374A')
left.paragraphs[0].add_run().add_picture(str(ROOT/'site/images/resume-photo.jpg'),width=Mm(23))
p=right.paragraphs[0]; r=p.add_run('周圣力');r.bold=True;r.font.size=Pt(18);r.font.color.rgb=RGBColor(255,255,255)
for text in ['籍贯：广东阳东   ·   居住地：广东广州   ·   出生年月：2003.03','手机号码：+86 18306622399   ·   邮箱：3279533794@qq.com']:
    p=right.add_paragraph();r=p.add_run(text);r.font.color.rgb=RGBColor(255,255,255);r.font.size=Pt(8)
para(profile['summary'],before=5)
heading('教育背景')
para('（本科）岭南师范学院',True)
para('数据科学与大数据技术                                      2021.09 – 2025.07')
bullet('GPA：3.2/5','GPA：')
heading('工作经历')
for job in profile['work']:
    para(job['company']+'   |   '+job['role']+'   |   '+job['start']+' – '+job['end'],True,before=2)
    for text,emphasis in job['bullets']: bullet(text,emphasis)
heading('项目经历')
project=profile['project']
para(project['name']+'   |   '+project['role'],True)
para(project['skills'])
for text,emphasis in project['bullets']: bullet(text,emphasis)
heading('个人总结')
para('具备医疗、企业 QMS 与车载系统测试及交付经验，关注业务需求理解、功能验证与上线保障，能够结合业务场景梳理问题并跟进解决。参与个人项目需求与功能规划、UI 方案及交互验收，运用 AI 工具和自动化技术支持协作与迭代。')
heading('专业技能')
abilities = ['需求理解与业务沟通', '功能规划与方案梳理', '交互验收与问题跟进', '上线保障与交付验证']
ability_table=doc.add_table(rows=0,cols=2); ability_table.autofit=False
ability_table.columns[0].width=Mm(90);ability_table.columns[1].width=Mm(90)
for index in range(0,len(abilities),2):
    cells=ability_table.add_row().cells
    for offset,(cell,label) in enumerate(zip(cells,abilities[index:index+2])):
        p=cell.paragraphs[0];p.paragraph_format.space_after=Pt(6)
        p.add_run(label+'  ').font.size=Pt(9)
        width=[78,72,84,80][index+offset]
        graphic=Image.new('RGB',(200,18),'#e3e6e8'); ImageDraw.Draw(graphic).polygon([(0,0),(width*2-10,0),(width*2,18),(0,18)],fill='#263d50')
        data=BytesIO();graphic.save(data,format='PNG');data.seek(0)
        p.add_run().add_picture(data,width=Mm(22))
para('AI 与技术工具：Codex Agent、Skill、Python、Pytest、Midscene、Apifox、SQL / MySQL、Linux、Git、Jenkins',before=4)
para('语言能力：英语四级')
target=ROOT/'site/variants/gdry/Zhou_Shengli_Resume_GDRY_Template1.docx'
doc.save(target)
print(target)
