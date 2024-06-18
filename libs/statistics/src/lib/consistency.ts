import { pairs, raceUntil } from '@models4insight/utils';
import { isEqual, orderBy, range } from 'lodash';

export interface ConsistencyOptions {
  /**
   * Whether or not to short cirquit the calculation if the datasets are not consistent.
   * When short cirquiting, the returned consistency index is always 0 (non-consistent) or 1 (consistent).
   * Enable short cirquting to improve performance if you don't care about the precise consistency index.
   */
  shortCirquiting?: boolean;
}

/**
 * Calculates a consistency index between two datasets by comparing the given reference values against the given other values.
 * The consistency value is *not* symmetric.
 */
export async function consistency<A, B>(
  /** The reference dataset for which to calculate the consistency index */
  referenceValues: A[],
  /** The other dataset against which to calculate the consistency index */
  otherValues: B[],
  { shortCirquiting }: ConsistencyOptions = {}
): Promise<number> {
  //Cluster all pairs with equal reference values together.
  const sortedPairs = orderBy(
    Array.from(pairs(referenceValues, otherValues)),
    [0, 1]
  );

  /*
   Count the number of rows that are consistent with the previous row.
   A row is consistent if the reference values are different, or when the other values are equal.
   This works because the pairs are sorted by reference value.
   */
  const isConsistentPair$ = range(
    1,
    Math.max(referenceValues.length, otherValues.length)
  ).map(async (index) => {
    const [a, b] = sortedPairs[index],
      [previousA, previousB] = sortedPairs[index - 1];
    return isEqual(previousB, b) || !isEqual(previousA, a);
  });

  if (shortCirquiting) {
    // If short cirquiting is enabled, continue until an inconsistent pair is found
    const hasAllConsistentPairs = await raceUntil(
      isConsistentPair$,
      (isConsistent) => !isConsistent,
      true
    );
    // Return a consistency index of 1 if all pairs are consistent
    return hasAllConsistentPairs ? 1 : 0;
  } else {
    // Else, wait until all comparisons are completed.
    const isConsistentPair = await Promise.all(isConsistentPair$);
    // Normalize the count of consistent pairs by dividing it by the original number of pairs.
    return sortedPairs.length
      ? (isConsistentPair.filter((isConsistent) => isConsistent).length + 1) /
          sortedPairs.length
      : 1;
  }
}
