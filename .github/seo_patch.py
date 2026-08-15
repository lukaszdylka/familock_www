from pathlib import Path

index = Path("index.html")
text = index.read_text(encoding="utf-8")

replacements = [
    (
        '<title>Familock Escape Room – Pokój Zagadek Świętochłowice | Śląsk</title>',
        '<title>Familock – Escape Room w Świętochłowicach | Śląsk</title>',
    ),
    (
        '<meta name="description" content="Familock Escape Room w Świętochłowicach na Śląsku. Zagraj w autorski, fabularny pokój zagadek Starzik w klimacie śląskiego familoka. Zarezerwuj termin online." />',
        '<meta name="description" content="Familock to fabularny escape room w Świętochłowicach. Starzik: 90 minut gry, 2–5 osób, śląski familok i autorskie zagadki. Rezerwacje online." />',
    ),
    (
        '<meta name="keywords" content="escape room Świętochłowice, pokój zagadek Śląsk, familock, escape room Chorzów, escape room Katowice, Starzik escape room, Tesla Escape Box, escape room śląsk" />\n',
        '',
    ),
    (
        '<meta property="og:title" content="Familock Escape Room · Starzik · Świętochłowice" />',
        '<meta property="og:title" content="Familock · Escape Room w Świętochłowicach" />',
    ),
    (
        '<meta property="og:description" content="Autorski, fabularny escape room w klimacie śląskiego familoka. Poznaj Starzika i zarezerwuj termin online." />',
        '<meta property="og:description" content="Starzik: 90 minut fabularnej gry w klimacie śląskiego familoka. 2–5 osób. Rezerwacje online w Familocku." />',
    ),
    (
        '<meta name="twitter:title" content="Familock Escape Room · Starzik · Świętochłowice" />',
        '<meta name="twitter:title" content="Familock · Escape Room w Świętochłowicach" />',
    ),
    (
        '<meta name="twitter:description" content="Autorski, fabularny escape room w klimacie śląskiego familoka." />',
        '<meta name="twitter:description" content="Starzik: 90 minut fabularnej gry w klimacie śląskiego familoka. 2–5 osób." />',
    ),
    (
        '<script type="application/ld+json">{"@context":"https://schema.org","@type":"EntertainmentBusiness","name":"Familock Escape Room","legalName":"Łukasz Dyłka Familock","taxID":"6272709230","url":"https://familock.pl","telephone":"+48573955316","email":"kontakt@familock.pl","address":{"@type":"PostalAddress","streetAddress":"ul. Cmentarna 5/3","addressLocality":"Świętochłowice","postalCode":"41-600","addressCountry":"PL"},"priceRange":"100–450 PLN"}</script>',
        '''<script type="application/ld+json">{
  "@context": "https://schema.org",
  "@type": "EntertainmentBusiness",
  "@id": "https://familock.pl/#business",
  "name": "Familock Escape Room",
  "alternateName": "Familock",
  "legalName": "Łukasz Dyłka Familock",
  "description": "Fabularny escape room w Świętochłowicach. Autorskie scenariusze i zagadki w śląskim klimacie.",
  "url": "https://familock.pl/",
  "telephone": "+48573955316",
  "email": "kontakt@familock.pl",
  "taxID": "6272709230",
  "image": "https://familock.pl/img/starzik/starzik-familock-escape-room-swietochlowice-02.webp",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "ul. Cmentarna 5/3",
    "addressLocality": "Świętochłowice",
    "postalCode": "41-600",
    "addressCountry": "PL"
  },
  "sameAs": [
    "https://www.facebook.com/escaperoomfamilock",
    "https://www.instagram.com/familock.escaperoom/"
  ],
  "priceRange": "100–450 PLN"
}</script>''',
    ),
    (
        '.nav-logo .dot{width:6px;height:6px;background:var(--red);border-radius:50%;display:inline-block;margin:0 2px 10px}\n',
        '',
    ),
    (
        'h1.hero-title{font-family:var(--fd);font-weight:900;font-size:clamp(5.5rem,11vw,12rem);line-height:.88;letter-spacing:-.025em;margin-bottom:2rem;position:relative}\n.hero-title .line1{display:inline-block;color:var(--cream)}\n.hero-title .line2{display:inline-block;color:var(--red);text-shadow:0 0 70px rgba(139,37,48,.4)}\n.hero-sub{font-family:var(--fs);font-style:italic;font-size:1.05rem;color:var(--cream2);max-width:440px;margin-bottom:2.8rem;line-height:1.9;position:relative}\n.hero-tagline{font-family:var(--fd);font-size:1.2rem;font-weight:700;text-transform:uppercase;letter-spacing:.35em;color:var(--muted);margin-top:1rem;margin-bottom:2.5rem;position:relative;opacity:0}',
        'h1.hero-title{font-family:var(--fd);font-weight:900;font-size:clamp(5.5rem,11vw,12rem);line-height:.88;letter-spacing:-.025em;margin-bottom:.9rem;position:relative}\n.hero-brand{display:block}\n.hero-title .line1{display:inline;color:var(--cream)}\n.hero-title .line2{display:inline;color:var(--red);text-shadow:0 0 70px rgba(139,37,48,.4)}\n.hero-seo-title{display:block;font-size:clamp(1.35rem,2.5vw,2.45rem);line-height:1.08;letter-spacing:.1em;text-transform:uppercase;color:var(--cream2);margin-top:1.15rem}\n.hero-sub{font-family:var(--fs);font-style:italic;font-size:1.05rem;color:var(--cream2);max-width:560px;margin-bottom:2.8rem;line-height:1.9;position:relative}\n.hero-tagline{font-family:var(--fd);font-size:1rem;font-weight:700;text-transform:uppercase;letter-spacing:.28em;color:var(--muted);margin-top:0;margin-bottom:1.35rem;position:relative;opacity:0}',
    ),
    (
        '<a href="#home" class="nav-logo">FAMI<span class="dot"></span><span class="lock">LOCK</span></a>',
        '<a href="#home" class="nav-logo" aria-label="Familock – strona główna">FAMI<span class="lock">LOCK</span></a>',
    ),
    (
        '''  <h1 class="hero-title fade-up d2">
    <span class="line1">FAMI</span><span class="line2">LOCK</span>
    <p class="hero-tagline fade-up d25">Śląski Escape Room 🤍</p>
  </h1>
  <p class="hero-sub fade-up d3">Familock to mała firma escape room, oferująca fabularne, autorskie scenariusze i zagadki.<br>Przekonaj się w pokoju <i>Starzik</i>. Rezerwacje na Escape Box „Ostatni wynalazek N. Tesli” pojawią się już wkrótce.</p>''',
        '''  <h1 class="hero-title fade-up d2">
    <span class="hero-brand"><span class="line1">FAMI</span><span class="line2">LOCK</span></span>
    <span class="hero-seo-title">Escape Room w Świętochłowicach</span>
  </h1>
  <p class="hero-tagline fade-up d25">Śląski klimat · autorskie zagadki · 90 minut historii</p>
  <p class="hero-sub fade-up d3">Familock to fabularny escape room w Świętochłowicach. W pokoju <i>Starzik</i> czeka na Was 90 minut autorskich zagadek i historii osadzonej w klimacie śląskiego familoka. Rezerwacje online są już dostępne.</p>''',
    ),
]

