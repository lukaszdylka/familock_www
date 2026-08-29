from pathlib import Path

HEAD_SNIPPET = '''<script>
window.dataLayer = window.dataLayer || [];
window.gtag = window.gtag || function() { window.dataLayer.push(arguments); };
window.gtag('consent', 'default', {
  analytics_storage: 'denied',
  ad_storage: 'denied',
  ad_user_data: 'denied',
  ad_personalization: 'denied',
  wait_for_update: 500
});
window.gtag('set', 'ads_data_redaction', true);
window.gtag('js', new Date());
</script>
<script id="familock-google-tag" async src="https://www.googletagmanager.com/gtag/js?id=AW-969004050"></script>
'''


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected exactly one match, got {count}')
    return text.replace(old, new, 1)


def patch_index():
    path = Path('index.html')
    text = path.read_text(encoding='utf-8')

    marker = '<link rel="preconnect" href="https://fonts.googleapis.com" />'
    if 'id="familock-google-tag"' not in text:
        text = replace_once(text, marker, HEAD_SNIPPET + marker, 'index head tag')

    old_bootstrap = '''  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function() { window.dataLayer.push(arguments); };
  window.gtag('consent', 'default', {
    analytics_storage: 'denied',
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied'
  });
  window.gtag('set', 'ads_data_redaction', true);
  window.gtag('js', new Date());
'''
    if old_bootstrap in text:
        text = replace_once(text, old_bootstrap, '  // Google tag i domyślne stany Consent Mode są inicjalizowane w <head>.\n', 'index old bootstrap')

    text = text.replace("script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA_MEASUREMENT_ID);", "script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GOOGLE_ADS_ID);")

    old_analytics = '''  function applyAnalytics(enabled) {
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
'''
    new_analytics = '''  function applyAnalytics(enabled) {
    // Advanced Consent Mode: tag pozostaje aktywny także przy odmowie,
    // ale analytics_storage=denied blokuje zapis/odczyt cookies analitycznych.
    ensureGoogleTag();
    if (!analyticsConfigured) {
      analyticsConfigured = true;
      window.gtag('config', GA_MEASUREMENT_ID, {
        anonymize_ip: true,
        allow_google_signals: false,
        allow_ad_personalization_signals: false
      });
    }
    if (!enabled) deleteAnalyticsCookies();
  }
'''
    text = replace_once(text, old_analytics, new_analytics, 'index applyAnalytics')

    old_marketing = '''  function applyMarketing(enabled) {
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
'''
    new_marketing = '''  function applyMarketing(enabled) {
    // Google Ads jest skonfigurowany od razu; przy ad_storage=denied działa bez cookies reklamowych.
    ensureGoogleTag();
    if (!adsConfigured) {
      adsConfigured = true;
      window.gtag('config', GOOGLE_ADS_ID, {
        allow_ad_personalization_signals: false
      });
    }
    if (!enabled) deleteAdvertisingCookies();
  }
'''
    text = replace_once(text, old_marketing, new_marketing, 'index applyMarketing')

    text = text.replace('Za Twoją zgodą możemy uruchomić Google Analytics i pomiar Google Ads.', 'Tag Google działa w trybie Consent Mode. Za Twoją zgodą włączamy pełny pomiar Google Analytics i Google Ads; bez zgody nie zapisujemy cookies analitycznych ani reklamowych.')
    path.write_text(text, encoding='utf-8')


def patch_starzik():
    path = Path('starzik/index.html')
    text = path.read_text(encoding='utf-8')

    marker = '<link rel="preconnect" href="https://fonts.googleapis.com" />'
    if 'id="familock-google-tag"' not in text:
        text = replace_once(text, marker, HEAD_SNIPPET + marker, 'starzik head tag')

    old_bootstrap = "window.dataLayer=window.dataLayer||[];window.gtag=window.gtag||function(){dataLayer.push(arguments)};gtag('consent','default',{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'});gtag('set','ads_data_redaction',true);gtag('js',new Date());"
    if old_bootstrap in text:
        text = replace_once(text, old_bootstrap, "/* Google tag i Consent Mode są inicjalizowane w <head>. */", 'starzik old bootstrap')

    old_decl = "var KEY='familock_cookie_consent_v5',VERSION=5,MAX=180*24*60*60*1000,GA='G-LY7D7XH1K3',ADS='AW-969004050';var banner="
    new_decl = "var KEY='familock_cookie_consent_v5',VERSION=5,MAX=180*24*60*60*1000,GA='G-LY7D7XH1K3',ADS='AW-969004050';var gaConfigured=false,adsConfigured=false;var banner="
    text = replace_once(text, old_decl, new_decl, 'starzik config flags')

    text = text.replace("s.src='https://www.googletagmanager.com/gtag/js?id='+GA", "s.src='https://www.googletagmanager.com/gtag/js?id='+ADS")

    old_apply = "function apply(c){gtag('consent','update',{analytics_storage:c.analytics?'granted':'denied',ad_storage:c.marketing?'granted':'denied',ad_user_data:c.marketing?'granted':'denied',ad_personalization:'denied'});if(c.analytics||c.marketing)tag();if(c.analytics)gtag('config',GA,{allow_google_signals:false,allow_ad_personalization_signals:false});if(c.marketing)gtag('config',ADS,{allow_ad_personalization_signals:false})}"
    new_apply = "function apply(c){gtag('consent','update',{analytics_storage:c.analytics?'granted':'denied',ad_storage:c.marketing?'granted':'denied',ad_user_data:c.marketing?'granted':'denied',ad_personalization:'denied'});tag();if(!gaConfigured){gaConfigured=true;gtag('config',GA,{allow_google_signals:false,allow_ad_personalization_signals:false})}if(!adsConfigured){adsConfigured=true;gtag('config',ADS,{allow_ad_personalization_signals:false})}}"
    text = replace_once(text, old_apply, new_apply, 'starzik apply')

    text = text.replace('Za Twoją zgodą możemy uruchomić Google Analytics i pomiar Google Ads.', 'Tag Google działa w trybie Consent Mode. Za Twoją zgodą włączamy pełny pomiar Google Analytics i Google Ads; bez zgody nie zapisujemy cookies analitycznych ani reklamowych.')
    path.write_text(text, encoding='utf-8')


