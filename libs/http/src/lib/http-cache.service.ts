import { HttpResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Logger } from '@models4insight/logger';
import { each } from 'lodash';

const log = new Logger('HttpCacheService');
const cachePersistenceKey = 'httpCache';

export interface HttpCacheEntry {
  lastUpdated: Date;
  data: HttpResponse<any>;
}

/**
 * Provides a cache facility for HTTP requests with configurable persistence policy.
 */
@Injectable()
export class HttpCacheService {
  private cachedData: { [key: string]: HttpCacheEntry } = {};
  private storage: Storage | null = null;

  constructor() {
    this.loadCacheData();
  }

  /**
   * Sets the cache data for the specified request.
   * @param url The request URL.
   * @param data The received data.
   * @param lastUpdated The cache last update, current date is used if not specified.
   */
  setCacheData(url: string, data: HttpResponse<any>, lastUpdated?: Date) {
    this.cachedData[url] = {
      lastUpdated: lastUpdated || new Date(),
      data: data,
    };
    log.debug(`Cache set for key: "${url}"`);
    this.saveCacheData();
  }

  /**
   * Gets the cached data for the specified request.
   * @param url The request URL.
   * @return The cached data or null if no cached data exists for this request.
   */
  getCacheData(url: string): HttpResponse<any> | null {
    const cacheEntry = this.cachedData[url];

    if (cacheEntry) {
      log.debug(`Cache hit for key: "${url}"`);
      return cacheEntry.data;
    }

    return null;
  }

  /**
   * Gets the cached entry for the specified request.
   * @param url The request URL.
   * @return The cache entry or null if no cache entry exists for this request.
   */
  getHttpCacheEntry(url: string): HttpCacheEntry | null {
    return this.cachedData[url] || null;
  }

  /**
   * Clears the cached entry (if exists) for the specified request.
   * @param url The request URL.
   * @param matchAll Whether or not the url of the request should match completely. Defaults to `true`.
   */
  clearCache(url: string, matchAll = true): void {
    this.cachedData = Object.entries(this.cachedData)
      .filter(([cachedUrl]) =>
        matchAll ? url === cachedUrl : cachedUrl.includes(url)
      )
      .reduce(
        (cache, [cachedUrl, cachedData]) => ({
          ...cache,
          [cachedUrl]: cachedData,
        }),
        {}
      );
    log.debug(`Cache cleared for key: "${url}"`);
    this.saveCacheData();
  }

  /**
   * Cleans cache entries older than the specified date.
   * @param expirationDate The cache expiration date. If no date is specified, all cache is cleared.
   */
  cleanCache(expirationDate?: Date) {
    if (expirationDate) {
      each(this.cachedData, (value: HttpCacheEntry, key: string) => {
        if (expirationDate >= value.lastUpdated) {
          delete this.cachedData[key];
        }
      });
    } else {
      this.cachedData = {};
    }
    this.saveCacheData();
  }

  /**
   * Sets the cache persistence policy.
   * Note that changing the cache persistence will also clear the cache from its previous storage.
   * @param persistence How the cache should be persisted, it can be either local or session storage, or if no value is
   *   provided it will be only in-memory (default).
   */
  setPersistence(persistence?: 'local' | 'session') {
    this.cleanCache();
    this.storage =
      persistence === 'local' || persistence === 'session'
        ? window[persistence + 'Storage']
        : null;
    this.loadCacheData();
  }

  private saveCacheData() {
    if (this.storage) {
      this.storage[cachePersistenceKey] = JSON.stringify(this.cachedData);
    }
  }

  private loadCacheData() {
    const data = this.storage ? this.storage[cachePersistenceKey] : null;
    this.cachedData = data ? JSON.parse(data) : {};
  }
}
