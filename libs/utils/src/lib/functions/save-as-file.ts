import { saveAs } from 'file-saver';

declare var window: any;

/**
 * Saves content in the form of a `string` or `Blob` to the user's device as a file with the given name.
 */
export function saveAsFile(content: string | Blob, name: string) {
  if (typeof content === 'string') {
    content = new Blob([content]);
  }
  if (window && window.navigator.msSaveOrOpenBlob) {
    window.navigator.msSaveOrOpenBlob(content, name);
  } else if (window && window.navigator.msSaveBlob) {
    window.navigator.msSaveBlob(content, name);
  } else {
    const objectUrl = window.URL.createObjectURL(content);
    saveAs(objectUrl, name);
  }
}
