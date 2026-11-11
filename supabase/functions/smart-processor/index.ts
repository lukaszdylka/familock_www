// Supabase Edge Function: most ElevenLabs Agent <-> LockMe API
// Trasy: POST /rooms | /slots | /reserve | /post-call ; GET /oauth-start?key=… | /oauth-callback
import { createClient } from "npm:@supabase/supabase-js@2";

const env = (k: string) => Deno.env.get(k) ?? "";
const sb = createClient(env("SUPABASE_URL"), env("SUPABASE_SERVICE_ROLE_KEY"));

// ---------- KONFIGURACJA ----------
// ROOMS_JSON, np.: {"pokoj-a":{"id":123,"nazwa":"Nazwa A","opis":"…","osoby":"2-5","czas":60,"cena":"od 160 zł"}}
const ROOMS: Record<string, { id: number; nazwa: string; [k: string]: unknown }> =
  JSON.parse(env("ROOMS_JSON") || "{}");

const LOCKME = {
  base: env("LOCKME_API") || "https://api.lock.me/v2.6", // potwierdzone w Swaggerze
  tokenUrl: env("LOCKME_TOKEN_URL") || "https://api.lock.me/access_token", // z oauth2-lockme
  authUrl: env("LOCKME_AUTH_URL") || "https://api.lock.me/authorize",      // z oauth2-lockme
  // ścieżki potwierdzone w kodzie lockme-sdk (PHP)
  path: {
    dateSettings: (r: number, d: string) => `/room/${r}/date/${d}`,
    daySettings: (r: number, day: number) => `/room/${r}/day/${day}`,  // 0 = poniedziałek … 6 = niedziela
    reservations: (r: number, d: string) => `/room/${r}/reservations/${d}`,
    addReservation: (r: number) => `/room/${r}/reservation`,           // metoda PUT
  },
};
const MIN_LEAD_MIN = 60; // nie oferuj terminów bliższych niż 60 min
const TZ = "Europe/Warsaw";

// ---------- CENNIK (łączna cena za grę, zł) ----------
// weekday = pon–czw; weekend = pt–nd oraz święta. early = wejścia do 18:30, late = od 20:30 (21:00 / niedz. 20:30)
const PRICING = {
  weekday: { early: { 2: 250, 3: 310, 4: 360, 5: 400 }, late: { 2: 270, 3: 330, 4: 380, 5: 420 } },
  weekend: { early: { 2: 280, 3: 350, 4: 400, 5: 450 }, late: { 2: 300, 3: 370, 4: 420, 5: 470 } },
};
const LATE_FROM_MIN = 20 * 60 + 30;

function easterDate(y: number) {
  const a = y % 19, b = Math.floor(y / 100), c = y % 100, d = Math.floor(b / 4), e = b % 4;
  const f = Math.floor((b + 8) / 25), g = Math.floor((b - f + 1) / 3);
  const h = (19 * a + b - d - g + 15) % 30, i = Math.floor(c / 4), k = c % 4;
  const l = (32 + 2 * e + 2 * i - h - k) % 7, m = Math.floor((a + 11 * h + 22 * l) / 451);
  const month = Math.floor((h + l - 7 * m + 114) / 31), day = ((h + l - 7 * m + 114) % 31) + 1;
  return Date.UTC(y, month - 1, day);
}

function isHoliday(date: string) {
  const y = +date.slice(0, 4), md = date.slice(5);
  if (["01-01", "01-06", "05-01", "05-03", "08-15", "11-01", "11-11", "12-24", "12-25", "12-26"].includes(md)) return true;
  const e = easterDate(y), day = 86400000;
  return [0, 1, 49, 60].some((o) => new Date(e + o * day).toISOString().slice(0, 10) === date);
}

