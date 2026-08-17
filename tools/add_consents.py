from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

OUT = Path('dokumenty')
OUT.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('FamSerif', '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'))
pdfmetrics.registerFont(TTFont('FamSerifBold', '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'))
BURGUNDY = colors.HexColor('#6B2D30')
PALE = colors.HexColor('#F3EEEE')
TEXT = colors.HexColor('#2E2B2B')
MUTED = colors.HexColor('#6F6868')
base = ParagraphStyle('base', fontName='FamSerif', fontSize=9.8, leading=14, textColor=TEXT, spaceAfter=5)
heading = ParagraphStyle('heading', fontName='FamSerif', fontSize=15, leading=18, textColor=BURGUNDY, spaceBefore=6, spaceAfter=8)
title = ParagraphStyle('title', fontName='FamSerif', fontSize=22, leading=26, textColor=BURGUNDY, alignment=TA_CENTER, spaceAfter=4)
subtitle = ParagraphStyle('subtitle', fontName='FamSerif', fontSize=10, leading=13, textColor=MUTED, alignment=TA_CENTER, spaceAfter=8)
notice = ParagraphStyle('notice', fontName='FamSerif', fontSize=9.3, leading=12, textColor=TEXT, alignment=TA_CENTER)
checkbox = '\u2610'

def line_field(label):
    return [Paragraph(label, base), Paragraph('.' * 76, ParagraphStyle('dots', parent=base, fontSize=8.5, leading=9, spaceAfter=3))]

def numbered(items):
    out=[]
    for i,text in enumerate(items,1):
        t=Table([[Paragraph(f'{i}.', base), Paragraph(text, base)]], colWidths=[7*mm, 162*mm])
        t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),1)]))
        out.append(t)
    return out

def header_story(title_text, subtitle_text, notice_text=None):
    story=[Spacer(1,3*mm), Paragraph(title_text, title)]
    line=Table([['']], colWidths=[169*mm], rowHeights=[0.5*mm])
    line.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),BURGUNDY),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0)]))
    story += [line, Spacer(1,2.5*mm), Paragraph(subtitle_text, subtitle)]
    if notice_text:
        box=Table([[Paragraph(notice_text, notice)]], colWidths=[169*mm])
        box.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8)]))
        story += [box, Spacer(1,5*mm)]
    return story

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('FamSerif', 6.8)
    canvas.setFillColor(colors.HexColor('#8A8181'))
    canvas.drawCentredString(A4[0]/2, 12*mm, 'Escape Room Familock | ul. Cmentarna 5/3, 41-600 Świętochłowice | kontakt@familock.pl | 573 955 316')
    canvas.restoreState()

def build_parent():
    path=OUT/'zgoda-rodzica-na-gre-familock.pdf'
    doc=SimpleDocTemplate(str(path), pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=14*mm, bottomMargin=23*mm)
    s=header_story('ZGODA RODZICA LUB OPIEKUNA PRAWNEGO','na udział osoby małoletniej w grze w Escape Room Familock','Dokument przeznaczony dla osoby małoletniej uczestniczącej bez obecności rodzica lub opiekuna prawnego.')
    for label in ['Imię i nazwisko rodzica lub opiekuna prawnego:','Numer telefonu kontaktowego:','Imię i nazwisko osoby małoletniej:','Data urodzenia osoby małoletniej:','Termin i nazwa gry:']:
        s += line_field(label)
    s += [Paragraph('Oświadczenie', heading), Paragraph('Wyrażam zgodę na udział wskazanej wyżej osoby małoletniej w grze organizowanej przez Escape Room Familock przy ul. Cmentarnej 5/3 w Świętochłowicach.', base)]
    s += numbered([
        'Zapoznałem lub zapoznałam się z regulaminem Escape Room Familock i akceptuję jego postanowienia.',
        'Według mojej wiedzy stan zdrowia osoby małoletniej pozwala na bezpieczny udział w grze. Zobowiązuję się wcześniej poinformować obsługę o istotnych przeciwwskazaniach, w tym klaustrofobii, epilepsji, silnych stanach lękowych, chorobach serca, ciąży lub nadwrażliwości na bodźce.',
        'Przyjmuję do wiadomości, że gra może zawierać ciemność, ograniczoną przestrzeń, efekty dźwiękowe i świetlne, elementy zaskoczenia oraz sytuacje wywołujące napięcie.',
        'Osoba małoletnia ma obowiązek przestrzegać poleceń obsługi, zasad bezpieczeństwa i zakazu używania siły wobec wyposażenia.',
        'W razie zagrożenia, złego samopoczucia lub potrzeby przerwania gry należy niezwłocznie powiadomić obsługę albo użyć wskazanego podczas instruktażu przycisku odblokowującego drogę ewakuacyjną.',
        'Podaję numer telefonu, pod którym pozostaję dostępny lub dostępna w czasie trwania gry.'
    ])
    s += [Spacer(1,3*mm), Paragraph('Miejscowość i data:  ............................................................', base), Spacer(1,2*mm), Paragraph('Czytelny podpis rodzica lub opiekuna prawnego:  ............................................................', base)]
    doc.build(s, onFirstPage=footer)

