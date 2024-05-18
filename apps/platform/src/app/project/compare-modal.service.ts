import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable()
export class CompareModalService {
  private readonly activateModal$ = new Subject<[string, number?]>();

  activateModal(branchName: string, version?: number) {
    this.activateModal$.next([branchName, version]);
  }

  get onModalActivated() {
    return this.activateModal$.asObservable();
  }
}
