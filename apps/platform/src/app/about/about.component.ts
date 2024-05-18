import { Component } from '@angular/core';
import { faBookmark } from '@fortawesome/free-regular-svg-icons';
import { VersionService } from '@models4insight/version';

@Component({
  selector: 'models4insight-about',
  templateUrl: './about.component.html',
  styleUrls: ['./about.component.scss']
})
export class AboutComponent {
  readonly version: string;
  readonly faBookmark = faBookmark;

  constructor(versionService: VersionService) {
    this.version = versionService.appVersion;
  }
}
