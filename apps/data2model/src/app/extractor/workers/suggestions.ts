import { consistency, cooccurrence, correlation, entropy, wordCount, WordCountSummary } from '@models4insight/statistics';
import { combinations, Stream } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { v4 as uuid } from 'uuid';
import { SuggestedRelation, Suggestions } from '../extractor-types';

export interface SuggestionsContext<
  T extends Dictionary<any> = Dictionary<any>
> {
  readonly data: T[];
  readonly lowerEntropyBound?: number;
  readonly lowerF1Bound?: number;
}

export async function suggestions<T extends Dictionary<any>>({
  data,
  lowerEntropyBound = 0.2,
  lowerF1Bound = 0.2
}: SuggestionsContext<T>): Promise<Suggestions<T>> {
  const keySet = new Set<keyof T>();

  await Promise.all(
    data.map(
      async row =>
        await Promise.all(
          Object.keys(row).map(async header => keySet.add(header as keyof T))
        )
    )
  );

  const keys = Array.from(keySet);

  // Calculate the entropy for every column
  const pairs = await Promise.all(
    keys.map(async key => [key, await entropy(data, key)] as [string, number])
  );
  const entropyMap: Dictionary<number> = pairs.reduce(
    (map, [key, value]) => ({ ...map, [key]: value }),
    {} as Dictionary<number>
  );
  const maxEntropy = Math.max(...(Object.values(entropyMap) as number[]));

  // Filter the columns to only include those within the entropy threshold
  const filteredKeys = keys.filter(
    key => maxEntropy * lowerEntropyBound <= entropyMap[key as string]
  );

  // Determine which columns contain strings
  const stringColumns = filteredKeys.filter(
    key =>
      data.length === 0 || typeof data.find(row => !!row[key])[key] === 'string'
  );

  // Calculate all combination pairs of keys in the dataset
  const stringKeyCombinations = combinations(stringColumns);

  // Sort the columns containing strings by entropy from high to low
  const nameColumns = stringColumns.sort(
    (a, b) => entropyMap[b as string] - entropyMap[a as string]
  );

  // Calculate the word count statistics per text column. The result is a map of the statistics keyed by the column name.
  const wordCountMap = Promise.all(
    stringColumns.map(
      async key =>
        [key, await wordCount(data.map(row => row[key]) as any[])] as [
          keyof T,
          WordCountSummary
        ]
    )
  ).then(summaries =>
    summaries.reduce(
      (map, [key, value]) => ({ ...map, [key as string]: value }),
      {} as Dictionary<WordCountSummary>
    )
  );

  // Calculate the remaining metrics that are based off combinations of keys.
  const metricsMatrix = Promise.all(
    Stream.from(stringKeyCombinations).map(async ([a, b]) => {
      const [values, otherValues] = await Promise.all([
        Promise.all(data.map(async row => row[a])),
        Promise.all(data.map(async row => row[b]))
      ]);

      const [
        referenceConsistency,
        reverseConsistency,
        f1,
        correlationIndex,
        transitionEntropy
      ] = await Promise.all([
        consistency(values, otherValues, { shortCirquiting: true }),
        consistency(otherValues, values, { shortCirquiting: true }),
        cooccurrence(values, otherValues),
        correlation(values, otherValues),
        entropy(data, [a, b])
      ]);

      return {
        correlation: correlationIndex,
        f1: f1,
        referenceConsistency: referenceConsistency,
        reverseConsistency: reverseConsistency,
        source: a,
        target: b,
        transitionEntropy: transitionEntropy
      };
    })
  );

  // Wait until all calculations are complete, and merge the results into a single matrix
  const [wordCounts, metrics] = await Promise.all([
    wordCountMap,
    metricsMatrix
  ]);

  // Derive the maximum values of each of our metrics for rank normalization
  const maxWordCount = Math.max(
    ...Object.values(wordCounts).map(({ sum }) => sum)
  );
  const maxCooccurrence = Math.max(...metrics.map(({ f1 }) => f1));
  const maxCorrelation = Math.max(
    ...metrics.map(({ correlation }) => correlation)
  );
  const maxTransitionEntropy = Math.max(
    ...metrics.map(({ transitionEntropy }) => transitionEntropy)
  );

  // Relationships with a cooccurrence rate above the threshold are classified as dynamic. Rank these relations accordingly.
  const dynamicRelationships$ = Promise.all(
    metrics
      .filter(
        ({ f1 }) => maxCooccurrence > 0 && f1 >= maxCooccurrence * lowerF1Bound
      )
      .map(
        async row =>
          ({
            ...row,
            sourceWordCount: (
              wordCounts[row.source as string] || ({} as WordCountSummary)
            ).sum,
            targetWordCount: (
              wordCounts[row.target as string] || ({} as WordCountSummary)
            ).sum,
            rank:
              // Correlation is a negative influence, so we weigh it by -2 for now.
              (maxCorrelation ? (row.correlation * -2) / maxCorrelation : 0) +
              (maxCooccurrence ? row.f1 / maxCooccurrence : 0) +
              (maxTransitionEntropy
                ? row.transitionEntropy / maxTransitionEntropy
                : 0),
            type: 'dynamic'
          } as SuggestedRelation<T>)
      )
  );

  // Relationships which are fully consistent are classified as structural. Rank these relations accordingly.
  const structuralRelationships$ = Promise.all(
    metrics
      .filter(
        ({ referenceConsistency, reverseConsistency }) =>
          referenceConsistency === 1 || reverseConsistency === 1
      )
      .map(async row => {
        const sourceWordCount = (
            wordCounts[row.source as string] || ({} as WordCountSummary)
          ).sum,
          targetWordCount = (
            wordCounts[row.target as string] || ({} as WordCountSummary)
          ).sum;

        return {
          ...row,
          sourceWordCount: sourceWordCount,
          targetWordCount: targetWordCount,
          rank:
            3 *
              (maxTransitionEntropy
                ? row.transitionEntropy / maxTransitionEntropy
                : 0) -
            (maxCorrelation ? row.correlation / maxCorrelation : 0) -
            (maxWordCount ? sourceWordCount / maxWordCount : 0) -
            (maxWordCount ? targetWordCount / maxWordCount : 0),
          type: 'structural'
        } as SuggestedRelation<T>;
      })
  );

  const otherRelationships$ = Promise.all(
    metrics
      .filter(
        ({ f1, referenceConsistency, reverseConsistency }) =>
          (maxCooccurrence === 0 || f1 < maxCooccurrence * lowerF1Bound) &&
          referenceConsistency !== 1 &&
          reverseConsistency !== 1
      )
      .map(async row => {
        const sourceWordCount = (
            wordCounts[row.source as string] || ({} as WordCountSummary)
          ).sum,
          targetWordCount = (
            wordCounts[row.target as string] || ({} as WordCountSummary)
          ).sum;

        return {
          ...row,
          sourceWordCount: sourceWordCount,
          targetWordCount: targetWordCount,
          rank:
            2 *
              (maxTransitionEntropy
                ? row.transitionEntropy / maxTransitionEntropy
                : 0) -
            (maxCorrelation ? row.correlation / maxCorrelation : 0) -
            (maxWordCount ? sourceWordCount / maxWordCount : 0) -
            (maxWordCount ? targetWordCount / maxWordCount : 0),
          type: 'other'
        } as SuggestedRelation<T>;
      })
  );

  const [
    dynamicRelationships,
    structuralRelationships,
    otherRelationships
  ] = await Promise.all([
    dynamicRelationships$,
    structuralRelationships$,
    otherRelationships$
  ]);

  // Construct the suggestions object. Relations are keyed by a UUID.
  const suggestions = {
    columns: filteredKeys.map(key => ({
      column: key,
      entropy: entropyMap[key as string]
    })),
    labels: nameColumns.map(name => ({
      column: name,
      entropy: entropyMap[name as string]
    })),
    relations: [
      ...dynamicRelationships,
      ...structuralRelationships,
      ...otherRelationships
    ]
      .sort((a, b) => b.rank - a.rank)
      .reduce(
        (map, transition) => {
          const id = uuid();
          return {
            ...map,
            [id]: {
              id: id,
              ...transition
            }
          };
        },
        {} as Dictionary<SuggestedRelation<T>>
      )
  };

  return suggestions;
}
