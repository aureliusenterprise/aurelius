import { Dictionary, identity } from 'lodash';

function buildPath(...names: string[]) {
  // Filter out null values and empty strings before joining
  return names.filter(identity).join('/');
}

async function parseOrganization(
  item: any,
  currentPath: string
): Promise<Dictionary<string>> {
  const id = item['@identifierRef'];
  if (id) {
    return { [id]: currentPath };
  }
  const children = item['ar3_item'];
  if (children) {
    const folderName = item['ar3_label']?.[0]['value'];
    const subPath = buildPath(currentPath, folderName);
    return parseOrganizations(children, subPath);
  }
  // If the item has no idref and no children, it's an empty folder
  return {};
}

export async function parseOrganizations(
  organizations: any[] = [],
  currentPath = ''
): Promise<Dictionary<string>> {
  const parsedOrganizations = organizations.map((item) =>
    parseOrganization(item, currentPath)
  );

  let result: Dictionary<string> = {};

  for await (const parsedOrganization of parsedOrganizations) {
    result = { ...result, ...parsedOrganization };
  }

  return result;
}
