import { Component } from '@angular/core';
import { userAgentIsInternetExplorer } from '@models4insight/utils';

@Component({
  selector: 'models4insight-extractor',
  templateUrl: 'extractor.component.html',
  styleUrls: ['extractor.component.scss']
})
export class ExtractorComponent {
  /**
   * Used to hide the suggestions tab if the browser is an Internet Explorer variant
   */
  readonly userAgentIsInternetExplorer = userAgentIsInternetExplorer();
}