function priceTable(date: string, hour: string) {
  const dow = new Date(`${date}T12:00:00Z`).getUTCDay();
  const weekend = dow === 0 || dow === 5 || dow === 6 || isHoliday(date);
  return PRICING[weekend ? "weekend" : "weekday"][toMin(hour) >= LATE_FROM_MIN ? "late" : "early"] as Record<number, number>;
}
const priceFor = (date: string, hour: string, people: number) => priceTable(date, hour)[people] ?? null;

// ---------- POMOCNICZE ----------
const json = (o: unknown, status = 200) =>
  new Response(JSON.stringify(o), { status, headers: { "content-type": "application/json" } });

const warsawNow = () => {
  const p = Object.fromEntries(
    new Intl.DateTimeFormat("sv-SE", { timeZone: TZ, dateStyle: "short", timeStyle: "short" })
      .formatToParts(new Date()).map((x) => [x.type, x.value]),
  );
  return { date: `${p.year}-${p.month}-${p.day}`, minutes: +p.hour * 60 + +p.minute };
};
const toMin = (h: string) => +h.slice(0, 2) * 60 + +h.slice(3, 5);
const hhmm = (h: string) => h.slice(0, 5);
const hhmmss = (h: string) => (h.length === 5 ? `${h}:00` : h);

// "Starzik" / "Starżik" / "Stażika" → ta sama postać; rz≈ż≈z, bez polskich znaków
const norm = (x: string) =>
  x.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/ł/g, "l")
    .replace(/rz/g, "z").replace(/[^a-z0-9]/g, "");

function getStarzikRoom() {
  const all = Object.entries(ROOMS);
  const hit = all.find(([k, v]) => norm(k).includes("starzik") || norm(v.nazwa).includes("starzik"));
  if (hit) return hit[1];
  return all.length === 1 ? all[0][1] : null;
}

// ---------- DATA / GODZINA / SMS ----------
const fold = (x: string) =>
  x.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/ł/g, "l").trim();
const DAYS_PL = ["poniedziałek", "wtorek", "środa", "czwartek", "piątek", "sobota", "niedziela"];
const MONTHS_PL = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia", "września", "października", "listopada", "grudnia"];

