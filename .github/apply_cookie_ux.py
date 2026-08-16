from pathlib import Path
import re


def sub_once(text, pattern, repl, label, flags=0):
    new, count = re.subn(pattern, repl, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    return new


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)

index_path = Path('index.html')
index = index_path.read_text(encoding='utf-8')

# Booking: remove cookie language, keep deliberate click-to-load fallback,
# and auto-load when user explicitly clicks any booking CTA.
booking_pattern = r'''        <div class="service-consent-placeholder booking-placeholder" data-cookie-placeholder="lockme">.*?        <iframe id="booking-lockme-frame" class="booking-lockme-frame" data-cookie-service="lockme" data-src="https://widget\.lock\.me/pl/calendar/fd5ace6aab33825bcc05880372c4f7b0_750_14685\.html\?month=1" loading="lazy" height="450" scrolling="auto" allowtransparency="true" title="Rezerwacja Familock" hidden></iframe>'''
booking_repl = '''        <div class="service-consent-placeholder booking-placeholder" id="lockme-loader">
          <div class="service-consent-box">
            <div class="service-consent-icon" aria-hidden="true">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            </div>
            <div class="service-consent-title">Sprawdź wolne terminy</div>
            <p class="service-consent-copy">Kalendarz rezerwacji otworzy się tutaj po kliknięciu. Możesz od razu wybrać termin i przejść do rezerwacji.</p>
            <div class="service-consent-actions">
              <button class="service-consent-btn" id="load-lockme" type="button">Pokaż dostępne terminy</button>
              <a class="service-consent-link" href="https://widget.lock.me/pl/calendar/fd5ace6aab33825bcc05880372c4f7b0_750_14685.html?month=1" target="_blank" rel="noopener noreferrer">Otwórz w nowej karcie</a>
            </div>
          </div>
        </div>
        <iframe id="booking-lockme-frame" class="booking-lockme-frame" data-src="https://widget.lock.me/pl/calendar/fd5ace6aab33825bcc05880372c4f7b0_750_14685.html?month=1" loading="lazy" height="450" scrolling="auto" allowtransparency="true" title="Rezerwacja Familock" hidden></iframe>'''
index = sub_once(index, booking_pattern, booking_repl, 'booking block', re.S)

map_pattern = r'''        <div class="service-consent-placeholder" data-cookie-placeholder="googleMaps">.*?      <iframe title="Mapa dojazdu do Familocka" data-cookie-service="googleMaps" data-src="https://www\.google\.com/maps\?q=Cmentarna\+5%2C\+41-600\+%C5%9Awi%C4%99to%C5%82owice&output=embed" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade" hidden></iframe>'''
map_repl = '''        <div class="service-consent-placeholder">
          <div class="service-consent-box">
            <div class="service-consent-icon" aria-hidden="true">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 12-9 12S3 17 3 10a9 9 0 1118 0z"/><circle cx="12" cy="10" r="3"/></svg>
            </div>
            <div class="service-consent-title">Familock · Cmentarna 5/3</div>
            <p class="service-consent-copy">Wejście przez klatkę schodową. Kliknięcie w mapę otworzy trasę w Google Maps w nowej karcie.</p>
          </div>
        </div>'''
index = sub_once(index, map_pattern, map_repl, 'map block', re.S)

index = replace_once(
    index,
    'Strona używa danych niezbędnych do działania. Kalendarz LockMe, mapa Google, Google Analytics i pomiar Google Ads są uruchamiane wyłącznie zgodnie z wyborem użytkownika w ustawieniach cookies. Nie korzystamy z Meta Pixel, a personalizacja reklam Google pozostaje wyłączona.',
    'Strona używa danych niezbędnych do działania. Kalendarz LockMe jest uruchamiany dopiero, gdy użytkownik wybierze rezerwację lub poprosi o pokazanie terminów. Google Maps otwiera się dopiero po kliknięciu linku. Zgoda w ustawieniach cookies dotyczy Google Analytics i pomiaru Google Ads. Nie korzystamy z Meta Pixel, a personalizacja reklam Google pozostaje wyłączona.',
    'privacy summary'
)
index = replace_once(
    index,
    'Niezbędne dane pozwalają zapamiętać Twój wybór. Za Twoją zgodą możemy też uruchomić Google Analytics, pomiar Google Ads, kalendarz LockMe i mapę Google. Usługi te mogą zapisywać własne cookies oraz otrzymać informacje o urządzeniu. Bez zgody strona nadal działa. Szczegóły znajdziesz w <a href="/polityka.html#s15">Polityce Cookies</a>.',
    'Niezbędne dane pozwalają zapamiętać Twój wybór. Za Twoją zgodą możemy uruchomić Google Analytics i pomiar Google Ads. Kalendarz rezerwacji LockMe ładuje się dopiero po działaniu związanym z rezerwacją, a Google Maps dopiero po kliknięciu linku. Bez zgody strona nadal działa. Szczegóły znajdziesz w <a href="/polityka.html#s15">Polityce Cookies</a>.',
    'cookie summary'
)
index = replace_once(
    index,
    'Możesz wyrazić zgodę osobno na analitykę, pomiar Google Ads, kalendarz LockMe i mapę Google.',
    'Możesz wyrazić zgodę osobno na analitykę i pomiar Google Ads.',
    'cookie settings intro'
)

