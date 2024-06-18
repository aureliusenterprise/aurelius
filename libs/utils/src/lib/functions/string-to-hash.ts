/**
 * Returns a unique hash for the given string
 */
export function stringToHash(string: string): number {
  return string
    .split('')
    .reduce(
      (prevHash, currVal) =>
        ((prevHash << 5) - prevHash + currVal.charCodeAt(0)) | 0,
      0
    );
}
