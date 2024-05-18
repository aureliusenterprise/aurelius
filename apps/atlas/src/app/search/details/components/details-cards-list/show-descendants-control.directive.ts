import {
  Directive,
  ElementRef,
  Injectable,
  OnDestroy,
  Renderer2,
} from '@angular/core';
import { CheckboxControlValueAccessor } from '@angular/forms';
import { BasicStore } from '@models4insight/redux';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';

export interface ShowDescendantsState {
  readonly showDescendants?: boolean;
}

@Injectable()
export class ShowDescendantsService extends BasicStore<ShowDescendantsState> {
  readonly showDescendants$: Observable<boolean>;

  constructor() {
    super({ defaultState: { showDescendants: false } });
    this.showDescendants$ = this.select('showDescendants');
  }

  set showDescendants(showDescendants: boolean) {
    this.update({
      description: 'Show descendants state updated',
      payload: { showDescendants },
    });
  }
}

@Directive({
  selector: 'models4insightShowDescendantsControl input[type="checkbox"]',
})
export class ShowDescendantsControlDirective
  extends CheckboxControlValueAccessor
  implements OnDestroy
{
  constructor(
    _renderer: Renderer2,
    _elementRef: ElementRef,
    private readonly showDescendantsService: ShowDescendantsService
  ) {
    super(_renderer, _elementRef);

    this.showDescendantsService.showDescendants$
      .pipe(untilDestroyed(this))
      .subscribe((showDescendants) => this.writeValue(showDescendants));

    this.registerOnChange(
      (showDescendants: boolean) =>
        (this.showDescendantsService.showDescendants = showDescendants)
    );
  }

  ngOnDestroy() {}
}
