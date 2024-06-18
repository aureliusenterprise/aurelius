/**
 * Returns a generator that returns every item from the given sequence, along with the previous item in the sequence.
 * @param items The seuqence of items
 */
export function* pairwise<T>(items: Iterable<T>): Generator<[T, T]> {
  let previous: T;
  for (const item of items) {
    if (previous) {
      yield [previous, item];
    }
    previous = item;
  }
}
