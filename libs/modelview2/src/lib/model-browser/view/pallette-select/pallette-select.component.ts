import { Component, OnInit } from '@angular/core';
import { faPalette } from '@fortawesome/free-solid-svg-icons';
import {
  AbstractSelectComponent,
  defaultSelectContext,
  ModalContext,
  Select,
  SelectContext,
  SortableTableShellConfig,
} from '@models4insight/components';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { ColorPallette, ColorViewService } from '../../../color-view.service';

export interface PalletteSelectOption {
  description: string;
  name: string;
  pallette: ColorPallette;
}

const optionsByPalette: Dictionary<PalletteSelectOption> = {
  diverging: {
    description: 'Colors on a diverging scale',
    name: 'Diverging',
    pallette: 'diverging',
  },
  qualitative: {
    description: 'Distinct colors per category',
    name: 'Qualitative',
    pallette: 'qualitative',
  },
  rainbow: {
    description: 'Colors of the rainbow',
    name: 'Rainbow',
    pallette: 'rainbow',
  },
  sequential: {
    description: 'Colors on a progressive scale',
    name: 'Sequential',
    pallette: 'sequential',
  },
};

const pallettes: PalletteSelectOption[] = Object.values(optionsByPalette);

const tableConfig: SortableTableShellConfig<PalletteSelectOption> = {
  name: { displayName: 'Name', description: 'The name of the palette' },
  description: {
    displayName: 'Description',
    description: 'The use case of the palette',
  },
};

const modalContext: ModalContext = {
  cancel: 'Close',
  closeOnConfirm: true,
  title: 'Choose a color palette',
};

const selectContext: SelectContext = {
  ...defaultSelectContext,
  icon: faPalette,
  label: 'Color palette',
  nullInputMessage: 'Please select a palette',
  requiredErrorMessage: 'Please select a palette',
  searchModalContext: modalContext,
  searchTableConfig: tableConfig,
};

@Component({
  selector: 'models4insight-pallette-select',
  templateUrl: 'pallette-select.component.html',
  styleUrls: ['pallette-select.component.scss'],
})
export class PalletteSelectComponent
  extends AbstractSelectComponent<PalletteSelectOption>
  implements OnInit
{
  readonly selectContext = selectContext;

  constructor(private readonly colorViewService: ColorViewService) {
    super();
  }

  ngOnInit() {
    this.control = new Select(true);
    this.data = pallettes;
    this.displayField = 'name';

    // Whenever the palette changes in the store, update the control
    this.colorViewService
      .select('colorPallette')
      .pipe(untilDestroyed(this))
      .subscribe((palette) =>
        this.control.patchValue(optionsByPalette[palette], { emitEvent: false })
      );

    // Whenever a new palette is selected, update the store
    this.control.valueChanges
      .pipe(untilDestroyed(this))
      .subscribe(({ pallette }) =>
        this.colorViewService.update({
          description: 'New palette selected',
          payload: { colorPallette: pallette },
        })
      );
  }
}
