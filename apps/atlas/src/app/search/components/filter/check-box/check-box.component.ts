import { Component, Input, OnDestroy } from '@angular/core';
import { FormControl } from '@angular/forms';
import {
  AppSearchDocument,
  AppSearchFilterValue
} from '@models4insight/atlas/api';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { CheckBoxService } from './check-box.service';

@Component({
  selector: 'models4insight-check-box',
  templateUrl: './check-box.component.html',
  styleUrls: ['./check-box.component.scss'],
  providers: [CheckBoxService],
})
export class CheckBoxComponent<
  T extends AppSearchDocument = AppSearchDocument,
  K extends keyof T = any
> implements OnDestroy
{
  readonly control: FormControl<boolean> = new FormControl<boolean>(false);

  readonly value$: Observable<AppSearchFilterValue<T, K>>;
  readonly count$: Observable<number>;

  constructor(private readonly filterChoiceService: CheckBoxService<T, K>) {
    this.value$ = this.filterChoiceService.value$;
    this.count$ = this.filterChoiceService.count$;

    this.control.valueChanges
      .pipe(untilDestroyed(this))
      .subscribe((value) =>
        this.filterChoiceService.updateFilterSelection(value)
      );

    this.filterChoiceService.isSelected$
      .pipe(untilDestroyed(this))
      .subscribe((isSelected) =>
        this.control.patchValue(isSelected, { emitEvent: false })
      );
  }

  ngOnDestroy() {}

  @Input()
  set count(count: number) {
    this.filterChoiceService.update({
      description: 'New count available',
      payload: { count },
    });
  }

  @Input()
  set facet(facet: K) {
    this.filterChoiceService.update({
      description: 'New facet available',
      payload: { facet },
    });
  }

  @Input()
  set value(value: AppSearchFilterValue<T, K>) {
    this.filterChoiceService.update({
      description: 'New value available',
      payload: { value },
    });
  }
}
