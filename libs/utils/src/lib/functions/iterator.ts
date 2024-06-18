/**
 * Returns an `Iterator` over every element of the given `iterable`.
 * @param iterable The collection of elements to iterate over
 */
export function* iterator<T>(iterable: Iterable<T>): Iterator<T> {
  yield* iterable;
}
