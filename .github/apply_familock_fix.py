from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)


index_path = Path('index.html')
index = index_path.read_text(encoding='utf-8')

index = replace_once(
    index,
    'Strona używa danych niezbędnych do działania. Kalendarz LockMe, mapa Google i Google Analytics są uruchamiane wyłącznie zgodnie z wyborem użytkownika w ustawieniach cookies. Nie korzystamy z Meta Pixel ani innych narzędzi marketingowych.',
    'Strona używa danych niezbędnych do działania. Kalendarz LockMe, mapa Google, Google Analytics i pomiar Google Ads są uruchamiane wyłącznie zgodnie z wyborem użytkownika w ustawieniach cookies. Nie korzystamy z Meta Pixel, a personalizacja reklam Google pozostaje wyłączona.',
    'privacy summary'
)

index = replace_once(
    index,
    'Niezbędne dane pozwalają zapamiętać Twój wybór. Za Twoją zgodą możemy też uruchomić Google Analytics, kalendarz LockMe i mapę Google. Usługi te mogą zapisywać własne cookies oraz otrzymać informacje o urządzeniu. Bez zgody strona nadal działa. Szczegóły znajdziesz w <a href="/polityka.html#s15">Polityce Cookies</a>.',
    'Niezbędne dane pozwalają zapamiętać Twój wybór. Za Twoją zgodą możemy też uruchomić Google Analytics, pomiar Google Ads, kalendarz LockMe i mapę Google. Usługi te mogą zapisywać własne cookies oraz otrzymać informacje o urządzeniu. Bez zgody strona nadal działa. Szczegóły znajdziesz w <a href="/polityka.html#s15">Polityce Cookies</a>.',
    'cookie banner summary'
)

index = replace_once(
    index,
    'Możesz wyrazić zgodę osobno na analitykę, kalendarz LockMe i mapę Google. Narzędzia marketingowe nie są obecnie używane.',
    'Możesz wyrazić zgodę osobno na analitykę, pomiar Google Ads, kalendarz LockMe i mapę Google.',
    'cookie settings intro'
)

index = replace_once(
    index,
    '''        <div class="cookie-category">
          <div>
            <div class="cookie-category-name">Marketingowe</div>
            <div class="cookie-category-copy">Meta Pixel i inne narzędzia reklamowe nie są obecnie używane.</div>
          </div>
          <span class="cookie-status">Nieużywane</span>
        </div>''',
    '''        <div class="cookie-category">
          <div>
            <div class="cookie-category-name">Reklamowe</div>
            <div class="cookie-category-copy">Google Ads służy do pomiaru skuteczności reklam i konwersji. Personalizacja reklam pozostaje wyłączona.</div>
          </div>
          <label class="cookie-toggle">
            <input id="cookie-marketing" type="checkbox" aria-label="Zezwól na pomiar Google Ads">
            <span class="cookie-switch" aria-hidden="true"></span>
          </label>
        </div>''',
    'marketing category'
)

index = replace_once(
    index,
    "  var STORAGE_KEY = 'familock_cookie_consent_v3';\n  var CONSENT_VERSION = 3;",
    "  var STORAGE_KEY = 'familock_cookie_consent_v4';\n  var CONSENT_VERSION = 4;",
    'consent version'
)

index = replace_once(
    index,
    "  var GA_MEASUREMENT_ID = 'G-LY7D7XH1K3';\n  var currentConsent = null;\n  var analyticsLoaded = false;",
    """  var GA_MEASUREMENT_ID = 'G-LY7D7XH1K3';
  var GOOGLE_ADS_ID = 'AW-969004050';
  var currentConsent = null;
  var googleTagLoaded = false;
  var analyticsConfigured = false;
  var adsConfigured = false;

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function() { window.dataLayer.push(arguments); };
  window.gtag('consent', 'default', {
    analytics_storage: 'denied',
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied'
  });
  window.gtag('set', 'ads_data_redaction', true);
  window.gtag('js', new Date());""",
    'google tag variables'
)

index = replace_once(
    index,
    "  var analyticsChoice = document.getElementById('cookie-analytics');",
    "  var analyticsChoice = document.getElementById('cookie-analytics');\n  var marketingChoice = document.getElementById('cookie-marketing');",
    'marketing choice'
)

index = replace_once(
    index,
    "      googleMaps: false,\n      analytics: false,\n      updatedAt: null",
    "      googleMaps: false,\n      analytics: false,\n      marketing: false,\n      updatedAt: null",
    'empty consent'
)

index = replace_once(
    index,
    "        typeof saved.googleMaps !== 'boolean' ||\n        typeof saved.analytics !== 'boolean' ||",
    "        typeof saved.googleMaps !== 'boolean' ||\n        typeof saved.analytics !== 'boolean' ||\n        typeof saved.marketing !== 'boolean' ||",
    'read consent validation'
)

