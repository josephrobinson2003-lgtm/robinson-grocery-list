// Robinson Grocery List service worker.
// VERSION is stamped by build.py on every rebuild so phones pick up the new worker.
const VERSION = '2026-10-17-0b8a9b22';
const CACHE = 'rgl-' + VERSION;
const SHELL = [
  './',
  './index.html',
  './list.json',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-192.png',
  './icons/icon-maskable-512.png',
  './icons/apple-touch-icon.png',
  './icons/favicon-32.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith('rgl-') && k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function isData(req, url) {
  // The page itself (list data is embedded in it) and list.json: always try the network first.
  return req.mode === 'navigate' || url.pathname.endsWith('/') ||
         url.pathname.endsWith('/index.html') || url.pathname.endsWith('/list.json');
}

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  if (isData(req, url)) {
    e.respondWith(
      fetch(req, { cache: 'no-store' })
        .then((res) => {
          if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); }
          return res;
        })
        .catch(() => caches.match(req).then((hit) => hit ||
          (req.mode === 'navigate' ? caches.match('./index.html') : undefined)))
    );
    return;
  }

  // Static assets (icons, manifest): cache first, fall back to network.
  e.respondWith(
    caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); }
      return res;
    }))
  );
});
