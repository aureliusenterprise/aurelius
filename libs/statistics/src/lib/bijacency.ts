import { pairs } from '@models4insight/utils';
import { isEqual } from 'lodash';
import BiMap from 'mnemonist/bi-map';

export interface BijacencyOptions {
  /**
   * Whether or not to short cirquit the calculation if the datasets are non-bijacent.
   * When short cirquiting, the returned bijacency index is always 0 (non-bijacent) or 1 (bijacent).
   * Enable short cirquting to improve performance if you don't care about the precise bijaceny index.
   */
  shortCirquiting?: boolean;
}

/**
 * Calculates the bijacency index between two datasets by comparing the given values against the given other values.
 * Two datasets are bijacent if every unique value A maps against exactly one unique value B.
 * An index of 1 indicates that the two datasets are fully bijacent.
 * The bijaceny value is symmetric.
 */
export async function bijacency<A, B>(
  /* The values for which to calculate the bijacency index  */
  values: Iterable<A>,
  /* The other values for which to calculate the bijacency index */
  otherValues: Iterable<B>,
  { shortCirquiting = false }: BijacencyOptions
): Promise<number> {
  // Create pairs out of the values for each row of A and B
  const valuePairs = pairs(values, otherValues);

  // Count the total number of pairs and the number of non bijacent pairs
  let pairCount = 0,
    notBijacentCount = 0;

  // This map keeps a cross reference of all its key-value pairs.
  // This means you can look up a key to get its corresponding value, and look up a value to get its corresponding key.
  // In a bijacent dataset of values (a, b), we should always find `b` for `a`, and `a` for `b` if we have seen any of these values before.
  // If the lookup values differ, the dataset is not bijacent.
  const biMap = new BiMap<A, B>();

  for (const [value, otherValue] of valuePairs) {
    if (!biMap.has(value)) {
      biMap.set(value, otherValue);
    } else if (!isEqual(biMap.get(value), otherValue)) {
      if (shortCirquiting) {
        return 0;
      }
      notBijacentCount++;
    }
    pairCount++;
  }

  return pairCount > 0 ? (pairCount - notBijacentCount) / pairCount : 0;
}