for old, new in replacements:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Nie znaleziono dokładnie jednego wzorca ({count}): {old[:120]}")
    text = text.replace(old, new, 1)

index.write_text(text, encoding="utf-8")

sitemap = Path("sitemap.xml")
sm = sitemap.read_text(encoding="utf-8")
old = '<loc>https://familock.pl/</loc>\n    <lastmod>2026-08-12</lastmod>'
new = '<loc>https://familock.pl/</loc>\n    <lastmod>2026-08-15</lastmod>'
if sm.count(old) != 1:
    raise SystemExit("Nie znaleziono oczekiwanej daty strony głównej w sitemap.xml")
sitemap.write_text(sm.replace(old, new, 1), encoding="utf-8")

# Proste testy bezpieczeństwa przed commitem.
result = index.read_text(encoding="utf-8")
checks = [
    '<title>Familock – Escape Room w Świętochłowicach | Śląsk</title>',
    '<span class="hero-seo-title">Escape Room w Świętochłowicach</span>',
    'https://familock.pl/#business',
    'https://www.instagram.com/familock.escaperoom/',
]
for item in checks:
    if item not in result:
        raise SystemExit(f"Brak po poprawce: {item}")
if 'class="dot"' in result:
    raise SystemExit("Kropka nadal występuje w logo")
if '<p class="hero-tagline' in result[result.index('<h1 class="hero-title'):result.index('</h1>', result.index('<h1 class="hero-title'))]:
    raise SystemExit("W H1 nadal znajduje się element <p>")

print("SEO patch OK")