def build_image():
    path=OUT/'zgoda-na-wizerunek-familock.pdf'
    doc=SimpleDocTemplate(str(path), pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=14*mm, bottomMargin=23*mm)
    s=header_story('ZGODA NA WYKORZYSTANIE WIZERUNKU','Escape Room Familock','Zgoda jest dobrowolna. Jej brak nie wpływa na możliwość udziału w grze.')
    s += line_field('Imię i nazwisko osoby wyrażającej zgodę:')
    s += [Paragraph('Zaznacz właściwe:', base), Paragraph(f'{checkbox} wyrażam zgodę na publikację mojego wizerunku', base), Paragraph(f'{checkbox} jako rodzic lub opiekun prawny wyrażam zgodę na publikację wizerunku osoby małoletniej:', base)]
    s += line_field('Imię i nazwisko osoby małoletniej:')
    s += [Paragraph('Zakres zgody', heading), Paragraph('Wyrażam zgodę na nieodpłatne utrwalanie, wykorzystywanie i publikowanie zdjęć wykonanych przez obsługę po zakończeniu gry, w celach informacyjnych i promocyjnych związanych z działalnością Escape Room Familock.', base), Paragraph('Zgoda obejmuje publikację w następujących miejscach:', base)]
    for text in ['strona internetowa familock.pl','profil Escape Room Familock na Facebooku','profil Escape Room Familock na Instagramie','inne materiały informacyjne i promocyjne Escape Room Familock']:
        s.append(Paragraph(f'{checkbox} {text}', base))
    s += [Paragraph('Informacje dotyczące zgody', heading)]
    s += numbered([
        'Zgoda może zostać cofnięta w dowolnym momencie poprzez wiadomość wysłaną na adres kontakt@familock.pl.',
        'Cofnięcie zgody nie wpływa na zgodność z prawem wykorzystania wizerunku dokonanego przed jej cofnięciem.',
        'Publikacja materiału w internecie może wiązać się z jego dalszym udostępnianiem przez użytkowników serwisów społecznościowych, na co Escape Room Familock nie ma pełnego wpływu.',
        'Administratorem danych osobowych jest podmiot prowadzący Escape Room Familock. Szczegółowe informacje znajdują się w polityce prywatności dostępnej na stronie familock.pl i w lokalu.'
    ])
    s += [Spacer(1,3*mm), Paragraph('Miejscowość i data:  ............................................................', base), Spacer(1,2*mm), Paragraph('Czytelny podpis:  ..............................................................................................', base)]
    doc.build(s, onFirstPage=footer)

build_parent()
build_image()

p=Path('starzik/index.html')
s=p.read_text(encoding='utf-8')
if '/dokumenty/zgoda-rodzica-na-gre-familock.pdf' in s:
    raise SystemExit('download block already present')
marker='</div></div></div></section>\n<section class="section-dark"><div class="shell faq">'
if marker not in s:
    raise SystemExit('info/faq marker not found')
block='''</div></div><div class="contact-strip" style="margin-top:2rem"><span><strong style="display:block;color:var(--cream);margin-bottom:.25rem">Dokumenty do pobrania</strong>Możesz wydrukować formularze wcześniej i przynieść podpisane do Familocka.</span><div class="contact-links"><a href="/dokumenty/zgoda-rodzica-na-gre-familock.pdf" download>Zgoda rodzica na grę (PDF)</a><a href="/dokumenty/zgoda-na-wizerunek-familock.pdf" download>Zgoda na wizerunek (PDF)</a></div></div></div></section>\n<section class="section-dark"><div class="shell faq">'''
s=s.replace(marker, block, 1)
old='Osoby poniżej 16 lat grają z pełnoletnim opiekunem, a osoby w wieku 16–18 lat mogą zagrać bez dorosłego po dostarczeniu pisemnej zgody opiekuna.</div>'
new='Osoby poniżej 16 lat grają z pełnoletnim opiekunem, a osoby w wieku 16–18 lat mogą zagrać bez dorosłego po dostarczeniu pisemnej zgody opiekuna. <a href="/dokumenty/zgoda-rodzica-na-gre-familock.pdf" download>Pobierz formularz zgody (PDF).</a></div>'
if old not in s:
    raise SystemExit('age FAQ marker not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