// Przyjmuje YYYY-MM-DD, "dzisiaj/jutro/pojutrze", "niedziela", "15.11", "15 listopada" — liczy w strefie Warszawy.
function resolveDate(input: unknown): string | null {
  const raw = fold(String(input ?? ""));
  if (!raw) return null;
  if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) return raw;
  const today = warsawNow().date;
  const base = Date.parse(`${today}T12:00:00Z`);
  const add = (n: number) => new Date(base + n * 86400000).toISOString().slice(0, 10);
  const iso = (y: number, m: number, d: number) => `${y}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
  const future = (m: number, d: number, y?: number) => {
    const year = y ?? +today.slice(0, 4);
    let out = iso(year, m, d);
    if (!y && out < today) out = iso(year + 1, m, d);
    return out;
  };
  if (raw.includes("pojutrze")) return add(2);
  if (raw.includes("jutro")) return add(1);
  if (/\bdzis/.test(raw)) return add(0);
  let m = raw.match(/^(\d{1,2})[./-](\d{1,2})(?:[./-](\d{2,4}))?$/);
  if (m) return future(+m[2], +m[1], m[3] ? (m[3].length === 2 ? 2000 + +m[3] : +m[3]) : undefined);
  m = raw.match(/(\d{1,2})\s*([a-z]+)/);
  if (m) {
    const mi = ["styc", "lut", "mar", "kwie", "maj", "czer", "lip", "sier", "wrze", "pazdz", "list", "grud"].findIndex((p) => m![2].startsWith(p));
    if (mi >= 0) return future(mi + 1, +m[1]);
  }
  const prefixes = ["pon", "wto", "sro", "czw", "pia", "sob", "nie"];
  for (const tok of raw.split(/[^a-z]+/)) {
    const wd = prefixes.findIndex((p) => tok.length >= 3 && tok.startsWith(p) && tok !== "nie");
    if (wd >= 0 || tok.startsWith("niedz")) {
      const target = wd >= 0 ? wd : 6;
      const todayWd = (new Date(base).getUTCDay() + 6) % 7; // 0 = poniedziałek
      return add((target - todayWd + 7) % 7);
    }
  }
  return null;
}

// "20:30", "20.30", "2030", "20", "20:30:00" → "20:30"
function parseHour(input: unknown): string | null {
  const m = String(input ?? "").trim().match(/^(\d{1,2})(?:[:.\s]?(\d{2}))?(?::\d{2})?$/);
  if (!m) return null;
  const h = +m[1], min = +(m[2] ?? 0);
  return h < 24 && min < 60 ? `${String(h).padStart(2, "0")}:${String(min).padStart(2, "0")}` : null;
}

// E-mail z rozmowy głosowej: obsługuje zarówno standardowy zapis,
// jak i np. „jan kropka kowalski małpa gmail kropka com”.
function normalizeEmail(input: unknown): string | null {
  let s = String(input ?? "").trim().toLowerCase();
  if (!s) return null;
  s = s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/ł/g, "l");
  s = s
    .replace(/\b(malpa|at)\b/g, "@")
    .replace(/\b(kropka|dot)\b/g, ".")
    .replace(/\b(myslnik|minus)\b/g, "-")
    .replace(/\b(podkreslenie|underscore)\b/g, "_")
    .replace(/\s+/g, "");

  const emailRe = /^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$/;
  return emailRe.test(s) ? s : null;
}

function normalizeNip(input: unknown): string | null {
  const nip = String(input ?? "").replace(/\D/g,"");
  if (nip.length !== 10) return null;
  const weights = [6,5,7,2,3,4,5,6,7];
  const checksum = weights.reduce((sum,w,i)=>sum + w * Number(nip[i]),0) % 11;
  return checksum !== 10 && checksum === Number(nip[9]) ? nip : null;
}

function parsePolishAddress(raw: unknown) {
  const address = String(raw ?? "").trim().replace(/\s+/g," ");
  if (!address) return { raw:"", street:"", postal_code:"", city:"", complete:false };
  const match = address.match(/^(.*?)[,\s]+(\d{2}-\d{3})\s+(.+)$/);
  if (!match) return { raw:address, street:"", postal_code:"", city:"", complete:false };
  return {
    raw:address,
    street:String(match[1]||"").replace(/[,\s]+$/,"").trim(),
    postal_code:String(match[2]||"").trim(),
    city:String(match[3]||"").replace(/,?\s*PL$/i,"").trim(),
    complete:Boolean(match[1]&&match[2]&&match[3])
  };
}

async function hCompanyByNip(b: any) {
  const nip = normalizeNip(b?.nip);
  if (!nip) return { ok:false, error:"Podaj prawidłowy 10-cyfrowy NIP." };

  const date = warsawNow().date;
  const url = `https://wykazpodatnikowvat.mf.gov.pl/api/search/nip/${nip}?date=${date}`;
  const controller = new AbortController();
  const timer = setTimeout(()=>controller.abort(),7000);
  try {
    const response = await fetch(url,{ headers:{ accept:"application/json" }, signal:controller.signal });
    const data = await response.json().catch(()=>({}));
    if (!response.ok) {
      return { ok:false, error:String(data?.message || data?.error?.message || `MF HTTP ${response.status}`) };
    }
    const subject = data?.result?.subject || data?.subject || null;
    if (!subject) return { ok:false, error:"Nie znaleziono firmy dla tego NIP-u w Wykazie podatników VAT." };

    const parsed = parsePolishAddress(subject.workingAddress || subject.residenceAddress || "");
    return {
      ok:true,
      source:"Ministerstwo Finansów · Wykaz podatników VAT",
      query_date:date,
      nip,
      name:String(subject.name || "").trim(),
      regon:String(subject.regon || "").trim(),
      status_vat:String(subject.statusVat || "").trim(),
      address:parsed.raw,
      street:parsed.street,
      postal_code:parsed.postal_code,
      city:parsed.city,
      address_complete:parsed.complete,
      request_id:String(data?.result?.requestId || data?.requestId || "").trim()
    };
  } catch (error) {
    return { ok:false, error:"Nie udało się teraz pobrać danych firmy z Ministerstwa Finansów.", detail:String(error) };
  } finally {
    clearTimeout(timer);
  }
}

