/**
 * Returns the final item of the given `items` that matches the given `predicate`.
 *
 * @param items The data to search through
 * @param predicate The condition that the item should match
 */
export function findLast<T>(
  [...items]: Iterable<T>,
  predicate: (item: T) => boolean
) {
  for (let i = items.length - 1; i >= 0; i--) {
    const item = items[i];
    if (predicate(item)) {
      return item;
    }
  }
}
