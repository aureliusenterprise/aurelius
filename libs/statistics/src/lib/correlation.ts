import { pairs } from '@models4insight/utils';
import { isEqual } from 'lodash';

/**
 * Calculates the correlation index between two datasets.
 * The correlation value is symmetric.
 */
export async function correlation<A, B>(
  /** The dataset for which to calculate the correlation index */
  values: A[],
  /** The other dataset for which to calculate the correlation index */
  otherValues: B[]
): Promise<number> {
  // Count the number of times the value at index i is equal between the two datasets
  const isCorrelatedPair = Array.from(pairs(values, otherValues)).map(isEqual);

  // Normalize the count by dividing it by the length of the longest dataset
  const maxLength = Math.max(values.length, otherValues.length);

  return maxLength
    ? isCorrelatedPair.filter((isCorrelated) => isCorrelated).length / maxLength
    : 1;
}
