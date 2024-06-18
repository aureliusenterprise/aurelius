/**
 * Converts a byte array to its UTF-16 string representation
 * @param bytes the byte array to convert
 * @param sliceSize the number of bytes to process per chunk
 */
export function bytesToBinaryString(bytes: Uint8Array, sliceSize = 512) {
  const len = bytes.byteLength;
  let binary = '';
  for (let i = 0; i < len; i += sliceSize) {
    binary += String.fromCharCode(...bytes.slice(i, i + sliceSize));
  }
  return binary;
}
