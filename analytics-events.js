(function () {
  'use strict';

  var STORAGE_KEY = 'familock_cookie_consent_v5';
  var CONSENT_VERSION = 5;
  var GA_MEASUREMENT_ID = 'G-LY7D7XH1K3';
  var GOOGLE_ADS_ID = 'AW-18392650191';
  var leadSentAt = 0;
  var bookingViewSent = false;
  var lockmeAnalyticsSent = false;
  var lockmeAdsSent = false;

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

  function marketingAllowed() {
    var choice = readConsent();
    return !!(choice && choice.marketing === true);
  }

  function sendAnalytics(eventName, params) {
    if (!analyticsAllowed() || typeof window.gtag !== 'function') return false;
    window.gtag('event', eventName, Object.assign({
      page_path: window.location.pathname,
      send_to: GA_MEASUREMENT_ID
    }, params || {}));
    return true;
  }

  function sendAds(eventName, params) {
    if (!marketingAllowed() || typeof window.gtag !== 'function') return false;
    window.gtag('event', eventName, Object.assign({
      page_path: window.location.pathname,
      send_to: GOOGLE_ADS_ID
    }, params || {}));
    return true;
  }

  function sendLockmeClick(params) {
    var eventParams = Object.assign({ booking_method: 'lockme_widget' }, params || {});
    var sent = false;

    if (!lockmeAnalyticsSent && sendAnalytics('lockme_click', eventParams)) {
      lockmeAnalyticsSent = true;
      sent = true;
    }

    if (!lockmeAdsSent && sendAds('lockme_click', eventParams)) {
      lockmeAdsSent = true;
      sent = true;
    }

    return sent;
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

      if (host === 'lock.me' || host === 'www.lock.me' || host === 'widget.lock.me' || host.slice(-8) === '.lock.me') {
        sendLockmeClick({ interaction_type: 'external_link', cta_location: where });
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

  var reservation = document.getElementById('rezerwacja');
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

  var lockmeFrame = document.getElementById('booking-lockme-frame');
  if (lockmeFrame) {
    window.addEventListener('blur', function () {
      window.setTimeout(function () {
        if (document.activeElement === lockmeFrame) {
          sendLockmeClick({ interaction_type: 'iframe_focus', cta_location: 'reservation' });
        }
      }, 50);
    });
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
