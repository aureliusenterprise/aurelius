import { AfterViewInit, Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { AuthenticationService, Credentials } from '@models4insight/authentication';
import { fromEvent, Observable } from 'rxjs';
import { shareReplay } from 'rxjs/operators';
import { faCopy } from '@fortawesome/free-regular-svg-icons';
import { faEllipsisH, faGlobe } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-insights',
  templateUrl: './insights.component.html',
  styleUrls: ['./insights.component.scss']
})
export class InsightsComponent implements OnInit, AfterViewInit {
  @ViewChild('credentialsDisplay', { static: false })
  credentialsDisplay: ElementRef;
  @ViewChild('credentialsDisplayCopy', { static: false })
  credentialsDisplayCopy: ElementRef;

  credentials$: Observable<Credentials>;

  faCopy = faCopy;
  faGlobe = faGlobe;
  faEllipsisH = faEllipsisH;

  constructor(private authenticationService: AuthenticationService) {}

  ngOnInit() {
    this.credentials$ = this.authenticationService
      .credentials()
      .pipe(shareReplay());
  }

  ngAfterViewInit() {
    fromEvent(this.credentialsDisplayCopy.nativeElement, 'click').subscribe(
      () => this.copyCredentialsToClipboard()
    );
  }

  accountManagement() {
    this.authenticationService.accountManagement();
  }

  copyCredentialsToClipboard() {
    const input = this.credentialsDisplay.nativeElement;
    input.select();
    document.execCommand('copy');
    input.blur();
  }
}
