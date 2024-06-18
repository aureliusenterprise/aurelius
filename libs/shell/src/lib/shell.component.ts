import { Component, HostListener } from '@angular/core';
import { Logger } from '@models4insight/logger';
import { ShellService } from './shell.service';

const log = new Logger('ShellComponent');

@Component({
  selector: 'models4insight-shell',
  templateUrl: './shell.component.html',
  styleUrls: ['./shell.component.scss'],
})
export class ShellComponent {
  constructor(private shellService: ShellService) {}

  /** Scroll to the top of the page whenever a new component is loaded */
  onActivate(): void {
    const scrollToTop = window.setInterval(() => {
      const pos = window.pageYOffset;
      if (pos > 0) {
        window.scrollTo(0, pos - 20); // how far to scroll on each step
      } else {
        window.clearInterval(scrollToTop);
      }
    }, 16);
  }

  /**
   * Triggers a check whether the current authentication token is still valid whenever the user (re-)focusses the shell
   */
  @HostListener('window:focus')
  onFocus(): void {
    this.shellService.updateToken();
  }
}
