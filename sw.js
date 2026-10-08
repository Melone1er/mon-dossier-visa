// Mon Dossier Voyage pour 199 pays: offline support.
// Pages and data are served from the network when possible (so updates show up at once),
// and from the cache when the phone is offline.
const CACHE = "mdv-v4";
const CORE = [
  "./", "index.html", "mentions-legales.html", "confidentialite.html", "manifest.webmanifest",
  "icons/icon-192.png", "icons/icon-512.png",
  "data/visa.json", "data/airports.json", "data/tz.json",
  "data/meta.json", "data/countries.geo.json"
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
  const url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== self.location.origin) return;
  // The paid space (accounts, payments, private data) is never cached on the device.
  if (url.pathname.includes("/agence/")) return;
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
