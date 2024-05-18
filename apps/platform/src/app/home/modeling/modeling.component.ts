import { AfterViewInit, Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { faCopy } from '@fortawesome/free-regular-svg-icons';
import { AuthenticationService, Credentials } from '@models4insight/authentication';
import { CreateProjectModalComponent } from '@models4insight/components';
import { fromEvent, Observable } from 'rxjs';
import { shareReplay } from 'rxjs/operators';

@Component({
  selector: 'models4insight-modeling',
  templateUrl: './modeling.component.html',
  styleUrls: ['./modeling.component.scss']
})
export class ModelingComponent implements OnInit, AfterViewInit {
  @ViewChild('credentialsDisplay', { static: false })
  private readonly credentialsDisplay: ElementRef;
  @ViewChild('credentialsDisplayCopy', { static: false })
  private readonly credentialsDisplayCopy: ElementRef;
  @ViewChild(CreateProjectModalComponent, { static: true })
  private readonly createProjectModal: CreateProjectModalComponent;

  credentials$: Observable<Credentials>;
  
  faCopy = faCopy;
  isLoading = false;

  constructor(
    private authenticationService: AuthenticationService
  ) {}

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

  activateModal() {
    this.createProjectModal.activate();
  }

  copyCredentialsToClipboard() {
    const input = this.credentialsDisplay.nativeElement;
    input.select();
    document.execCommand('copy');
    input.blur();
  }
}
