from pathlib import Path
import json,re,html
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parent.parent
out=ROOT/'outputs/01a1530f-f378-7fd1-9654-468c9b2141b6/FLOW_Dossier_client_2026-10-21'
for name,file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf'),('Arial-Italic','ariali.ttf')]:pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial-Italic',boldItalic='Arial-Bold')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Body',fontName='Arial',fontSize=9.4,leading=13.8,spaceAfter=8,textColor=colors.HexColor('#19344c')))
styles.add(ParagraphStyle(name='TitleClient',fontName='Arial-Bold',fontSize=23,leading=28,spaceAfter=16,textColor=colors.HexColor('#19344c')))
for name,size in [('H2',15),('H3',11.5)]:styles.add(ParagraphStyle(name=name,fontName='Arial-Bold',fontSize=size,leading=size+4,spaceBefore=12,spaceAfter=8,keepWithNext=True,textColor=colors.HexColor('#19344c')))
styles.add(ParagraphStyle(name='Cell',parent=styles['Body'],fontSize=8.3,leading=11.5,spaceAfter=0))
styles.add(ParagraphStyle(name='HeadCell',parent=styles['Cell'],textColor=colors.white,fontName='Arial-Bold'))
def inline(s):
 s=html.escape(s).replace('—','-').replace('–','-')
 s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
 s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:'<link color="#5041c9" href="'+html.escape(('annexes/'+m[2].replace('.md','.html')) if m[2].endswith('.md') else m[2],quote=True)+'">'+m[1]+'</link>',s)
 return s
story=[]
tokens=json.loads((ROOT/'tmp/client_note_tokens.json').read_text(encoding='utf-8'))
for t in tokens:
 typ=t['type']
 if typ=='paragraph':
  if t['text'].startswith('![Logo'):continue
  story.append(Paragraph(inline(t['text']),styles['Body']))
 elif typ=='heading':
  if t['text']=='Quand les systèmes rendent le service':story.append(PageBreak())
  story.append(Paragraph(inline(t['text']),styles['TitleClient' if t['depth']==1 else 'H2' if t['depth']==2 else 'H3']))
 elif typ=='table':
  n=len(t['header']); widths=([168,105,105,105] if n==4 else [150,333] if n==2 else [483/n]*n)
  rows=[[Paragraph(inline(c['text']),styles['HeadCell']) for c in t['header']]]+[[Paragraph(inline(c['text']),styles['Cell']) for c in row] for row in t['rows']]
  table=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
  table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#19344c')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f0edff')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,-1),(-1,-1),.5,colors.HexColor('#dce3e9'))]))
  story.extend([table,Spacer(1,10)])
 elif typ=='list':
  for item in t['items']:story.append(Paragraph('• '+inline(item['text']),styles['Body']))
 elif typ=='hr':story.append(Spacer(1,4))
def page(c,doc):
 c.drawImage(str(ROOT/'assets/exalt-logo.png'),456,793,width=83,height=30,preserveAspectRatio=True,mask='auto')
 c.setFont('Arial',8);c.setFillColor(colors.HexColor('#617488'));c.drawString(56,30,'Laurent Sintès · eXalt · 21 octobre 2026');c.drawRightString(539,30,f'{doc.page}')
doc=SimpleDocTemplate(str(out/'FLOW_Etude_decision.pdf'),pagesize=(595.28,841.89),rightMargin=56,leftMargin=56,topMargin=60,bottomMargin=48,title='FLOW Etude économique',author='Laurent Sintès · eXalt')
doc.build(story,onFirstPage=page,onLaterPages=page)
print(out/'FLOW_Etude_decision.pdf')
