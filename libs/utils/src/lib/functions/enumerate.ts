/**
 * Iterates over the given `items` and yields for every item a tuple of that item and its sequential index.
 * @param items The items to iterate over.
 */
export function* enumerate<T>(items: Iterable<T>): Generator<[T, number]> {
  let index = 0;
  for (const item of items) {
    yield [item, index];
    index++;
  }
}
