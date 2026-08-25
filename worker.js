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