def patch_policy():
    path = Path('polityka.html')
    text = path.read_text(encoding='utf-8')

    old_g = '<p>Po wyrażeniu zgody Google Analytics służy do tworzenia statystyk odwiedzin, oceny sposobu korzystania ze strony i jej ulepszania.<br>\n    <strong>Podstawa prawna:</strong> <span class="basis-tag">art. 6 ust. 1 lit. a RODO</span> — zgoda osoby, której dane dotyczą. Zgoda obejmuje również zapis i odczyt informacji w urządzeniu użytkownika.</p>'
    new_g = '<p>Tag Google działa w trybie Consent Mode. Przed wyrażeniem zgody stan <code>analytics_storage</code> pozostaje ustawiony na <code>denied</code>, dlatego nie zapisujemy ani nie odczytujemy cookies Google Analytics. Google może otrzymywać ograniczone sygnały techniczne bez identyfikatorów cookies. Po wyrażeniu zgody Google Analytics służy do tworzenia statystyk odwiedzin, oceny sposobu korzystania ze strony i jej ulepszania.<br>\n    <strong>Podstawa prawna dla pełnego pomiaru i zapisu/odczytu informacji w urządzeniu:</strong> <span class="basis-tag">art. 6 ust. 1 lit. a RODO</span> — zgoda osoby, której dane dotyczą.</p>'
    text = replace_once(text, old_g, new_g, 'policy analytics')

    old_h = '<p>Po wyrażeniu odrębnej zgody tag Google Ads służy do pomiaru skuteczności kampanii reklamowych i konwersji. Personalizacja reklam pozostaje wyłączona.<br>\n    <strong>Podstawa prawna:</strong> <span class="basis-tag">art. 6 ust. 1 lit. a RODO</span> — zgoda osoby, której dane dotyczą. Zgoda obejmuje również zapis i odczyt informacji w urządzeniu użytkownika.</p>'
    new_h = '<p>Tag Google Ads działa w trybie Consent Mode. Przed wyrażeniem zgody stany <code>ad_storage</code> i <code>ad_user_data</code> pozostają ustawione na <code>denied</code>, dlatego nie zapisujemy ani nie odczytujemy cookies reklamowych. Google może otrzymywać ograniczone sygnały techniczne bez identyfikatorów cookies. Po wyrażeniu odrębnej zgody Google Ads służy do pełnego pomiaru skuteczności kampanii i konwersji. Personalizacja reklam pozostaje wyłączona.<br>\n    <strong>Podstawa prawna dla pełnego pomiaru i zapisu/odczytu informacji w urządzeniu:</strong> <span class="basis-tag">art. 6 ust. 1 lit. a RODO</span> — zgoda osoby, której dane dotyczą.</p>'
    text = replace_once(text, old_h, new_h, 'policy ads')

    old_recipient = '<li>dostawcy usług pomiarowych <strong>Google Analytics i Google Ads, Google Ireland Limited</strong>, wyłącznie po wyrażeniu odpowiedniej zgody</li>'
    new_recipient = '<li>dostawcy usług pomiarowych <strong>Google Analytics i Google Ads, Google Ireland Limited</strong>; przed zgodą tag działa w ograniczonym trybie Consent Mode bez cookies analitycznych i reklamowych, a pełny pomiar jest uruchamiany po odpowiedniej zgodzie</li>'
    text = replace_once(text, old_recipient, new_recipient, 'policy recipient')
    path.write_text(text, encoding='utf-8')


patch_index()
patch_starzik()
patch_policy()

# Usuń pliki techniczne po wykonaniu, aby repo pozostało czyste.
for temporary in [Path('.advanced-consent-trigger'), Path('.github/workflows/advanced-consent.yml'), Path('.github/advanced_consent_patch.py')]:
    if temporary.exists():
        temporary.unlink()

print('Advanced Consent Mode patch applied successfully.')
