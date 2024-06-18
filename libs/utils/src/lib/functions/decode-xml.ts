const specialCharactersMap = {
  '&amp;': '&',
  '&quot;': '"',
  '&lt;': '<',
  '&gt;': '>',
  '&#xA;': '\n',
};

const pattern = new RegExp(Object.keys(specialCharactersMap).join('|'), 'g');

function replacer(specialCharacter: keyof typeof specialCharactersMap) {
  return specialCharactersMap[specialCharacter];
}

/**
 * Replaces XML encoded characters in the given string with their respective decoded characters.
 * @param xml The string that contains XML encoded characters
 */
export function decodeXML(xml: string): string {
  if (!xml) return xml;
  return xml.replace(pattern, replacer);
}
