from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected 1 match, got {count}')
    return text.replace(old, new, 1)

index = Path('index.html')
text = index.read_text(encoding='utf-8')
old = '''  <div class="f-links">
    <a href="/polityka.html">Polityka prywatności</a>
    <a href="/regulamin.html">Regulamin</a>
    <button type="button" id="cookie-settings-link" aria-controls="cookie-consent" aria-expanded="false">Ustawienia cookies</button>
    <a href="mailto:kontakt@familock.pl">kontakt@familock.pl</a>
  </div>'''
new = '''  <div class="f-links">
    <a href="/starzik/">Starzik</a>
    <a href="/cennik/">Cennik</a>
    <a href="/voucher/">Voucher</a>
    <a href="/dla-szkol-i-firm/">Szkoły i firmy</a>
    <a href="/pierwszy-escape-room/">Pierwszy escape room</a>
    <a href="/polityka.html">Polityka prywatności</a>
    <a href="/regulamin.html">Regulamin</a>
    <button type="button" id="cookie-settings-link" aria-controls="cookie-consent" aria-expanded="false">Ustawienia cookies</button>
    <a href="mailto:kontakt@familock.pl">kontakt@familock.pl</a>
  </div>'''
text = replace_once(text, old, new, 'index footer')
index.write_text(text, encoding='utf-8')

starzik = Path('starzik/index.html')
text = starzik.read_text(encoding='utf-8')
old = '''<div class="footer-links"><a href="/regulamin.html">Regulamin</a><a href="/polityka.html">Polityka prywatności</a><button type="button" id="cookie-settings-link">Ustawienia cookies</button></div>'''
new = '''<div class="footer-links"><a href="/cennik/">Cennik</a><a href="/voucher/">Voucher</a><a href="/dla-szkol-i-firm/">Szkoły i firmy</a><a href="/pierwszy-escape-room/">Pierwszy escape room</a><a href="/regulamin.html">Regulamin</a><a href="/polityka.html">Polityka prywatności</a><button type="button" id="cookie-settings-link">Ustawienia cookies</button></div>'''
text = replace_once(text, old, new, 'starzik footer')
starzik.write_text(text, encoding='utf-8')

for p in [Path('.subpages-links-trigger'), Path('.github/workflows/subpages-links.yml'), Path('.github/subpages_internal_links.py')]:
    if p.exists():
        p.unlink()
