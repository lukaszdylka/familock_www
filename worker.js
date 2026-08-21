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

export default {
  async fetch(request, env) {
    const response = await env.ASSETS.fetch(request);
    const contentType = response.headers.get('content-type') || '';

    if (!response.ok || !contentType.includes('text/html')) {
      return response;
    }

    return new HTMLRewriter()
      .on('head', {
        element(head) {
          head.append(googleAdsIdShim, { html: true });
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
