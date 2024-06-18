declare var document: any;
declare var navigator: any;

async function fallbackCopyValueToClipboard(value: string) {
  const textArea = document.createElement('textarea');
  textArea.value = value;
  textArea.style.position = 'fixed'; //avoid scrolling to bottom
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();
  return new Promise<void>((resolve, reject) => {
    try {
      document.execCommand('copy')
        ? resolve()
        : reject(`Value ${value} could not be copied to the clipboard!`);
    } catch (e) {
      reject(e);
    } finally {
      document.body.removeChild(textArea);
    }
  });
}

/**
 * Writes the given value to the clipboard.
 * @param value The value that should be written to the clipboard
 */
export async function copyToClipboard(value: string): Promise<void> {
  // If the clipboard API is supported by the browser, use it.
  // Otherwise, use a fallback method instead.
  return navigator.clipboard
    ? navigator.clipboard.writeText(value)
    : fallbackCopyValueToClipboard(value);
}