function normalizeInvoiceRequest(b: any) {
  if (!b?.invoice_requested) return { requested:false, data:null, label:"" };
  const company = String(b.invoice_company ?? "").trim();
  const rawTax = String(b.invoice_tax_id ?? "").toUpperCase().replace(/[^A-Z0-9]/g, "");
  const digits = rawTax.replace(/^PL/,"").replace(/\D/g,"");
  const taxId = digits.length === 10 ? `PL${digits}` : "";
  const street = String(b.invoice_street ?? "").trim();
  const postal = String(b.invoice_postal_code ?? "").trim();
  const city = String(b.invoice_city ?? "").trim();
  if (!company || !taxId || !street || !/^\d{2}-\d{3}$/.test(postal) || !city) {
    return {
      requested:true,
      error:"Do faktury brakuje kompletnych danych firmy.",
      missing:true
    };
  }
  const data = {
    tax_id: taxId,
    address: { city, state:null, street, postal_code:postal, country_code:"PL" },
    company,
    recipient:null
  };
  const label = `${company}\n${street}\n${postal} ${city}, PL\nVAT-ID: ${taxId}`;
  return { requested:true, data, label };
}

async function resolveInvoiceRequest(b:any) {
  const direct = normalizeInvoiceRequest(b);
  if (!direct.requested || !direct.error) return direct;

  const nip = normalizeNip(b?.invoice_tax_id);
  if (!nip) {
    return {
      requested:true,
      error:"Do faktury podaj NIP firmy. Jeśli nie uda się pobrać danych automatycznie, poproszę o nazwę i adres."
    };
  }

  const company = await hCompanyByNip({ nip });
  if (!company?.ok) {
    return {
      requested:true,
      error:`Nie udało się pobrać danych firmy po NIP-ie. ${String(company?.error||"Podaj nazwę firmy i adres ręcznie.")}`
    };
  }
  if (!company.name || !company.address_complete) {
    return {
      requested:true,
      error:"Znalazłem firmę po NIP-ie, ale rejestr nie zwrócił pełnego adresu. Podaj proszę nazwę firmy, ulicę i numer, kod pocztowy oraz miasto."
    };
  }

  return normalizeInvoiceRequest({
    invoice_requested:true,
    invoice_tax_id:nip,
    invoice_company:company.name,
    invoice_street:company.street,
    invoice_postal_code:company.postal_code,
    invoice_city:company.city
  });
}

const ORD = ["północ", "pierwsza", "druga", "trzecia", "czwarta", "piąta", "szósta", "siódma", "ósma", "dziewiąta", "dziesiąta", "jedenasta", "dwunasta", "trzynasta", "czternasta", "piętnasta", "szesnasta", "siedemnasta", "osiemnasta", "dziewiętnasta", "dwudziesta", "dwudziesta pierwsza", "dwudziesta druga", "dwudziesta trzecia"];
const UNITS = ["", "jeden", "dwa", "trzy", "cztery", "pięć", "sześć", "siedem", "osiem", "dziewięć"];
const TEENS = ["dziesięć", "jedenaście", "dwanaście", "trzynaście", "czternaście", "piętnaście", "szesnaście", "siedemnaście", "osiemnaście", "dziewiętnaście"];
const TENS = ["", "", "dwadzieścia", "trzydzieści", "czterdzieści", "pięćdziesiąt"];
const minWords = (m: number) => (m < 10 ? UNITS[m] : m < 20 ? TEENS[m - 10] : TENS[Math.floor(m / 10)] + (m % 10 ? ` ${UNITS[m % 10]}` : ""));
function hourWords(hhmm_: string) {
  const h = +hhmm_.slice(0, 2), m = +hhmm_.slice(3, 5);
  return m === 0 ? ORD[h] : `${ORD[h]} ${m < 10 ? `zero ${UNITS[m]}` : minWords(m)}`;
}
function dateLabel(date: string) {
  const d = new Date(`${date}T12:00:00Z`);
  return { dzien: DAYS_PL[(d.getUTCDay() + 6) % 7], data_slownie: `${d.getUTCDate()} ${MONTHS_PL[d.getUTCMonth()]}` };
}

