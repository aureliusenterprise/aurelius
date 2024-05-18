const DEFAULT_RANGE = -9999;

/**
 * Generates a placeholder ID for use when creating entities or relationships in Atlas
 */
export function generatePlaceholderId(range: number = DEFAULT_RANGE) {
  return Math.floor(Math.random() * range).toString();
}