index = replace_once(
    index,
    "      googleMaps: !!choice.googleMaps,\n      analytics: !!choice.analytics,\n      updatedAt: new Date().toISOString()",
    "      googleMaps: !!choice.googleMaps,\n      analytics: !!choice.analytics,\n      marketing: !!choice.marketing,\n      updatedAt: new Date().toISOString()",
    'write consent'
)

old_google_functions = """  function deleteAnalyticsCookies() {
    var names = document.cookie.split(';').map(function(cookie) {
      return cookie.split('=')[0].trim();
    }).filter(function(name) {
      return name === '_ga' || name.indexOf('_ga_') === 0;
    });
    var domains = ['', location.hostname, '.' + location.hostname, '.familock.pl'];
    names.forEach(function(name) {
      domains.forEach(function(domain) {
        var domainPart = domain ? '; domain=' + domain : '';
        document.cookie = name + '=; Max-Age=0; path=/' + domainPart + '; SameSite=Lax';
      });
    });
  }

  function loadGoogleAnalytics() {
    window['ga-disable-' + GA_MEASUREMENT_ID] = false;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function() { window.dataLayer.push(arguments); };

    if (analyticsLoaded || document.getElementById('familock-ga4')) {
      analyticsLoaded = true;
      window.gtag('consent', 'update', { analytics_storage: 'granted' });
      window.gtag('config', GA_MEASUREMENT_ID, {
        anonymize_ip: true,
        allow_google_signals: false,
        allow_ad_personalization_signals: false
      });
      return;
    }

    analyticsLoaded = true;
    var script = document.createElement('script');
    script.id = 'familock-ga4';
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA_MEASUREMENT_ID);
    script.onload = function() {
      window.gtag('js', new Date());
      window.gtag('consent', 'update', { analytics_storage: 'granted' });
      window.gtag('config', GA_MEASUREMENT_ID, {
        anonymize_ip: true,
        allow_google_signals: false,
        allow_ad_personalization_signals: false
      });
    };
    document.head.appendChild(script);
  }

  function applyAnalytics(enabled) {
    if (enabled) {
      loadGoogleAnalytics();
      return;
    }
    window['ga-disable-' + GA_MEASUREMENT_ID] = true;
    if (typeof window.gtag === 'function') {
      window.gtag('consent', 'update', { analytics_storage: 'denied' });
    }
    deleteAnalyticsCookies();
  }

  function applyConsent(choice) {
    var effective = choice || emptyConsent();
    applyService('lockme', effective.lockme);
    applyService('googleMaps', effective.googleMaps);
    applyAnalytics(effective.analytics);
  }"""

new_google_functions = """  function deleteAnalyticsCookies() {
    var names = document.cookie.split(';').map(function(cookie) {
      return cookie.split('=')[0].trim();
    }).filter(function(name) {
      return name === '_ga' || name.indexOf('_ga_') === 0;
    });
    deleteCookiesByName(names);
  }

  function deleteAdvertisingCookies() {
    var names = document.cookie.split(';').map(function(cookie) {
      return cookie.split('=')[0].trim();
    }).filter(function(name) {
      return name.indexOf('_gcl_') === 0 || name.indexOf('_gac_') === 0;
    });
    deleteCookiesByName(names);
  }

  function deleteCookiesByName(names) {
    var domains = ['', location.hostname, '.' + location.hostname, '.familock.pl'];
    names.forEach(function(name) {
      domains.forEach(function(domain) {
        var domainPart = domain ? '; domain=' + domain : '';
        document.cookie = name + '=; Max-Age=0; path=/' + domainPart + '; SameSite=Lax';
      });
    });
  }

  function ensureGoogleTag() {
    if (googleTagLoaded || document.getElementById('familock-google-tag')) {
      googleTagLoaded = true;
      return;
    }
    googleTagLoaded = true;
    var script = document.createElement('script');
    script.id = 'familock-google-tag';
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA_MEASUREMENT_ID);
    document.head.appendChild(script);
  }

  function updateGoogleConsent(choice) {
    window.gtag('consent', 'update', {
      analytics_storage: choice.analytics ? 'granted' : 'denied',
      ad_storage: choice.marketing ? 'granted' : 'denied',
      ad_user_data: choice.marketing ? 'granted' : 'denied',
      ad_personalization: 'denied'
    });
  }

  function applyAnalytics(enabled) {
    window['ga-disable-' + GA_MEASUREMENT_ID] = !enabled;
    if (enabled) {
      ensureGoogleTag();
      if (!analyticsConfigured) {
        analyticsConfigured = true;
        window.gtag('config', GA_MEASUREMENT_ID, {
          anonymize_ip: true,
          allow_google_signals: false,
          allow_ad_personalization_signals: false
        });
      }
      return;
    }
    deleteAnalyticsCookies();
  }

  function applyMarketing(enabled) {
    if (enabled) {
      ensureGoogleTag();
      if (!adsConfigured) {
        adsConfigured = true;
        window.gtag('config', GOOGLE_ADS_ID, {
          allow_ad_personalization_signals: false
        });
      }
      return;
    }
    deleteAdvertisingCookies();
  }

  function applyConsent(choice) {
    var effective = choice || emptyConsent();
    applyService('lockme', effective.lockme);
    applyService('googleMaps', effective.googleMaps);
    updateGoogleConsent(effective);
    applyAnalytics(effective.analytics);
    applyMarketing(effective.marketing);
  }"""

