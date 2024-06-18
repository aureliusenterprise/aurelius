import { Directive, OnDestroy } from '@angular/core';

@Directive()
export class BaseComponent implements OnDestroy {
  ngOnDestroy() {}
}