# Remove LockMe and Maps from the global cookie toggles.
for name, label in [('Kalendarz LockMe', 'lockme category'), ('Mapa Google', 'maps category')]:
    pat = rf'''        <div class="cookie-category">\s*<div>\s*<div class="cookie-category-name">{re.escape(name)}</div>.*?</div>\s*</div>'''
    index = sub_once(index, pat, '', label, re.S)

index = replace_once(index, "var STORAGE_KEY = 'familock_cookie_consent_v4';\n  var CONSENT_VERSION = 4;", "var STORAGE_KEY = 'familock_cookie_consent_v5';\n  var CONSENT_VERSION = 5;", 'consent version')
index = replace_once(index, "  var lockmeChoice = document.getElementById('cookie-lockme');\n  var mapsChoice = document.getElementById('cookie-google-maps');\n", '', 'cookie service vars')

index = sub_once(
    index,
    r'''  function emptyConsent\(\) \{.*?\n  \}''',
    '''  function emptyConsent() {
    return {
      version: CONSENT_VERSION,
      necessary: true,
      analytics: false,
      marketing: false,
      updatedAt: null
    };
  }''',
    'emptyConsent', re.S
)
index = replace_once(index, "        typeof saved.lockme !== 'boolean' ||\n        typeof saved.googleMaps !== 'boolean' ||\n", '', 'read consent service validation')
index = replace_once(index, "      lockme: !!choice.lockme,\n      googleMaps: !!choice.googleMaps,\n", '', 'write consent service fields')

index = sub_once(index, r'''  function applyService\(service, enabled\) \{.*?\n  \}\n\n''', '', 'applyService', re.S)
index = sub_once(
    index,
    r'''  function applyConsent\(choice\) \{.*?\n  \}''',
    '''  function applyConsent(choice) {
    var effective = choice || emptyConsent();
    updateGoogleConsent(effective);
    applyAnalytics(effective.analytics);
    applyMarketing(effective.marketing);
  }''',
    'applyConsent', re.S
)
index = replace_once(index, "      lockmeChoice.checked = !!base.lockme;\n      mapsChoice.checked = !!base.googleMaps;\n", '', 'setView service fields')
index = replace_once(index, "    choice.lockme = true;\n    choice.googleMaps = true;\n", '', 'acceptAll service fields')
index = replace_once(index, "    choice.lockme = !!lockmeChoice.checked;\n    choice.googleMaps = !!mapsChoice.checked;\n", '', 'saveSettings service fields')
index = sub_once(index, r'''  function enableService\(service\) \{.*?\n  \}\n\n''', '', 'enableService', re.S)
index = sub_once(index, r'''\n  document\.querySelectorAll\('\[data-cookie-enable\]'\)\.forEach\(function\(button\) \{.*?\n  \}\);''', '', 'data cookie listener', re.S)

# Add intentional LockMe loader outside the consent module.
marker = '''function switchTab(id, btn) {
  document.querySelectorAll('.cennik-panel').forEach(function(p) { p.classList.remove('active'); });
  document.querySelectorAll('.tab-btn').forEach(function(b) { b.classList.remove('active'); });
  document.getElementById(id).classList.add('active');
  btn.classList.add('active');
}
'''
loader = marker + '''
var LOCKME_WIDGET_URL = 'https://widget.lock.me/pl/calendar/fd5ace6aab33825bcc05880372c4f7b0_750_14685.html?month=1';
function loadLockmeWidget() {
  var frame = document.getElementById('booking-lockme-frame');
  var loaderBox = document.getElementById('lockme-loader');
  if (!frame) return;
  if (!frame.getAttribute('src')) frame.setAttribute('src', LOCKME_WIDGET_URL);
  frame.hidden = false;
  if (loaderBox) loaderBox.hidden = true;
}
var lockmeLoadButton = document.getElementById('load-lockme');
if (lockmeLoadButton) lockmeLoadButton.addEventListener('click', loadLockmeWidget);
document.querySelectorAll('a[href="#rezerwacja"]').forEach(function(link) {
  link.addEventListener('click', loadLockmeWidget);
});
'''
index = replace_once(index, marker, loader, 'lockme loader insertion')
index = replace_once(
    index,
    "  if (scrollToBooking) {\n    window.setTimeout(function() {",
    "  if (scrollToBooking) {\n    loadLockmeWidget();\n    window.setTimeout(function() {",
    'opening popup booking load'
)

