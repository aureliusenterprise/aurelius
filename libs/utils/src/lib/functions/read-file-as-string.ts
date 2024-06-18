/**
 * Returns the content of the given `file` as a `string`
 */
export async function readFileAsString(file: File): Promise<string> {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = () => resolve(reader.result as string);
    reader.onerror = () => reject(reader.error);
    reader.onabort = () => reject('Read process aborted');

    reader.readAsText(file);
  });
}
