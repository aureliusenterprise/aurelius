/**
 * Convenience function to help iterate over the given `iterator`.
 */
export function* iterate<T>(iterator: Iterator<T>): Iterable<T> {
  let item: IteratorResult<T> = iterator.next();
  while (!item.done) {
    yield item.value;
    item = iterator.next();
  }
}