index_path.write_text(index, encoding='utf-8')

policy_path = Path('polityka.html')
policy = policy_path.read_text(encoding='utf-8')
policy = replace_once(
    policy,
    'Strona internetowa Familock korzysta z pamięci przeglądarki oraz, po uzyskaniu zgody użytkownika, z usług funkcjonalnych, analitycznych i reklamowych. Pliki cookies i podobne technologie mogą zapisywać lub odczytywać informacje na urządzeniu użytkownika.',
    'Strona internetowa Familock korzysta z pamięci przeglądarki oraz z usług niezbędnych do działania serwisu. Google Analytics i pomiar Google Ads są uruchamiane wyłącznie po uzyskaniu odpowiedniej zgody użytkownika. Pliki cookies i podobne technologie mogą zapisywać lub odczytywać informacje na urządzeniu użytkownika.',
    'policy intro'
)
old_categories = '''    <p><strong>a) Niezbędne</strong>. Obejmują zapis decyzji dotyczącej prywatności w pamięci przeglądarki. Są potrzebne do respektowania dokonanego wyboru i nie służą do analizy zachowania ani profilowania reklamowego.</p>
    <p><strong>b) Kalendarz LockMe</strong>. Po wyrażeniu odrębnej zgody strona ładuje osadzony kalendarz terminów. LockMe może wtedy korzystać z własnych plików cookies lub podobnych technologii oraz otrzymywać informacje techniczne, takie jak adres IP i dane przeglądarki.</p>
    <p><strong>c) Mapa Google</strong>. Po wyrażeniu odrębnej zgody strona ładuje interaktywną mapę. Google może wtedy korzystać z własnych plików cookies lub podobnych technologii oraz otrzymywać informacje techniczne, takie jak adres IP i dane przeglądarki.</p>
    <p><strong>d) Analityczne</strong>. Po wyrażeniu odrębnej zgody strona uruchamia Google Analytics 4 z identyfikatorem pomiaru G-LY7D7XH1K3. Usługa pomaga mierzyć liczbę użytkowników, wizyty, przybliżoną lokalizację oraz informacje o urządzeniu i przeglądarce. Ustawienia wyłączają Google Signals i personalizację reklam.</p>
    <p><strong>e) Reklamowe</strong>. Po wyrażeniu odrębnej zgody strona uruchamia tag Google Ads z identyfikatorem AW-969004050 w celu pomiaru skuteczności kampanii i konwersji. Personalizacja reklam pozostaje wyłączona.</p>'''
new_categories = '''    <p><strong>a) Niezbędne</strong>. Obejmują zapis decyzji dotyczącej prywatności w pamięci przeglądarki oraz informacje technicznie potrzebne do wykonania funkcji, o które użytkownik sam poprosił, np. procesu rezerwacji po uruchomieniu kalendarza LockMe. Nie są wykorzystywane przez Familock do analizy zachowania ani profilowania reklamowego.</p>
    <p><strong>b) Analityczne</strong>. Po wyrażeniu odrębnej zgody strona uruchamia Google Analytics 4 z identyfikatorem pomiaru G-LY7D7XH1K3. Usługa pomaga mierzyć liczbę użytkowników, wizyty, przybliżoną lokalizację oraz informacje o urządzeniu i przeglądarce. Ustawienia wyłączają Google Signals i personalizację reklam.</p>
    <p><strong>c) Reklamowe</strong>. Po wyrażeniu odrębnej zgody strona uruchamia tag Google Ads z identyfikatorem AW-969004050 w celu pomiaru skuteczności kampanii i konwersji. Personalizacja reklam pozostaje wyłączona.</p>

    <h3>Kalendarz rezerwacji LockMe</h3>
    <p>Kalendarz LockMe nie jest uruchamiany automatycznie przy samym wejściu na stronę. Ładuje się dopiero, gdy użytkownik kliknie przycisk związany z rezerwacją albo wybierze „Pokaż dostępne terminy”. Wtedy przeglądarka łączy się z domeną LockMe, a usługa może otrzymać dane techniczne, takie jak adres IP i informacje o przeglądarce, oraz korzystać z informacji niezbędnych do procesu rezerwacji.</p>
    <p>W zakresie, w jakim zapis lub odczyt informacji na urządzeniu jest konieczny do dostarczenia usługi rezerwacji wyraźnie żądanej przez użytkownika, zastosowanie ma wyjątek przewidziany w art. 399 ust. 3 pkt 2 ustawy Prawo komunikacji elektronicznej. Ewentualne dodatkowe cele analityczne lub marketingowe po stronie LockMe podlegają zasadom i ustawieniom prywatności tego dostawcy.</p>

    <h3>Google Maps</h3>
    <p>Familock nie osadza automatycznie interaktywnej mapy Google. Na stronie znajduje się wyłącznie link do Google Maps. Dane są przekazywane do Google dopiero wtedy, gdy użytkownik sam otworzy ten zewnętrzny serwis.</p>'''
