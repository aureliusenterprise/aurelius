import { NestedTreeControl } from '@angular/cdk/tree';
import {
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
  ViewEncapsulation,
} from '@angular/core';
import { MatTreeNestedDataSource } from '@angular/material/tree';
import {
  faChevronDown,
  faChevronRight,
} from '@fortawesome/free-solid-svg-icons';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { shareReplay, switchMap } from 'rxjs/operators';
import { BaseComponent } from '../base-component';
import { PathIndex, TreeLevel, TreeService } from './tree.service';

@Component({
  selector: 'models4insight-tree',
  templateUrl: 'tree.component.html',
  styleUrls: ['tree.component.scss'],
  providers: [TreeService],
  encapsulation: ViewEncapsulation.None,
})
export class TreeComponent extends BaseComponent implements OnInit {
  @Output() readonly nodeActivated = new EventEmitter<string>();

  readonly treeControl = new NestedTreeControl<TreeLevel>(
    (node) => node.children
  );

  readonly faChevronDown = faChevronDown;
  readonly faChevronRight = faChevronRight;

  activeNode$: Observable<string>;

  dataSource: MatTreeNestedDataSource<TreeLevel>;

  constructor(private readonly treeService: TreeService) {
    super();
  }

  ngOnInit() {
    this.activeNode$ = this.treeService
      .select('activeNode')
      .pipe(shareReplay());

    this.activeNode$
      .pipe(
        switchMap((id) => this.handleOpenActivatedTreeNode(id)),
        untilDestroyed(this)
      )
      .subscribe();

    this.activeNode$.pipe(untilDestroyed(this)).subscribe(this.nodeActivated);

    this.treeService
      .select('tree')
      .pipe(untilDestroyed(this))
      .subscribe((tree) => {
        // There exists a memory leak in the data source object.
        // Assign null to any existing data source, and overwrite it with a new datasource instance.
        if (this.dataSource) {
          this.dataSource.data = null;
        }
        this.dataSource = new MatTreeNestedDataSource<TreeLevel>();
        this.dataSource.data = tree;
      });
  }

  hasChild(_: number, node: TreeLevel) {
    return !!node.children && node.children.length > 0;
  }

  @Input() set activeNode(id: string) {
    this.treeService.update({
      description: 'Active node updated',
      payload: { activeNode: id },
    });
  }

  @Input() set pathIndex(pathIndex: PathIndex) {
    this.treeService.update({
      description: 'New tree available',
      payload: { pathIndex },
    });
  }

  get isBuildingTree(): Observable<boolean> {
    return this.treeService.select('isBuildingTree');
  }

  private async handleOpenActivatedTreeNode(id: string) {
    const nodesById = await this.treeService.get('nodesById');

    this.treeControl.collapseAll();

    let currentNode = nodesById[id];

    while (currentNode) {
      this.treeControl.expand(currentNode);
      currentNode = nodesById[currentNode.parent];
    }
  }
}
