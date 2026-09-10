(function () {
  'use strict';

  var STORAGE_KEY = 'familock_cookie_consent_v5';
  var CONSENT_VERSION = 5;
  var GA_MEASUREMENT_ID = 'G-LY7D7XH1K3';
  var leadSentAt = 0;
  var bookingViewSent = false;

  function readConsent() {
    try {
      var choice = JSON.parse(localStorage.getItem(STORAGE_KEY));
      if (!choice || choice.version !== CONSENT_VERSION) return null;
      return choice;
    } catch (e) {
      return null;
    }
  }

  function analyticsAllowed() {
    var choice = readConsent();
    return !!(choice && choice.analytics === true);
  }

  function sendAnalytics(eventName, params) {
    if (!analyticsAllowed() || typeof window.gtag !== 'function') return false;
    window.gtag('event', eventName, Object.assign({
      page_path: window.location.pathname,
      send_to: GA_MEASUREMENT_ID
    }, params || {}));
    return true;
  }

  function locationLabel(element) {
    if (!element || !element.closest) return 'page';
    if (element.closest('nav')) return 'nav';
    if (element.closest('#home')) return 'hero';
    if (element.closest('.pokoj-card')) return 'room_card';
    if (element.closest('#rezerwacja')) return 'reservation';
    if (element.closest('#kontakt')) return 'contact';
    if (element.closest('footer')) return 'footer';
    return 'page';
  }

  document.addEventListener('click', function (event) {
    var target = event.target;
    if (!target || !target.closest) return;
    var link = target.closest('a[href]');
    if (!link) return;

    var href = link.getAttribute('href') || '';
    var where = locationLabel(link);
    var text = (link.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase();

    if (/^tel:/i.test(href)) {
      sendAnalytics('contact_click', { method: 'phone', cta_location: where });
      return;
    }

    if (/^mailto:/i.test(href)) {
      sendAnalytics('contact_click', { method: 'email', cta_location: where });
      return;
    }

    try {
      var url = new URL(link.href, window.location.href);
      var host = url.hostname.toLowerCase();

      if ((host === window.location.hostname || !host) && url.hash === '#rezerwacja') {
        sendAnalytics('booking_click', { booking_method: 'onsite_calendar', cta_location: where });
        return;
      }

      // Zdarzenia wewnątrz widgetu LockMe obsługuje connect.js.
      // Nie próbujemy już zgadywać kliknięcia przez fokus iframe ani wysyłać
      // własnego zdarzenia bezpośrednio do Google Ads.
      if (host === 'lock.me' || host === 'www.lock.me' || host === 'widget.lock.me' || host.slice(-8) === '.lock.me') {
        return;
      }

      if ((host === 'facebook.com' || host === 'www.facebook.com') && text.indexOf('messenger') !== -1) {
        sendAnalytics('contact_click', { method: 'messenger', cta_location: where });
        return;
      }

      if (host === 'maps.google.com' || (host === 'www.google.com' && url.pathname.indexOf('/maps') !== -1)) {
        sendAnalytics('directions_click', { cta_location: where });
        return;
      }
    } catch (e) {}

    if (text.indexOf('voucher') !== -1) {
      sendAnalytics('voucher_click', { cta_location: where });
    }
  }, true);

  // Na stronie Starzika istnieje już własny reservation_view. booking_view
  // zostawiamy wyłącznie na stronie głównej, aby nie mnożyć tych samych sygnałów.
  var reservation = window.location.pathname === '/' ? document.getElementById('rezerwacja') : null;
  if (reservation && 'IntersectionObserver' in window) {
    var reservationObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!bookingViewSent && entry.isIntersecting && entry.intersectionRatio >= 0.35) {
          if (sendAnalytics('booking_view', { booking_method: 'lockme_widget' })) {
            bookingViewSent = true;
            reservationObserver.disconnect();
          }
        }
      });
    }, { threshold: [0.35] });
    reservationObserver.observe(reservation);
  }

  var formOk = document.getElementById('form-ok');
  if (formOk && 'MutationObserver' in window) {
    var formObserver = new MutationObserver(function () {
      var visible = window.getComputedStyle(formOk).display !== 'none';
      var now = Date.now();
      if (visible && now - leadSentAt > 5000) {
        if (sendAnalytics('generate_lead', { lead_source: 'contact_form' })) {
          leadSentAt = now;
        }
      }
    });
    formObserver.observe(formOk, { attributes: true, attributeFilter: ['style', 'class'] });
  }
})();
