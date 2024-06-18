import { sum, words } from 'lodash';

/**
 * A statistical summary returned by the wordCount function.
 * Contains the minimum, maximum and average number of words per row,
 * as well as the total number of words in the dataset.
 */
export interface WordCountSummary {
  average: number;
  min: number;
  max: number;
  sum: number;
}

/**
 * For an array of strings, returns a summary of the average, minimum and maximum words per row, as well as the sum of words in the dataset.
 */
export async function wordCount(
  /** The array of strings for which to calculate the statistics */
  data: string[]
): Promise<WordCountSummary> {
  // Map each string in the dataset to its word count
  const wordCounts = await Promise.all(
    data.map(async (row) => words(row).length)
  );

  // Calculate the statistics and return a summary
  const totalWordCount = sum(wordCounts);

  return {
    average: wordCounts.length ? totalWordCount / wordCounts.length : 0,
    min: Math.min(...wordCounts),
    max: Math.max(...wordCounts),
    sum: totalWordCount,
  };
}
