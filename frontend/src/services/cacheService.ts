interface CacheItem<T> {
  data: T;
  timestamp: number;
  ttl: number; // Time to live in milliseconds
}

class CacheService {
  private cache = new Map<string, CacheItem<any>>();
  private readonly DEFAULT_TTL = 5 * 60 * 1000; // 5 minutes

  set<T>(key: string, data: T, ttl: number = this.DEFAULT_TTL): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  get<T>(key: string): T | null {
    const item = this.cache.get(key);

    if (!item) {
      return null;
    }

    const isExpired = Date.now() - item.timestamp > item.ttl;

    if (isExpired) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  has(key: string): boolean {
    return this.get(key) !== null;
  }

  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  // Méthodes utilitaires pour les clés de cache
  generateSearchKey(query: string, category?: string, limit?: number): string {
    return `search:${query}:${category || "all"}:${limit || 8}`;
  }

  generateSuggestionsKey(category?: string, limit?: number): string {
    return `suggestions:${category || "all"}:${limit || 6}`;
  }

  generateListKey(listId: number): string {
    return `list:${listId}`;
  }

  generateListItemsKey(listId: number): string {
    return `listItems:${listId}`;
  }

  // Invalidation intelligente du cache
  invalidateList(listId: number): void {
    this.delete(this.generateListKey(listId));
    this.delete(this.generateListItemsKey(listId));
  }

  invalidateSearch(): void {
    // Supprimer toutes les clés de recherche
    for (const key of this.cache.keys()) {
      if (key.startsWith("search:")) {
        this.delete(key);
      }
    }
  }

  invalidateSuggestions(): void {
    // Supprimer toutes les clés de suggestions
    for (const key of this.cache.keys()) {
      if (key.startsWith("suggestions:")) {
        this.delete(key);
      }
    }
  }

  // Statistiques du cache
  getStats() {
    const now = Date.now();
    let validEntries = 0;
    let expiredEntries = 0;

    for (const [, item] of this.cache.entries()) {
      if (now - item.timestamp > item.ttl) {
        expiredEntries++;
      } else {
        validEntries++;
      }
    }

    return {
      total: this.cache.size,
      valid: validEntries,
      expired: expiredEntries,
    };
  }

  // Nettoyage automatique des entrées expirées
  cleanup(): void {
    const now = Date.now();
    for (const [k, item] of this.cache.entries()) {
      if (now - item.timestamp > item.ttl) {
        this.cache.delete(k);
      }
    }
  }
}

// Instance singleton
export const cacheService = new CacheService();

// Nettoyage automatique toutes les 5 minutes
setInterval(() => {
  cacheService.cleanup();
}, 5 * 60 * 1000);

export default cacheService;
