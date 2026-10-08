// Mon Dossier Voyage: offline support.
// Pages and data are served from the network when possible (so updates show up at once),
// and from the cache when the phone is offline.
const CACHE = "mdv-v2";
const CORE = [
  "./", "index.html", "mentions-legales.html", "confidentialite.html", "manifest.webmanifest",
  "icons/icon-192.png", "icons/icon-512.png",
  "data/visa.json", "data/embassies.json", "data/airports.json", "data/tz.json",
  "data/emergency.json", "data/meta.json", "data/countries.geo.json"
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET" || new URL(req.url).origin !== self.location.origin) return;
  event.respondWith(
    fetch(req)
      .then((res) => {
        if (res.ok) {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
        }
        return res;
      })
      .catch(() => caches.match(req).then((hit) => hit || caches.match("index.html")))
  );
});
