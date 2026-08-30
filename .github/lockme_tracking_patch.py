from pathlib import Path

CONNECT = '<script src="https://widget.lock.me/connect.js" type="text/javascript" crossorigin="anonymous" async></script>'
GOOGLE_TAG = '<script id="familock-google-tag" async src="https://www.googletagmanager.com/gtag/js?id=AW-969004050"></script>'


def add_connect(path_str):
    path = Path(path_str)
    text = path.read_text(encoding='utf-8')
    if 'https://widget.lock.me/connect.js' in text:
        return False
    if GOOGLE_TAG not in text:
        raise RuntimeError(f'{path_str}: nie znaleziono tagu Google')
    text = text.replace(GOOGLE_TAG, GOOGLE_TAG + '\n' + CONNECT, 1)
    path.write_text(text, encoding='utf-8')
    return True


THANK_YOU = '''<!doctype html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rezerwacja potwierdzona | Familock</title>
<meta name="robots" content="noindex,follow">
<meta name="description" content="Potwierdzenie rezerwacji w Familock Escape Room.">
<link rel="icon" href="/favicon.png">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800;900&family=Barlow:wght@300;400;500&display=swap">
<script>
window.dataLayer = window.dataLayer || [];
window.gtag = window.gtag || function(){ window.dataLayer.push(arguments); };
window.gtag('consent','default',{
  analytics_storage:'denied',
  ad_storage:'denied',
  ad_user_data:'denied',
  ad_personalization:'denied',
  wait_for_update:500
});
window.gtag('set','ads_data_redaction',true);
try {
  var saved = JSON.parse(localStorage.getItem('familock_cookie_consent_v5'));
  if (saved && saved.version === 5) {
    window.gtag('consent','update',{
      analytics_storage:saved.analytics ? 'granted' : 'denied',
      ad_storage:saved.marketing ? 'granted' : 'denied',
      ad_user_data:saved.marketing ? 'granted' : 'denied',
      ad_personalization:'denied'
    });
  }
} catch(e) {}
window.gtag('js',new Date());
window.gtag('config','G-LY7D7XH1K3',{
  allow_google_signals:false,
  allow_ad_personalization_signals:false
});
window.gtag('config','AW-969004050',{
  allow_ad_personalization_signals:false
});
</script>
<script id="familock-google-tag" async src="https://www.googletagmanager.com/gtag/js?id=AW-969004050"></script>
<script src="https://widget.lock.me/connect.js" type="text/javascript" crossorigin="anonymous" async></script>
<style>
*{box-sizing:border-box}body{margin:0;min-height:100vh;background:#0d0d0d;color:#f0ecec;font-family:Barlow,Arial,sans-serif;display:grid;place-items:center;padding:24px}.box{width:min(720px,100%);border:1px solid #353030;border-top:3px solid #8b2530;background:#171515;padding:clamp(28px,6vw,54px)}.logo{font-family:'Barlow Condensed',Arial,sans-serif;font-size:1.45rem;font-weight:900;letter-spacing:.04em;text-decoration:none;color:#f0ecec}.logo span{color:#8b2530}.kicker{margin:42px 0 8px;font-family:'Barlow Condensed',Arial,sans-serif;font-size:.72rem;font-weight:800;letter-spacing:.22em;text-transform:uppercase;color:#d2606f}h1{font-family:'Barlow Condensed',Arial,sans-serif;font-size:clamp(2.8rem,9vw,5rem);line-height:.9;margin:0 0 18px}p{color:#b0a8a5;line-height:1.75;margin:0 0 14px}.details{margin:28px 0;border-top:1px solid #353030}.row{display:grid;grid-template-columns:150px 1fr;gap:14px;padding:12px 0;border-bottom:1px solid #353030}.label{font-family:'Barlow Condensed',Arial,sans-serif;font-size:.75rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#8f8583}.value{color:#f0ecec}.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:28px}.btn{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:9px 16px;text-decoration:none;border:1px solid #4a4244;color:#f0ecec;font-family:'Barlow Condensed',Arial,sans-serif;font-weight:800;text-transform:uppercase;letter-spacing:.08em;font-size:.78rem}.btn.primary{background:#8b2530;border-color:#8b2530}@media(max-width:560px){.row{grid-template-columns:1fr;gap:2px}.box{padding:28px 22px}}
</style>
</head>
<body>
<main class="box">
<a class="logo" href="/">FAMI<span>LOCK</span></a>
<div class="kicker">Rezerwacja przyjęta</div>
<h1>Do zobaczenia w Familocku</h1>
<p>Rezerwacja została zakończona. Potwierdzenie i szczegóły rezerwacji znajdziesz również w wiadomości wysłanej przez LockMe.</p>
<div class="details" id="details" hidden>
  <div class="row" id="date-row" hidden><div class="label">Termin</div><div class="value" id="date-value"></div></div>
  <div class="row" id="price-row" hidden><div class="label">Cena</div><div class="value" id="price-value"></div></div>
  <div class="row" id="id-row" hidden><div class="label">Numer rezerwacji</div><div class="value" id="id-value"></div></div>
</div>
<div class="actions"><a class="btn primary" href="/">Strona główna</a><a class="btn" href="/starzik/">Starzik</a></div>
</main>
<script>
(function(){
  var q = new URLSearchParams(window.location.search);
  var date = q.get('date');
  var hour = q.get('h');
  var price = q.get('price');
  var currency = q.get('currency') || 'PLN';
  var id = q.get('id');
  var any = false;
  if (date || hour) {
    document.getElementById('date-value').textContent = [date, hour].filter(Boolean).join(' · ');
    document.getElementById('date-row').hidden = false;
    any = true;
  }
  if (price) {
    var numeric = Number(String(price).replace(',', '.'));
    document.getElementById('price-value').textContent = Number.isFinite(numeric) ? new Intl.NumberFormat('pl-PL',{style:'currency',currency:currency}).format(numeric) : price + ' ' + currency;
    document.getElementById('price-row').hidden = false;
    any = true;
  }
  if (id) {
    document.getElementById('id-value').textContent = id;
    document.getElementById('id-row').hidden = false;
    any = true;
  }
  document.getElementById('details').hidden = !any;
})();
</script>
</body>
</html>
'''

add_connect('index.html')
add_connect('starzik/index.html')

tp = Path('rezerwacja-potwierdzona/index.html')
tp.parent.mkdir(parents=True, exist_ok=True)
tp.write_text(THANK_YOU, encoding='utf-8')

# Pliki techniczne są usuwane po wykonaniu, żeby repo pozostało czyste.
for temporary in [
    Path('.lockme-tracking-trigger'),
    Path('.github/workflows/lockme-tracking.yml'),
    Path('.github/lockme_tracking_patch.py')
]:
    if temporary.exists():
        temporary.unlink()

print('LockMe connect.js i thank-you page wdrożone.')
