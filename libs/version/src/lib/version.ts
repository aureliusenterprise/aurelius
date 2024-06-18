import { hash as gitHash } from 'git-version.json';
import { version as packageVersion } from 'package.json';

/**
 * Returns a version string composed of the node package version and the git hash, delimited by a `#` sign.
 * If not in production mode, the version string includes a `-dev` suffix.
 * @param production Whether or not the application is running in production mode. Defaults to `false`.
 */
export function version(production: boolean = false): string {
  return `${packageVersion}#${gitHash}${production ? '' : '-dev'}`;
}
