// Service Worker pour PWA T4ST3 M4TCH
const CACHE_NAME = 't4st3-m4tch-v2';
const STATIC_CACHE_NAME = 't4st3-static-v2';
const DYNAMIC_CACHE_NAME = 't4st3-dynamic-v2';

// Ressources critiques à mettre en cache
const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/icon-192.png',
  '/icon-512.png'
];

// Installation du Service Worker
self.addEventListener('install', event => {
  console.log('[SW] Installation...');
  event.waitUntil(
    caches.open(STATIC_CACHE_NAME)
      .then(cache => {
        console.log('[SW] Mise en cache des ressources statiques');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('[SW] Installation terminée');
        return self.skipWaiting();
      })
      .catch(error => {
        console.error('[SW] Erreur lors de l\'installation:', error);
      })
  );
});

// Activation du Service Worker
self.addEventListener('activate', event => {
  console.log('[SW] Activation...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== STATIC_CACHE_NAME && cacheName !== DYNAMIC_CACHE_NAME) {
            console.log('[SW] Suppression du cache obsolète:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('[SW] Activation terminée');
      return self.clients.claim();
    })
  );
});

// Stratégie de mise en cache
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Ignorer les requêtes non-HTTP
  if (!request.url.startsWith('http')) {
    return;
  }

  // Stratégie Cache First pour les ressources statiques
  if (STATIC_ASSETS.some(asset => url.pathname === asset) || 
      request.destination === 'image' ||
      request.destination === 'style' ||
      request.destination === 'script') {
    
    event.respondWith(
      caches.match(request)
        .then(response => {
          if (response) {
            return response;
          }
          return fetch(request).then(fetchResponse => {
            if (fetchResponse.status < 400) {
              const responseClone = fetchResponse.clone();
              caches.open(STATIC_CACHE_NAME).then(cache => {
                cache.put(request, responseClone);
              });
            }
            return fetchResponse;
          });
        })
        .catch(() => {
          // Fallback pour les images
          if (request.destination === 'image') {
            return caches.match('/icon-192.png');
          }
        })
    );
  }
  // Stratégie Network First pour le contenu dynamique
  else {
    event.respondWith(
      fetch(request)
        .then(response => {
          if (response.status < 400) {
            const responseClone = response.clone();
            caches.open(DYNAMIC_CACHE_NAME).then(cache => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          return caches.match(request);
        })
    );
  }
});

// Nettoyage périodique du cache dynamique
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'CLEAN_CACHE') {
    event.waitUntil(
      caches.open(DYNAMIC_CACHE_NAME).then(cache => {
        return cache.keys().then(keys => {
          if (keys.length > 50) { // Limite à 50 entrées
            return Promise.all(
              keys.slice(0, keys.length - 50).map(key => cache.delete(key))
            );
          }
        });
      })
    );
  }
});