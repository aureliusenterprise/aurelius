function componentToHex(c: number) {
  const hex = c.toString(16);
  return hex.length === 1 ? `0${hex}` : hex;
}

/**
 * Converts an rgb value to a hex color value, prefixed with a #. Defaults to #000000 if one of the given values cannot be mapped to a hex value.
 * @param r the redness value between 0 and 255
 * @param g the blueness value between 0 and 255
 * @param b the greenness value between 0 and 255
 */
export function rgbToHex(r: number, g: number, b: number) {
  return typeof r === 'number' && typeof g === 'number' && typeof b === 'number'
    ? `#${componentToHex(r)}${componentToHex(g)}${componentToHex(b)}`
    : '#000000';
}