// ---------- LOCKME: token + fetch ----------
async function getToken(force = false) {
  const { data } = await sb.from("lockme_tokens").select("*").eq("id", 1).single();
  if (!data) throw new Error("Brak tokenu LockMe w tabeli lockme_tokens");
  const exp = data.expires_at ? new Date(data.expires_at).getTime() : Infinity;
  if (!force && exp - Date.now() > 60_000) return data.access_token as string;
  if (!data.refresh_token) return data.access_token as string;

  const r = await fetch(LOCKME.tokenUrl, {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "refresh_token",
      refresh_token: data.refresh_token,
      client_id: env("LOCKME_CLIENT_ID"),
      client_secret: env("LOCKME_CLIENT_SECRET"),
    }),
  });
  if (!r.ok) throw new Error(`Refresh tokenu LockMe: ${r.status}`);
  const t = await r.json();
  await sb.from("lockme_tokens").update({
    access_token: t.access_token,
    refresh_token: t.refresh_token ?? data.refresh_token,
    expires_at: t.expires_in ? new Date(Date.now() + t.expires_in * 1000).toISOString() : null,
    updated_at: new Date().toISOString(),
  }).eq("id", 1);
  return t.access_token as string;
}

async function lm(path: string, init: RequestInit = {}, retry = true): Promise<any> {
  const token = await getToken();
  const r = await fetch(LOCKME.base + path, {
    ...init,
    headers: { authorization: `Bearer ${token}`, "content-type": "application/json", accept: "application/json", ...(init.headers ?? {}) },
  });
  if (r.status === 401 && retry) { await getToken(true); return lm(path, init, false); }
  if (!r.ok) throw new Error(`LockMe ${r.status} ${path}: ${(await r.text()).slice(0, 200)}`);
  return r.status === 204 ? null : r.json();
}

const list = (x: any): any[] => (Array.isArray(x) ? x : x?.data ?? x?.hours ?? x?.settings ?? x?.reservations ?? []);

// ---------- LOGIKA ----------
async function getSlots(roomId: number, date: string) {
  const dow = (new Date(`${date}T12:00:00Z`).getUTCDay() + 6) % 7; // LockMe: 0 = poniedziałek … 6 = niedziela
  let settings = list(await lm(LOCKME.path.dateSettings(roomId, date)).catch(() => null));
  if (!settings.length) settings = list(await lm(LOCKME.path.daySettings(roomId, dow)));
  const booked = new Set(
    list(await lm(LOCKME.path.reservations(roomId, date)))
      .filter((r) => !/cancel|anul/i.test(String(r.status ?? "")))
      .map((r) => hhmm(String(r.hour))),
  );
  const now = warsawNow();
  return settings
    .filter((s) => s.hour && !booked.has(hhmm(s.hour)))
    .filter((s) => date > now.date || (date === now.date && toMin(s.hour) >= now.minutes + MIN_LEAD_MIN))
    .map((s) => ({ hour: hhmmss(s.hour), pricers: (s.pricers ?? []) as number[] }))
    .sort((a, b) => a.hour.localeCompare(b.hour));
}

// ---------- HANDLERY ----------
async function hRooms() {
  const room = getStarzikRoom();
  return room ? { ok: true, room: { ...room, id: undefined } } : { ok: false, error: "Brak konfiguracji pokoju Starzik" };
}

