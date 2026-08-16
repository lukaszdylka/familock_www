from pathlib import Path

path = Path('.github/apply_cookie_ux.py')
text = path.read_text(encoding='utf-8')
old = '''map_pattern = r\'''        <div class="service-consent-placeholder" data-cookie-placeholder="googleMaps">.*?      <iframe title="Mapa dojazdu do Familocka" data-cookie-service="googleMaps" data-src="https://www\\.google\\.com/maps\\?q=Cmentarna\\+5%2C\\+41-600\\+%C5%9Awi%C4%99to%C5%82owice&output=embed" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade" hidden></iframe>\'''\n'''
new = '''map_pattern = r\'''        <div class="service-consent-placeholder" data-cookie-placeholder="googleMaps">.*?<a href="https://maps\\.google\\.com/\\?q=Cmentarna\\+5\\+%C5%9Awi%C4%99toch%C5%82owice" target="_blank" rel="noopener noreferrer" class="map-link">Otwórz w Google Maps →</a>\'''\n'''
if text.count(old) != 1:
    raise SystemExit(f'expected one map pattern, found {text.count(old)}')
text = text.replace(old, new, 1)
old_repl = '''        </div>'''\n'''
# Include the existing external Maps link in the replacement, because the broader
# pattern consumes it together with the blocked iframe.
needle = '''map_repl = r\'''        <div class="service-consent-placeholder">\n'''
if needle not in text:
    needle = '''map_repl = \'\'\'        <div class="service-consent-placeholder">\n'''
# Append the link immediately before the closing triple quote of map_repl.
start = text.index('map_repl = ', text.index('map_pattern = '))
end = text.index("\nindex = sub_once(index, map_pattern", start)
block = text[start:end]
if 'Otwórz w Google Maps →' not in block:
    close = "        </div>'''"
    if close not in block:
        raise SystemExit('map replacement closing marker not found')
    block = block.replace(close, '''        </div>\n        <a href="https://maps.google.com/?q=Cmentarna+5+%C5%9Awi%C4%99toch%C5%82owice" target="_blank" rel="noopener noreferrer" class="map-link">Otwórz w Google Maps →</a>\''' ''', 1)
    text = text[:start] + block + text[end:]
path.write_text(text, encoding='utf-8')
print('Map selector fixed')
