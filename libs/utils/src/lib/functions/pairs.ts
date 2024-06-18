import { iterator } from './iterator';

/**
 * For two collections `A` and `B`, returns a list of tuples `[A, B]` representing the items at index `i` for every item in `A` and `B`.
 * If either `A` or `B` does not contain an item at index `i`, the respective side of the tuple will be `undefined`.
 */
export function* pairs<A, B>(
  /* A collection */
  a: Iterable<A>,
  /* Another collection */
  b: Iterable<B>
): Generator<[A, B]> {
  const iteratorA = iterator(a),
    iteratorB = iterator(b);
  for (
    let itemA = iteratorA.next(), itemB = iteratorB.next();
    !(itemA.done && itemB.done);
    itemA = iteratorA.next(), itemB = iteratorB.next()
  ) {
    yield [itemA.value, itemB.value] as [A, B];
  }
}
