import {
  AfterViewInit,
  Component,
  ElementRef,
  Input,
  ViewChild,
} from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { PageScrollInstance, PageScrollService } from 'ngx-page-scroll-core';

const SCROLL_DURATION = 500; //ms
const SCROLL_OFFSET = 68; //px, height of the app nav bar

@Component({
  selector: 'models4insight-hero',
  templateUrl: 'hero.component.html',
  styleUrls: ['hero.component.scss'],
})
export class HeroComponent implements AfterViewInit {
  @Input() subtitle: string;
  @Input() title: string;

  @ViewChild(RouterOutlet, { static: true })
  readonly routerOutlet: RouterOutlet;

  @ViewChild('nav', { static: true }) private readonly nav: ElementRef;

  private pageScrollInstance: PageScrollInstance;

  constructor(private readonly pageScrollService: PageScrollService) {}

  ngAfterViewInit() {
    // Create the scroll only after the view has been initialized.
    // This prevents from scrolling on initial page load rather than on navigation.
    this.pageScrollInstance = this.pageScrollService.create({
      document,
      duration: SCROLL_DURATION,
      interruptible: true,
      scrollOffset: SCROLL_OFFSET,
      scrollTarget: this.nav.nativeElement,
    });
  }

  /** Scroll to the top of the navigation whenever a new component is loaded */
  onActivate(): void {
    if (this.pageScrollInstance) {
      this.pageScrollService.start(this.pageScrollInstance);
    }
  }
}