index = replace_once(index, old_google_functions, new_google_functions, 'google functions')

index = replace_once(
    index,
    "      analyticsChoice.checked = !!base.analytics;",
    "      analyticsChoice.checked = !!base.analytics;\n      marketingChoice.checked = !!base.marketing;",
    'settings state'
)

index = replace_once(
    index,
    "    choice.googleMaps = true;\n    choice.analytics = true;\n    writeConsent(choice);",
    "    choice.googleMaps = true;\n    choice.analytics = true;\n    choice.marketing = true;\n    writeConsent(choice);",
    'accept all'
)

index = replace_once(
    index,
    "    choice.googleMaps = !!mapsChoice.checked;\n    choice.analytics = !!analyticsChoice.checked;\n    writeConsent(choice);",
    "    choice.googleMaps = !!mapsChoice.checked;\n    choice.analytics = !!analyticsChoice.checked;\n    choice.marketing = !!marketingChoice.checked;\n    writeConsent(choice);",
    'save settings'
)

index = replace_once(
    index,
    "      googleMaps: currentConsent.googleMaps,\n      analytics: currentConsent.analytics,\n      updatedAt: currentConsent.updatedAt",
    "      googleMaps: currentConsent.googleMaps,\n      analytics: currentConsent.analytics,\n      marketing: currentConsent.marketing,\n      updatedAt: currentConsent.updatedAt",
    'enable service consent copy'
)

index_path.write_text(index, encoding='utf-8')

policy_path = Path('polityka.html')
policy = policy_path.read_text(encoding='utf-8')

policy = replace_once(
    policy,
    'dane techniczne i statystyczne dotyczące korzystania ze strony, takie jak identyfikator internetowy, przybliżona lokalizacja, informacje o urządzeniu, przeglądarce i przebiegu wizyty, jeżeli wyrazisz zgodę na Google Analytics',
    'dane techniczne i statystyczne dotyczące korzystania ze strony oraz pomiaru skuteczności reklam, takie jak identyfikator internetowy, przybliżona lokalizacja, informacje o urządzeniu, przeglądarce i przebiegu wizyty, jeżeli wyrazisz zgodę na Google Analytics lub Google Ads',
    'policy data scope'
)

policy = replace_once(
    policy,
    '''    <h3>g) Analiza korzystania ze strony</h3>
    <p>Po wyrażeniu zgody Google Analytics służy do tworzenia statystyk odwiedzin, oceny sposobu korzystania ze strony i jej ulepszania.<br>
    <strong>Podstawa prawna:</strong> <span class="basis-tag">art. 6 ust. 1 lit. a RODO</span> — zgoda osoby, której dane dotyczą. Zgoda obejmuje również zapis i odczyt informacji w urządzeniu użytkownika.</p>''',
    '''    <h3>g) Analiza korzystania ze strony</h3>
    <p>Po wyrażeniu zgody Google Analytics służy do tworzenia statystyk odwiedzin, oceny sposobu korzystania ze strony i jej ulepszania.<br>
    <strong>Podstawa prawna:</strong> <span class="basis-tag">art. 6 ust. 1 lit. a RODO</span> — zgoda osoby, której dane dotyczą. Zgoda obejmuje również zapis i odczyt informacji w urządzeniu użytkownika.</p>

    <h3>h) Pomiar skuteczności reklam</h3>
    <p>Po wyrażeniu odrębnej zgody tag Google Ads służy do pomiaru skuteczności kampanii reklamowych i konwersji. Personalizacja reklam pozostaje wyłączona.<br>
    <strong>Podstawa prawna:</strong> <span class="basis-tag">art. 6 ust. 1 lit. a RODO</span> — zgoda osoby, której dane dotyczą. Zgoda obejmuje również zapis i odczyt informacji w urządzeniu użytkownika.</p>''',
    'policy ads purpose'
)

policy = replace_once(
    policy,
    '<li>dostawcy usługi statystycznej <strong>Google Analytics, Google Ireland Limited</strong>, wyłącznie po wyrażeniu zgody</li>',
    '<li>dostawcy usług pomiarowych <strong>Google Analytics i Google Ads, Google Ireland Limited</strong>, wyłącznie po wyrażeniu odpowiedniej zgody</li>',
    'policy recipients'
)

