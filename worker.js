export default {
  async fetch(request, env) {
    const response = await env.ASSETS.fetch(request);
    const contentType = response.headers.get('content-type') || '';

    if (!response.ok || !contentType.includes('text/html')) {
      return response;
    }

    return new HTMLRewriter()
      .on('body', {
        element(body) {
          body.append('<script src="/analytics-events.js" defer></script>', { html: true });
        }
      })
      .transform(response);
  }
};
