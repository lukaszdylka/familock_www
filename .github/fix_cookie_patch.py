from pathlib import Path

path = Path('.github/apply_cookie_ux.py')
text = path.read_text(encoding='utf-8')

old_line = "map_pattern = r'''        <div class=\"service-consent-placeholder\" data-cookie-placeholder=\"googleMaps\">.*?      <iframe title=\"Mapa dojazdu do Familocka\" data-cookie-service=\"googleMaps\" data-src=\"https://www\\.google\\.com/maps\\?q=Cmentarna\\+5%2C\\+41-600\\+%C5%9Awi%C4%99to%C5%82owice&output=embed\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\" hidden></iframe>'''"
new_line = "map_pattern = r'''        <div class=\"service-consent-placeholder\" data-cookie-placeholder=\"googleMaps\">.*?<a href=\"https://maps\\.google\\.com/\\?q=Cmentarna\\+5\\+%C5%9Awi%C4%99toch%C5%82owice\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"map-link\">Otwórz w Google Maps →</a>'''"

if text.count(old_line) != 1:
    raise SystemExit(f'expected one old map pattern, found {text.count(old_line)}')
text = text.replace(old_line, new_line, 1)

start = text.index('map_repl = ', text.index('map_pattern = '))
end = text.index('\nindex = sub_once(index, map_pattern', start)
block = text[start:end]
if 'Otwórz w Google Maps →' not in block:
    close = "        </div>'''"
    if block.count(close) != 1:
        raise SystemExit(f'expected one map repl close, found {block.count(close)}')
    replacement = "        </div>\n        <a href=\"https://maps.google.com/?q=Cmentarna+5+%C5%9Awi%C4%99toch%C5%82owice\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"map-link\">Otwórz w Google Maps →</a>'''"
    block = block.replace(close, replacement, 1)
    text = text[:start] + block + text[end:]

old_category_pattern = "pat = rf'''        <div class=\"cookie-category\">\\s*<div>\\s*<div class=\"cookie-category-name\">{re.escape(name)}</div>.*?</div>\\s*</div>'''"
new_category_pattern = "pat = rf'''        <div class=\"cookie-category\">\\s*<div>\\s*<div class=\"cookie-category-name\">{re.escape(name)}</div>.*?</label>\\s*</div>'''"
if text.count(old_category_pattern) != 1:
    raise SystemExit(f'expected one category pattern, found {text.count(old_category_pattern)}')
text = text.replace(old_category_pattern, new_category_pattern, 1)

path.write_text(text, encoding='utf-8')
print('Map and category selectors fixed')
