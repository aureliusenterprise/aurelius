import { Component, Inject, Optional } from '@angular/core';
import { faCopyright } from '@fortawesome/free-regular-svg-icons';
import { VersionService } from '@models4insight/version';
import { ShellConfig, ShellConfigService } from '../shell-config.service';

@Component({
  selector: 'models4insight-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.scss'],
})
export class FooterComponent {
  readonly appName: string;
  readonly copyright: number;
  readonly version: string;

  readonly faCopyright = faCopyright;

  constructor(
    versionService: VersionService,
    @Optional()
    @Inject(ShellConfigService)
    config: ShellConfig = {}
  ) {
    this.appName = config.appName;
    this.copyright = config.appCopyright;
    this.version = versionService.appVersion;
  }
}
