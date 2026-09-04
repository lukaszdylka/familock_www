const LEGACY_GOOGLE_ADS_ID = 'AW-969004050';
const GOOGLE_ADS_ID = 'AW-18392650191';

const googleAdsIdShim = `<script>
(function () {
  var legacyAdsId = '${LEGACY_GOOGLE_ADS_ID}';
  var currentAdsId = '${GOOGLE_ADS_ID}';

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () {
    if (arguments.length > 1 && arguments[1] === legacyAdsId) {
      arguments[1] = currentAdsId;
    }
    window.dataLayer.push(arguments);
  };
})();
</script>`;

const lockMeConnectScript = '<script src="https://widget.lock.me/connect.js" type="text/javascript" crossorigin="anonymous" async></script>';
const lockMeProfileLink = '<div class="lockme-profile-link" style="margin-top:.85rem;text-align:right"><a href="https://lock.me/pl/poland/slaskie/swietochlowice/escape-room/tajemnica-garazu/14685-starzik" target="_blank" rel="noopener noreferrer" style="display:inline-flex;align-items:center;gap:.45rem;padding:.2rem 0;color:var(--cream2);font-family:var(--fd);font-size:.72rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;text-decoration:none;border-bottom:1px solid var(--border3);transition:color .2s,border-color .2s">Zobacz Starzika na LockMe <span aria-hidden="true">↗</span></a></div>';
const lockMeSocialButton = '<a href="https://lock.me/pl/poland/slaskie/swietochlowice/escape-room/tajemnica-garazu/14685-starzik" target="_blank" rel="noopener noreferrer" class="soc-btn" aria-label="LockMe"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7.07.07l2-2a5 5 0 0 0-7.07-7.07l-1.15 1.15"/><path d="M14 11a5 5 0 0 0-7.07-.07l-2 2A5 5 0 0 0 12 20l1.15-1.15"/></svg>Lockme</a>';
const lateNightPriceNote = '<p class="price-note" style="margin-top:.85rem;color:var(--red-glow)">Piątek i sobota, godz. 23:30: obowiązuje dopłata 20 zł do ceny grupy.</p>';

export default {
  async fetch(request, env) {
    const response = await env.ASSETS.fetch(request);
    const contentType = response.headers.get('content-type') || '';

    if (!response.ok || !contentType.includes('text/html')) {
      return response;
    }

    const pathname = new URL(request.url).pathname;
    const shouldLoadLockMe = pathname === '/' || pathname === '/starzik' || pathname.startsWith('/starzik/');
    let starzikPriceBlockIndex = 0;

    return new HTMLRewriter()
      .on('head', {
        element(head) {
          head.append(googleAdsIdShim, { html: true });
          if (shouldLoadLockMe) {
            head.append(lockMeConnectScript, { html: true });
          }
        }
      })
      .on('.booking-widget-wrap', {
        element(bookingWidget) {
          if (shouldLoadLockMe) {
            bookingWidget.after(lockMeProfileLink, { html: true });
          }
        }
      })
      .on('.booking-wrap', {
        element(bookingWidget) {
          if (shouldLoadLockMe) {
            bookingWidget.after(lockMeProfileLink, { html: true });
          }
        }
      })
      .on('#kontakt .socials', {
        element(socials) {
          if (pathname === '/') {
            socials.append(lockMeSocialButton, { html: true });
          }
        }
      })
      .on('#tab-starzik .price-block', {
        element(priceBlock) {
          starzikPriceBlockIndex += 1;
          if (starzikPriceBlockIndex === 2) {
            priceBlock.append(lateNightPriceNote, { html: true });
          }
        }
      })
      .on('body', {
        element(body) {
          body.append('<script src="/analytics-events.js" defer></script>', { html: true });
        }
      })
      .transform(response);
  }
};
