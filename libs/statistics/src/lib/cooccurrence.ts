import { intersectionWith, isEqual } from 'lodash';

/**
 * Calculates a cooccurence index between two datasets.
 * The cooccurrence value is symmetric.
 */
export async function cooccurrence<A, B>(
  /** The dataset for which to calculate the cooccurrence index */
  values: A[],
  /** The other dataset for which to calculate the cooccurrence index */
  otherValues: B[]
): Promise<number> {
  // Find the intersection between the two datasets
  const intersection = intersectionWith(values, otherValues, isEqual);
  // Calculate the cooccurrence metric
  const f1 = (2 * intersection.length) / (values.length + otherValues.length);
  // Return the metric
  return f1;
}