policy = replace_once(
    policy,
    'Strona internetowa Familock korzysta z pamięci przeglądarki oraz, po uzyskaniu zgody użytkownika, z usług funkcjonalnych i analitycznych. Pliki cookies i podobne technologie mogą zapisywać lub odczytywać informacje na urządzeniu użytkownika.',
    'Strona internetowa Familock korzysta z pamięci przeglądarki oraz, po uzyskaniu zgody użytkownika, z usług funkcjonalnych, analitycznych i reklamowych. Pliki cookies i podobne technologie mogą zapisywać lub odczytywać informacje na urządzeniu użytkownika.',
    'policy cookie intro'
)

policy = replace_once(
    policy,
    'Strona korzysta z Google Analytics 4. Nie korzysta z Meta Pixel ani innych narzędzi marketingowych.',
    'Strona korzysta z Google Analytics 4 oraz, po odrębnej zgodzie, z tagu Google Ads AW-969004050 do pomiaru skuteczności reklam i konwersji. Nie korzysta z Meta Pixel. Personalizacja reklam Google pozostaje wyłączona.',
    'policy google ads intro'
)

policy = replace_once(
    policy,
    '<p><strong>e) Marketingowe</strong>. Nie są obecnie używane.</p>',
    '<p><strong>e) Reklamowe</strong>. Po wyrażeniu odrębnej zgody strona uruchamia tag Google Ads z identyfikatorem AW-969004050 w celu pomiaru skuteczności kampanii i konwersji. Personalizacja reklam pozostaje wyłączona.</p>',
    'policy ads category'
)

policy = replace_once(
    policy,
    '''    <h3>Cookies Google Analytics</h3>
    <p>Google Analytics może zapisywać w domenie familock.pl pliki <strong>_ga</strong>, służący do odróżniania użytkowników, oraz <strong>_ga_ID</strong>, gdzie ID oznacza identyfikator usługi, służący do zachowania stanu sesji. Ich domyślny okres ważności wynosi do 2 lat. Pliki te nie są ustawiane przed wyrażeniem zgody.</p>''',
    '''    <h3>Cookies Google Analytics i Google Ads</h3>
    <p>Google Analytics może zapisywać w domenie familock.pl pliki <strong>_ga</strong>, służący do odróżniania użytkowników, oraz <strong>_ga_ID</strong>, gdzie ID oznacza identyfikator usługi, służący do zachowania stanu sesji. Google Ads może zapisywać pliki zaczynające się od <strong>_gcl_</strong>, wykorzystywane do pomiaru kliknięć reklam i konwersji. Pliki te nie są ustawiane przed wyrażeniem odpowiedniej zgody.</p>''',
    'policy cookie names'
)

policy = replace_once(
    policy,
    'Google Analytics, LockMe i Google Maps są uruchamiane wyłącznie po dobrowolnej, świadomej i jednoznacznej zgodzie wyrażonej w banerze cookies lub przez przycisk przy danej usłudze.',
    'Google Analytics, Google Ads, LockMe i Google Maps są uruchamiane wyłącznie po dobrowolnej, świadomej i jednoznacznej zgodzie wyrażonej w banerze cookies lub przez przycisk przy danej usłudze.',
    'policy consent basis'
)

policy = replace_once(
    policy,
    'Przy pierwszej wizycie można wybrać „Tylko niezbędne”, „Akceptuję wszystkie” albo otworzyć „Ustawienia” i zdecydować osobno o Google Analytics, kalendarzu LockMe oraz mapie Google. Żadna opcjonalna zgoda nie jest zaznaczona domyślnie.',
    'Przy pierwszej wizycie można wybrać „Tylko niezbędne”, „Akceptuję wszystkie” albo otworzyć „Ustawienia” i zdecydować osobno o Google Analytics, Google Ads, kalendarzu LockMe oraz mapie Google. Żadna opcjonalna zgoda nie jest zaznaczona domyślnie.',
    'policy consent management'
)

policy = replace_once(
    policy,
    '      <li>Google Analytics, jako dostawca statystyk korzystania ze strony,</li>',
    '      <li>Google Analytics, jako dostawca statystyk korzystania ze strony,</li>\n      <li>Google Ads, jako dostawca pomiaru skuteczności reklam i konwersji,</li>',
    'policy services list'
)

policy_path.write_text(policy, encoding='utf-8')

Path('wrangler.jsonc').write_text('''{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "familock",
  "compatibility_date": "2026-07-22",
  "observability": {
    "enabled": true
  },
  "assets": {
    "directory": "."
  },
  "compatibility_flags": [
    "nodejs_compat"
  ]
}
''', encoding='utf-8')
