import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { untilDestroyed } from '@models4insight/utils';
import { BehaviorSubject, Observable, ReplaySubject, Subject } from 'rxjs';
import { distinctUntilChanged, first, switchMap } from 'rxjs/operators';
import { IconDefinition } from '@fortawesome/fontawesome-svg-core';
import { faEllipsisH } from '@fortawesome/free-solid-svg-icons';

/** A context menu item represents a button in the context menu */
export interface ContextMenuItem {
  readonly click: () => void;
  readonly hasPermission?: () => Observable<boolean>;
  readonly holdTime?: number;
  readonly icon?: IconDefinition;
  readonly iconModifier?: string;
  readonly title: string;
}

/** Each group of context menu items is separated by a divider */
export type ContextMenuItems = ContextMenuItem[][];

@Component({
  selector: 'models4insight-context-menu',
  templateUrl: 'context-menu.component.html',
  styleUrls: ['context-menu.component.scss'],
})
export class ContextMenuComponent implements OnInit, OnDestroy {
  private readonly menuItems$: Subject<ContextMenuItems> =
    new BehaviorSubject<ContextMenuItems>([]);

  readonly filteredMenuItems$: Subject<ContextMenuItems> =
    new ReplaySubject<ContextMenuItems>();

  faEllipsisH = faEllipsisH;

  ngOnInit() {
    // Whenever the menu items are updated, filter out the ones the user does not have permission for
    this.menuItems$
      .pipe(
        distinctUntilChanged(),
        switchMap((menuItems) => this.filterMenuItems(menuItems)),
        untilDestroyed(this)
      )
      .subscribe(this.filteredMenuItems$);
  }

  ngOnDestroy() {}

  onHeld(event: boolean, item: ContextMenuItem) {
    if (event) {
      item.click();
    }
  }

  trackByIndex(index: number) {
    return index;
  }

  private async filterMenuItems(menuItems: ContextMenuItems) {
    const allowedMenuItems = await Promise.all(
      menuItems.map(async (group) => {
        // Determine for every menu item whether or not it is currently permitted
        const hasPermission = await Promise.all(
          group.map(async (menuItem) =>
            menuItem.hasPermission
              ? menuItem.hasPermission().pipe(first()).toPromise()
              : Promise.resolve(true)
          )
        );
        // Filter the list of menu items based on whether or not the item is permitted
        return group.filter((menuItem, index) => hasPermission[index]);
      })
    );
    return allowedMenuItems.filter((group) => group.length > 0);
  }

  @Input() set menuItems(menuItems: ContextMenuItems) {
    this.menuItems$.next(menuItems);
  }
}
