import { bijacency } from '@models4insight/statistics';
import { ComplexSet } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { ExtractorDatasetEntry, SuggestedColumn } from '../extractor-types';

export interface BijacencyMapContext {
  columns: SuggestedColumn[];
  data: ExtractorDatasetEntry[];
  name: string;
  source: string;
  target: string;
  valuesPerColumn: Dictionary<any[]>;
}

export async function bijacencyMap({
  data,
  columns,
  source,
  target,
  name,
  valuesPerColumn
}: BijacencyMapContext) {
  // Create a limited subset of the data based on the source, target and name columns.
  // This combination of values always identifies a relationship.
  const identifiers = data.map(row =>
    [row[source], row[target], row[name]].filter(
      value => value !== undefined && value !== null
    )
  );
  // Filter out duplicate identifiers
  const identifierSet = new ComplexSet<any[]>();
  identifierSet.add(identifiers);

  // Next, calculate whether or not any of the other columns in the dataset are bijacent with the identifiers
  // We check whether we can find any single column which is bijacent with the combination of source, target and name,
  // since we would prefer to use a single column instead.
  const bijacencies = await Promise.all(
    columns
      .filter(label => ![source, target, name].includes(label.column as string))
      .map(async label => ({
        label: label,
        value: await bijacency(
          valuesPerColumn[label.column],
          identifierSet.items,
          {
            shortCirquiting: true
          }
        )
      }))
  );

  const result = bijacencies.reduce(
    (map, item) => ({
      ...map,
      [item.label.column]: item.value
    }),
    {} as Dictionary<number>
  );

  return result;
}
