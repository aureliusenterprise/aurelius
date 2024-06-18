import { Inject, Injectable, Optional } from '@angular/core';
import { repositoryVersion } from '@models4insight/repository';
import gitVersion from 'git-version.json';
import packageDef from 'package.json';
import { VersionConfig, VersionConfigService } from './version-config.service';

@Injectable()
export class VersionService {
  /** The name of the application */
  readonly appName: string;

  /**
   * The version string for this application.
   * The version string is composed of the node package version and the git hash, delimited by a `#` sign.
   * If not in production mode, the version string also includes a `-dev` suffix.
   */
  readonly appVersion: string;

  constructor(
    @Optional()
    @Inject(VersionConfigService)
    private readonly config: VersionConfig = {}
  ) {
    this.appName = this.config.appName;
    this.appVersion = `${packageDef.version}#${gitVersion.hash}${
      this.config.production ? '' : '-dev'
    }`;
  }

  /**
   * Retrieves the version string of the repository to which the application connects.
   * The version string is composed of the release number and the git hash, delimited by a `#` sign.
   * If the version string could not be retrieved for any reason, returns `unknown` instead.
   * @param forceUpdate Whether or not to refresh the cache
   */
  async getRepositoryVersion(forceUpdate: boolean = false): Promise<string> {
    try {
      const { version } = await repositoryVersion({ forceUpdate }).toPromise();
      return version;
    } catch {
      return 'unknown';
    }
  }

  /**
   * Returns an object which represents the version of the app and connected services.
   * @param forceUpdate Whether or not to refresh the cache
   */
  async getVersionDescriptor(forceUpdate: boolean = false) {
    // Resolve the version strings of the connected services concurrently
    const [repository] = await Promise.all([
      this.getRepositoryVersion(forceUpdate),
    ]);

    return {
      app: this.appVersion,
      production: this.config.production,
      repository,
    };
  }
}
