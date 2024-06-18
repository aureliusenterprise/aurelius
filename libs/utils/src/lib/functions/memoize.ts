import LRUMap from 'mnemonist/lru-map';

/**
 * The default maximum size of the cache.
 */
export const defaultCacheLimit = 1000;

/**
 * The default cache key resolver.
 * Returns the first argument as the cache key.
 * The first argument should therefore be a string.
 *
 * @param args the arguments from which to take the key.
 */
export const defaultResolver: MemoResolver<
  (arg0: string, ...args: any[]) => any
> = (...args) => args[0];

/**
 * Function that builds a cache key from its arguments.
 */
export type MemoResolver<T extends Memoizable> = (
  ...args: Parameters<T>
) => string;

/**
 * Functions that match this type can be memoized.
 */
export type Memoizable = (...args: any[]) => any;

/**
 * A memoized function caches its results by a key built from its arguments.
 */
export type Memoized<T extends Memoizable> = T & Memo<T>;

/**
 * A memoized function exposes its cache as a read-only attribute.
 */
interface Memo<T extends Memoizable> {
  /**
   * The cache from which memoized results are retrieved.
   */
  readonly cache: Map<string, ReturnType<T>>;
}

/**
 * Optional settings for the memoize function.
 */
export interface MemoizeOptions<T extends Memoizable> {
  /**
   * The max number of items in the cache.
   * When the size of the cache exceeds this limit, the least recently used items are removed from the cache.
   * Defaults to `defaultCacheLimit`.
   */
  readonly cacheLimit?: number;
  /**
   * Function that returns the cache key.
   * Defaults to `defaultResolver`.
   */
  readonly resolver?: MemoResolver<T>;
}

/**
 * Caches the results of the given function by a key built from its arguments.
 *
 * When the function is called again for the same arguments, the result is returned from the cache instead.
 *
 * Use `memoize` whenever you need to repeat an expensive computation often.
 *
 * If your function takes multiple arguments, or if the first argument of your function is not a string, you should pass a custom `resolver`.
 *
 * Whenever the size of the cache exceeds the given `cacheLimit`, the least recently used entries is removed from the cache.
 * You can optionally increase or decrease the size of the cache.
 *
 * @param func The function of which the results should be cached.
 * @param options Configuration parameters.
 */
export function memoize<T extends Memoizable>(
  func: T,
  {
    cacheLimit = defaultCacheLimit,
    resolver = defaultResolver,
  }: MemoizeOptions<T> = {}
): Memoized<T> {
  const cache = new LRUMap<string, ReturnType<T>>(cacheLimit);

  function memoized(...args: Parameters<T>) {
    const key = resolver.apply(null, args);

    if (cache.has(key)) return cache.get(key);

    const value = func.apply(null, args);

    cache.set(key, value);

    return value;
  }

  const result = Object.defineProperty(memoized, 'cache', {
    get: () => cache,
  });

  return result as any;
}
