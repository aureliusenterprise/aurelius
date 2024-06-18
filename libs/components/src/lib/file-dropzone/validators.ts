import { FileDropzone } from './file-dropzone';

/**
 * Checks whether the current file matches any of the given extensions.
 * You can pass an empty array to validate all extensions.
 * By default, all extensions are valid.
 */
export function extension(validExtensions: string[] = []) {
  return (control: FileDropzone) => {
    const file: File = control.value;
    return file &&
      file.name &&
      validExtensions &&
      validExtensions.length > 0 &&
      !validExtensions.includes(file.name.split('.').pop())
      ? { extension: true }
      : null;
  };
}
