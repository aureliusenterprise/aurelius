import { Injectable } from '@angular/core';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { ManagedTask } from '@models4insight/task-manager';
import { enumerate, untilDestroyed } from '@models4insight/utils';
import pallette from 'google-palette';
import { Dictionary } from 'lodash';
import { combineLatest } from 'rxjs';
import { switchMap } from 'rxjs/operators';

export type FixedColorPalette = 'compare';

export const fixedLegends: {
  readonly [name in FixedColorPalette]?: Dictionary<string>;
} = {
  compare: {
    'model 1 only': '#AEC6EF',
    'model 1 view only': '#EAF0F2',
    changed: '#FFB347',
    'changed in view': '#FFD599',
    'model 2 only': '#77DD77',
    'model 2 view only': '#BBEEBB',
  },
};

export type DynamicColorPalette =
  | 'diverging'
  | 'qualitative'
  | 'rainbow'
  | 'sequential';

export type ColorPallette = DynamicColorPalette | FixedColorPalette;

export interface ColorViewStoreContext {
  readonly bucketMapping?: Dictionary<string>;
  readonly colorMapping?: Dictionary<string>;
  readonly colorPallette?: ColorPallette;
  readonly isCreatingColorMapping?: boolean;
  readonly isCreatingLegend?: boolean;
  readonly isPalletteFixed?: boolean;
  readonly legend?: Dictionary<string>;
}

const defaultState: ColorViewStoreContext = {
  colorPallette: 'qualitative',
};

@Injectable()
export class ColorViewService extends BasicStore<ColorViewStoreContext> {
  constructor() {
    super({ defaultState });
    this.init();
  }

  private init() {
    // Whenever the color buckets or the color pallette change, update the legend
    combineLatest([this.select('bucketMapping'), this.select('colorPallette')])
      .pipe(
        switchMap(([bucketMapping, colorPallette]) =>
          this.handleCreateLegend(bucketMapping, colorPallette)
        ),
        untilDestroyed(this)
      )
      .subscribe();

    // Whenever the color buckets or the legend change, update the color mapping
    combineLatest([this.select('bucketMapping'), this.select('legend')])
      .pipe(
        switchMap(([bucketMapping, legend]) =>
          this.handleCreateColorMapping(bucketMapping, legend)
        ),
        untilDestroyed(this)
      )
      .subscribe();
  }

  getBucketById(id: string) {
    return this.select(['bucketMapping', id], { includeFalsy: true });
  }

  getColorById(id: string) {
    return this.select(['colorMapping', id], { includeFalsy: true });
  }

  @ManagedTask('Creating the color view mapping')
  @MonitorAsync('isCreatingColorMapping')
  private async handleCreateColorMapping(
    bucketMapping: Dictionary<string>,
    legend: Dictionary<string>
  ) {
    const colorMapping = {};
    for (const [conceptId, bucket] of Object.entries(bucketMapping)) {
      colorMapping[conceptId] = legend[bucket];
    }

    this.update({
      description: 'New color mapping available',
      payload: { colorMapping },
    });
  }

  @ManagedTask('Creating the color view legend')
  @MonitorAsync('isCreatingLegend')
  private async handleCreateLegend(
    bucketMapping: Dictionary<string>,
    colorPallette: ColorPallette
  ) {
    let legend = fixedLegends[colorPallette];

    if (!legend) {
      const buckets = new Set(Object.values(bucketMapping));

      const colors = pallette(colorPallette, buckets.size);

      legend = {};
      for (const [bucket, index] of enumerate(buckets)) {
        const color = colors[index % colors.length];
        legend[bucket] = `#${color}`;
      }
    }

    this.update({
      description: 'New legend available',
      payload: { legend },
    });
  }
}