async function hSlots(b: any) {
  const room = getStarzikRoom();
  if (!room) return { ok: false, error: "Brak konfiguracji pokoju Starzik" };
  const people = b.people ? Number(b.people) : null;
  if (people != null && (!Number.isInteger(people) || people < 2 || people > 5))
    return { ok: false, error: "Liczba graczy musi wynosić od 2 do 5" };

  const view = (date: string, free: { hour: string }[]) => ({
    ok: true, source: "lockme", room: room.nazwa, date, ...dateLabel(date),
    free: free.map((s) => ({
      godzina: hhmm(s.hour),
      slownie: hourWords(hhmm(s.hour)),
      cena_zl: people ? priceFor(date, s.hour, people) : priceTable(date, s.hour),
    })),
  });

  const mode = String(b.mode || "").trim().toLowerCase();

  if (mode === "weekday") {
    const start = Date.parse(`${warsawNow().date}T12:00:00Z`);
    const matches:any[] = [];
    for (let i = 0; i < 28 && matches.length < 4; i++) {
      const d = new Date(start + i * 86400000).toISOString().slice(0, 10);
      const dow = new Date(`${d}T12:00:00Z`).getUTCDay();
      if (dow < 1 || dow > 4) continue;
      try {
        const free = await getSlots(room.id, d);
        if (free.length) matches.push(view(d, free));
      } catch (e) {
        console.warn("slots_weekday_error", d, String(e));
      }
    }
    const result = {
      ok: true,
      source: "lockme",
      mode: "weekday",
      zakres: "poniedziałek–czwartek",
      dni: matches,
      najblizszy_termin: matches[0] || null
    };
    console.log("slots_result", JSON.stringify(result));
    return result;
  }

  if (b.date) {
    const date = resolveDate(b.date);
    if (!date) return { error: "Nie rozumiem daty — podaj YYYY-MM-DD albo np. „niedziela”, „jutro”, „15 listopada”" };
    const result = view(date, await getSlots(room.id, date));
    console.log("slots_result", JSON.stringify(result));
    return result;
  }

  const start = Date.parse(`${warsawNow().date}T12:00:00Z`);
  const days = Array.from({ length: 14 }, (_, i) => new Date(start + i * 86400000).toISOString().slice(0, 10));
  for (const d of days) {
    try {
      const free = await getSlots(room.id, d);
      if (free.length) {
        const result = { ok: true, source: "lockme", mode: "nearest", najblizszy_termin: view(d, free) };
        console.log("slots_result", JSON.stringify(result));
        return result;
      }
    } catch (e) {
      console.warn("slots_day_error", d, String(e));
    }
  }
  return { ok: true, source: "lockme", mode: mode || "nearest", najblizszy_termin: null, info: "Brak wolnych terminów w najbliższych 14 dniach" };
}

