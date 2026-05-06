/**
 * Service Worker pour Omar.tech Portfolio
 * Cache stratégique pour une expérience offline et chargement rapide
 */

const CACHE_NAME = 'omar-tech-v2';
const STATIC_CACHE = 'omar-tech-static-v2';
const DYNAMIC_CACHE = 'omar-tech-dynamic-v2';

// Ressources à mettre en cache immédiatement
const STATIC_ASSETS = [
  '/',
  '/offline/',
  '/static/css/style.css',
  '/static/js/script.js',
  '/static/img/og-cover.png',
  '/static/img/profile.svg',
  '/static/manifest.json',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css',
  'https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700;800&family=Manrope:wght@300;400;500;600;700;800&display=swap'
];

// Installation - cache des assets statiques
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[SW] Cache des assets statiques');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
      .catch((error) => {
        console.error('[SW] Erreur lors de l\'installation:', error);
      })
  );
});

// Activation - nettoyage des anciens caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => {
        return Promise.all(
          keys
            .filter((key) => key !== STATIC_CACHE && key !== DYNAMIC_CACHE)
            .map((key) => {
              console.log('[SW] Suppression ancien cache:', key);
              return caches.delete(key);
            })
        );
      })
      .then(() => self.clients.claim())
  );
});

// Stratégie de cache: Network First pour API, Cache First pour static
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Stratégie différente selon le type de requête
  if (request.method !== 'GET') {
    // Requêtes POST/PUT/DELETE - network only
    return;
  }

  if (isStaticAsset(url)) {
    // Cache First pour les assets statiques
    event.respondWith(
      caches.match(request)
        .then((cachedResponse) => {
          if (cachedResponse) {
            // Retourner la version en cache tout en mettant à jour en background
            fetch(request).then((response) => {
              if (response.ok) {
                caches.open(STATIC_CACHE).then((cache) => {
                  cache.put(request, response);
                });
              }
            }).catch(() => {
              // Network failed, cached response is fine
            });
            return cachedResponse;
          }

          // Pas en cache, fetch et cache
          return fetch(request).then((response) => {
            if (!response.ok || response.status === 404) {
              return response;
            }

            const responseClone = response.clone();
            caches.open(STATIC_CACHE).then((cache) => {
              cache.put(request, responseClone);
            });

            return response;
          }).catch(() => {
            // Offline, retourner une page offline si c'est une navigation
            if (request.mode === 'navigate') {
              return caches.match('/offline/');
            }
          });
        })
        .catch(() => {
          // Erreur, retourner offline page si navigation
          if (request.mode === 'navigate') {
            return caches.match('/offline/');
          }
        })
    );
  } else if (isNavigationRequest(request)) {
    // Network First pour les pages HTML
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Cache la page réussie
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(DYNAMIC_CACHE).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Offline, essayer de servir depuis le cache
          return caches.match(request)
            .then((cachedResponse) => {
              return cachedResponse || caches.match('/offline/');
            });
        })
    );
  } else {
    // Autres requêtes (images, fonts, etc.) - Cache First
    event.respondWith(
      caches.match(request)
        .then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }

          return fetch(request).then((response) => {
            if (response.ok) {
              const responseClone = response.clone();
              caches.open(DYNAMIC_CACHE).then((cache) => {
                cache.put(request, responseClone);
              });
            }
            return response;
          });
        })
    );
  }
});

// Helper functions
function isStaticAsset(url) {
  const staticExtensions = [
    '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp',
    '.ico', '.woff', '.woff2', '.ttf', '.eot', '.json'
  ];
  const pathname = url.pathname.toLowerCase();
  return staticExtensions.some(ext => pathname.endsWith(ext)) ||
         url.hostname === 'cdn.jsdelivr.net' ||
         url.hostname === 'cdnjs.cloudflare.com' ||
         url.hostname === 'fonts.googleapis.com' ||
         url.hostname === 'fonts.gstatic.com';
}

function isNavigationRequest(request) {
  return request.mode === 'navigate' ||
         (request.destination === 'document') ||
         (request.headers.get('Accept') && request.headers.get('Accept').includes('text/html'));
}

// Background sync pour les formulaires offline
self.addEventListener('sync', (event) => {
  if (event.tag === 'contact-form-sync') {
    event.waitUntil(
      // Retry sending pending contact form submissions
      syncContactForms()
    );
  }
});

async function syncContactForms() {
  // Implementation pour retry les soumissions de formulaires
  console.log('[SW] Sync des formulaires de contact en attente');
}

// Push notifications (pour futures fonctionnalités)
self.addEventListener('push', (event) => {
  if (!event.data) return;

  const data = event.data.json();
  const options = {
    body: data.body,
    icon: '/static/img/og-cover.png',
    badge: '/static/img/og-cover.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: data.primaryKey
    },
    actions: [
      { action: 'explore', title: 'Voir le portfolio' },
      { action: 'close', title: 'Fermer' }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(data.title || 'Omar.tech', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(clients.openWindow('/'));
  }
});

console.log('[SW] Service Worker chargé et prêt');
