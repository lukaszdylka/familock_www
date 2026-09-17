const lockMeProfileLink = '<div class="lockme-profile-link" style="margin-top:.85rem;text-align:right"><a href="https://lock.me/pl/poland/slaskie/swietochlowice/escape-room/tajemnica-garazu/14685-starzik" target="_blank" rel="noopener noreferrer" style="display:inline-flex;align-items:center;gap:.45rem;padding:.2rem 0;color:var(--cream2);font-family:var(--fd);font-size:.72rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;text-decoration:none;border-bottom:1px solid var(--border3);transition:color .2s,border-color .2s">Zobacz Starzika na LockMe <span aria-hidden="true">↗</span></a></div>';
const lockMeSocialButton = '<a href="https://lock.me/pl/poland/slaskie/swietochlowice/escape-room/tajemnica-garazu/14685-starzik" target="_blank" rel="noopener noreferrer" class="soc-btn" aria-label="LockMe"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7.07.07l2-2a5 5 0 0 0-7.07-7.07l-1.15 1.15"/><path d="M14 11a5 5 0 0 0-7.07-.07l-2 2A5 5 0 0 0 12 20l1.15-1.15"/></svg>Lockme</a>';
const lateNightPriceNote = '<p class="price-note" style="margin-top:.85rem;color:var(--red-glow)">Piątek i sobota, godz. 23:30: obowiązuje dopłata 20 zł do ceny grupy.</p>';

const oldGroupInfo = 'Grupy szkolne i firmowe – <strong style="color:var(--cream)">specjalne warunki.</strong>';
const newGroupInfo = 'Urodziny, szkoły i małe zespoły – <strong style="color:var(--cream)"><a href="/dla-szkol-i-firm/" style="color:inherit;text-decoration:underline;text-underline-offset:3px">sprawdź zasady dla grup</a>.</strong>';

const oldGroupFaq = '<div class="faq-item"><button class="faq-q" type="button" aria-expanded="false" aria-controls="faq-a-12" onclick="toggleFaq(this)"><span>Czy organizujecie gry dla szkół i firm?</span><span class="faq-ico" aria-hidden="true">+</span></button><div class="faq-a" id="faq-a-12">Tak. Dla grup szkolnych i firmowych możemy ustalić odpowiednią godzinę oraz szczegóły wizyty. Skontaktujcie się z nami przed rezerwacją.</div></div>';
const newGroupFaq = '<div class="faq-item"><button class="faq-q" type="button" aria-expanded="false" aria-controls="faq-a-12" onclick="toggleFaq(this)"><span>Czy Familock nadaje się na urodziny, wyjście szkolne lub firmowe?</span><span class="faq-ico" aria-hidden="true">+</span></button><div class="faq-a" id="faq-a-12">Tak, jeśli chodzi o małą grupę. Starzik jest przeznaczony standardowo dla 2–5 osób. Przy urodzinach po wcześniejszym uzgodnieniu może zagrać maksymalnie 6 osób. Nie mamy sali urodzinowej, cateringu ani przestrzeni na większe imprezy. W przypadku szkoły zapraszamy np. niewielką grupę uczniów w ramach nagrody, koła zainteresowań lub samorządu. <a href="/dla-szkol-i-firm/">Zobacz szczegóły dla grup i okazji.</a></div></div>';

export default {
  async fetch(request, env) {
    const response = await env.ASSETS.fetch(request);
    const contentType = response.headers.get('content-type') || '';

    if (!response.ok || !contentType.includes('text/html')) {
      return response;
    }

    const pathname = new URL(request.url).pathname;
    const isBookingPage = pathname === '/' || pathname === '/starzik' || pathname.startsWith('/starzik/');
    let starzikPriceBlockIndex = 0;

    const headers = new Headers(response.headers);
    headers.delete('content-length');
    headers.delete('content-encoding');
    headers.delete('etag');

    let html = await response.text();

    if (pathname === '/') {
      html = html
        .replace(oldGroupInfo, newGroupInfo)
        .replace(oldGroupFaq, newGroupFaq)
        .replace('<a href="/dla-szkol-i-firm/">Szkoły i firmy</a>', '<a href="/dla-szkol-i-firm/">Grupy i okazje</a>');
    }

    const normalizedResponse = new Response(html, {
      status: response.status,
      statusText: response.statusText,
      headers
    });

    return new HTMLRewriter()
      .on('.booking-widget-wrap', {
        element(bookingWidget) {
          if (isBookingPage) {
            bookingWidget.after(lockMeProfileLink, { html: true });
          }
        }
      })
      .on('.booking-wrap', {
        element(bookingWidget) {
          if (isBookingPage) {
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
          body.append('<script src="/analytics-events.js" defer></script><script src="/site-content-runtime.js?v=1" defer></script>', { html: true });
        }
      })
      .transform(normalizedResponse);
  }
};