async function hReserve(b: any, callerFromHeader: string) {
  const room = getStarzikRoom();
  if (!room) return { ok: false, error: "Brak konfiguracji pokoju Starzik" };
  const date = resolveDate(b.date), hour = parseHour(b.hour);
  const { name, surname, people } = b;
  const phone = b.phone || callerFromHeader;
  const rawEmail = String(b.email ?? "").trim();
  if (!rawEmail)
    return { ok: false, error: "Brakuje adresu e-mail. Zapytaj rozmówcę o e-mail i potwierdź go przed utworzeniem rezerwacji." };
  const email = normalizeEmail(rawEmail);
  if (!email)
    return { ok: false, error: "Nieprawidłowy adres e-mail. Poproś o ponowne podanie, np. jan kropka kowalski małpa gmail kropka com, i potwierdź zapis." };
  if (!date || !hour || !name || !surname || !phone || !people)
    return { ok: false, error: "Brakuje danych lub zły format: data, godzina, imię, nazwisko, telefon, liczba osób" };

  // ponowne sprawdzenie tuż przed zapisem (ochrona przed podwójną rezerwacją)
  const free = await getSlots(room.id, date);
  const slot = free.find((s) => hhmm(s.hour) === hour);
  if (!slot) return { ok: false, error: "Ten termin został właśnie zajęty lub nie istnieje", free: free.map((s) => ({ godzina: hhmm(s.hour), slownie: hourWords(hhmm(s.hour)) })) };

  const price = priceFor(date, slot.hour, Number(people));
  if (price == null) return { ok: false, error: "Pokój jest dla 2–5 osób" };

  const invoice = await resolveInvoiceRequest(b);
  if (invoice.error) return { ok:false, error:invoice.error, code:"invoice_data_required" };

  const channel = b.channel === "chat" ? "chat" : "voice";
  const extid = `${channel}-${crypto.randomUUID().slice(0, 8)}`;
  const payloadObj:any = {
    roomid: room.id, date, hour: slot.hour, extid,
    name, surname, email, phone, people: Number(people),
    pricer: slot.pricers[0], // ZWERYFIKUJ: dobór cennika LockMe wg liczby osób
    price,
    comment: `Rezerwacja przez asystenta AI (${channel === "chat" ? "czat" : "telefon"}), cena wg cennika: ${price} zł${invoice.requested ? " · faktura VAT" : ""} — do potwierdzenia`,
  };
  if (invoice.requested && invoice.data) {
    payloadObj.invoice = invoice.label;
    payloadObj.invoice_data = invoice.data;
  }
  const res = await lm(LOCKME.path.addReservation(room.id), { method: "PUT", body: JSON.stringify(payloadObj) });
  await sb.from("voice_reservations").insert({
    conversation_id: b.conversation_id ?? null, room_id: room.id, date, hour: hour,
    name, surname, phone, people: Number(people), lockme_id: String(res?.id ?? res ?? extid),
  });

  return {
    ok: true, room: room.nazwa, date, ...dateLabel(date), hour, slownie: hourWords(hour),
    people: Number(people), cena_zl: price, email_zapisany: !!email,
    faktura: invoice.requested,
  };
}

async function hInvoice(b: any) {
  const conversationId = String(b?.conversation_id || "").trim();
  if (!conversationId) return { ok:false, error:"Nie mam identyfikatora tej rozmowy." };
  const invoice = await resolveInvoiceRequest({ ...b, invoice_requested:true });
  if (invoice.error) return { ok:false, error:invoice.error, code:"invoice_data_required" };

  const { data:rows, error } = await sb.from("voice_reservations")
    .select("room_id,lockme_id,date,hour")
    .eq("conversation_id", conversationId)
    .order("created_at", { ascending:false })
    .limit(1);
  if (error) throw error;
  const row = Array.isArray(rows) ? rows[0] : null;
  if (!row?.room_id || !row?.lockme_id) {
    return { ok:false, error:"Nie znajduję rezerwacji utworzonej w tej rozmowie. Dane do faktury możesz przekazać obsłudze Familocka." };
  }

  await lm(`/room/${row.room_id}/reservation/${row.lockme_id}`, {
    method:"POST",
    body:JSON.stringify({ invoice:invoice.label, invoice_data:invoice.data })
  });
  return { ok:true, faktura:true, date:row.date, hour:row.hour };
}

async function verifyElevenLabs(req: Request, raw: string) {
  const sig = req.headers.get("elevenlabs-signature") ?? "";
  const t = /t=(\d+)/.exec(sig)?.[1], v0 = /v0=([a-f0-9]+)/.exec(sig)?.[1];
  if (!t || !v0 || Math.abs(Date.now() / 1000 - +t) > 1800) return false;
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(env("ELEVENLABS_WEBHOOK_SECRET")),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const mac = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(`${t}.${raw}`));
  const hex = [...new Uint8Array(mac)].map((x) => x.toString(16).padStart(2, "0")).join("");
  return hex === v0;
}