policy = replace_once(policy, old_categories, new_categories, 'policy categories')
policy = replace_once(
    policy,
    'Dane niezbędne są stosowane w zakresie potrzebnym do zapamiętania wyboru użytkownika i prawidłowego działania serwisu. Google Analytics, Google Ads, LockMe i Google Maps są uruchamiane wyłącznie po dobrowolnej, świadomej i jednoznacznej zgodzie wyrażonej w banerze cookies lub przez przycisk przy danej usłudze.',
    'Dane niezbędne są stosowane w zakresie potrzebnym do zapamiętania wyboru użytkownika i wykonania funkcji, o które użytkownik sam poprosił. Google Analytics i Google Ads są uruchamiane wyłącznie po dobrowolnej, świadomej i jednoznacznej zgodzie wyrażonej w banerze cookies. Kalendarz LockMe ładuje się dopiero po działaniu użytkownika związanym z rezerwacją, a Google Maps otwiera się jako zewnętrzny serwis dopiero po kliknięciu linku.',
    'policy legal basis'
)
policy = replace_once(
    policy,
    'Brak zgody nie ogranicza dostępu do podstawowej treści strony. Kalendarz i mapa nie zostaną osadzone, ale nadal można skorzystać z bezpośrednich linków prowadzących do tych usług.',
    'Brak zgody na analitykę lub pomiar reklam nie ogranicza dostępu do treści strony ani możliwości rezerwacji gry.',
    'policy no consent impact'
)
policy = replace_once(
    policy,
    'Przy pierwszej wizycie można wybrać „Tylko niezbędne”, „Akceptuję wszystkie” albo otworzyć „Ustawienia” i zdecydować osobno o Google Analytics, Google Ads, kalendarzu LockMe oraz mapie Google. Żadna opcjonalna zgoda nie jest zaznaczona domyślnie.',
    'Przy pierwszej wizycie można wybrać „Tylko niezbędne”, „Akceptuję wszystkie” albo otworzyć „Ustawienia” i zdecydować osobno o Google Analytics oraz pomiarze Google Ads. Żadna opcjonalna zgoda nie jest zaznaczona domyślnie.',
    'policy consent management'
)
policy = replace_once(
    policy,
    'Zgodę można w każdej chwili zmienić lub wycofać przez przycisk „Ustawienia cookies” w stopce strony. Wycofanie zgody zatrzymuje dalsze ładowanie danej usługi na stronie, ale nie usuwa automatycznie danych zapisanych wcześniej przez podmiot trzeci na jego własnej domenie.',
    'Zgodę można w każdej chwili zmienić lub wycofać przez przycisk „Ustawienia cookies” w stopce strony. Wycofanie zgody zatrzymuje dalsze korzystanie przez Familock z odpowiedniej analityki lub pomiaru reklam, ale nie usuwa automatycznie danych zapisanych wcześniej przez podmiot trzeci na jego własnej domenie.',
    'policy consent withdrawal'
)
policy = replace_once(
    policy,
    '<li>Google Maps, jako dostawca interaktywnej mapy,</li>',
    '<li>Google Maps, jako zewnętrzny serwis mapowy otwierany wyłącznie po kliknięciu linku przez użytkownika,</li>',
    'policy services maps'
)
policy = replace_once(
    policy,
    'Przed włączeniem usługi użytkownik może zapoznać się z polityką odpowiedniego dostawcy. Otwarcie bezpośredniego linku do LockMe lub Google Maps powoduje przejście do serwisu zewnętrznego, w którym obowiązują zasady tego serwisu.',
    'Przed skorzystaniem z usługi użytkownik może zapoznać się z polityką odpowiedniego dostawcy. Uruchomienie kalendarza LockMe powoduje połączenie z usługą zewnętrzną, a otwarcie linku do Google Maps powoduje przejście do serwisu Google. W obu przypadkach obowiązują również zasady prywatności danego dostawcy.',
    'policy third parties'
)
policy_path.write_text(policy, encoding='utf-8')

# Basic assertions
assert 'data-cookie-service="lockme"' not in index
assert 'data-cookie-service="googleMaps"' not in index
assert 'cookie-lockme' not in index
assert 'cookie-google-maps' not in index
assert "familock_cookie_consent_v5" in index
assert 'loadLockmeWidget' in index
assert 'art. 399 ust. 3 pkt 2' in policy
print('Cookie UX patch applied successfully')