async function hPostCall(req: Request) {
  const raw = await req.text();
  if (!(await verifyElevenLabs(req, raw))) return json({ error: "bad signature" }, 401);
  const ev = JSON.parse(raw);
  if (ev.type !== "post_call_transcription") return json({ ok: true, ignored: ev.type });
  const d = ev.data;
  await sb.from("voice_calls").upsert({
    conversation_id: d.conversation_id,
    caller: d.metadata?.phone_call?.external_number ?? null,
    summary: d.analysis?.transcript_summary ?? null,
    transcript: d.transcript ?? null,
  });
  return json({ ok: true });
}

// ---------- OAUTH: jednorazowa autoryzacja w LockMe (zapis tokenu do bazy) ----------
async function hmacHex(msg: string) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(env("AGENT_SECRET")),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const mac = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(msg));
  return [...new Uint8Array(mac)].map((x) => x.toString(16).padStart(2, "0")).join("");
}

async function hOauthStart(req: Request) {
  if (new URL(req.url).searchParams.get("key") !== env("AGENT_SECRET")) return json({ error: "unauthorized" }, 401);
  const ts = String(Date.now());
  const state = `${ts}.${await hmacHex(ts)}`;
  const q = new URLSearchParams({
    response_type: "code", client_id: env("LOCKME_CLIENT_ID"),
    redirect_uri: env("LOCKME_REDIRECT_URI"), scope: "rooms_manage", state,
  });
  return Response.redirect(`${LOCKME.authUrl}?${q}`, 302);
}

async function hOauthCallback(req: Request) {
  const u = new URL(req.url);
  const code = u.searchParams.get("code"), state = u.searchParams.get("state") ?? "";
  const [ts, sig] = state.split(".");
  if (!code || !ts || sig !== (await hmacHex(ts)) || Date.now() - +ts > 15 * 60_000)
    return new Response("Nieprawidłowy lub wygasły state — zacznij od /oauth-start", { status: 400 });
  const r = await fetch(LOCKME.tokenUrl, {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code", code, redirect_uri: env("LOCKME_REDIRECT_URI"),
      client_id: env("LOCKME_CLIENT_ID"), client_secret: env("LOCKME_CLIENT_SECRET"),
    }),
  });
  if (!r.ok) return new Response(`LockMe token: ${r.status} ${(await r.text()).slice(0, 300)}`, { status: 502 });
  const t = await r.json();
  await sb.from("lockme_tokens").upsert({
    id: 1, access_token: t.access_token, refresh_token: t.refresh_token ?? null,
    expires_at: t.expires_in ? new Date(Date.now() + t.expires_in * 1000).toISOString() : null,
    updated_at: new Date().toISOString(),
  });
  return new Response("Token LockMe zapisany. Możesz zamknąć tę kartę.", { headers: { "content-type": "text/plain; charset=utf-8" } });
}

// ---------- ROUTER ----------
Deno.serve(async (req) => {
  const route = new URL(req.url).pathname.split("/").pop();
  try {
    if (route === "post-call") return await hPostCall(req);
    if (route === "oauth-start") return await hOauthStart(req);
    if (route === "oauth-callback") return await hOauthCallback(req);

    if (req.headers.get("x-agent-secret") !== env("AGENT_SECRET")) {
      console.warn("unauthorized:", route, "— sprawdź nagłówek x-agent-secret w narzędziu ElevenLabs");
      return json({ error: "unauthorized" }, 401);
    }
    const body = req.method === "POST" ? await req.json().catch(() => ({})) : {};
    console.log("tool", route, JSON.stringify(body));
    if (route === "rooms") return json(await hRooms());
    if (route === "slots") return json(await hSlots(body));
    if (route === "company") return json(await hCompanyByNip(body));
    if (route === "reserve") return json(await hReserve(body, body.caller_id ?? ""));
    if (route === "invoice") return json(await hInvoice(body));
    return json({ error: "not found" }, 404);
  } catch (e) {
    console.error(e);
    return json({ ok: false, error: "Błąd systemu rezerwacji — zbierz dane i powiedz, że ktoś oddzwoni." }, 200);
  }
});
