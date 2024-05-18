import { Component, EventEmitter, Input, Output } from '@angular/core';
import { faCheck, faTimes } from '@fortawesome/free-solid-svg-icons';
import { Conflict, ConflictChangeTypeEnum, ConflictSide, ConflictTypeEnum } from '@models4insight/repository';
import { ConflictSetContext } from '@models4insight/services/model';
import { SaveContext } from '../../conflict-resolution.service';

@Component({
  selector: 'models4insight-conflict-details',
  templateUrl: 'conflict-details.component.html',
  styleUrls: ['conflict-details.component.scss']
})
export class ConflictDetailsComponent {
  @Input() conflict: Conflict;
  @Input() context: ConflictSetContext;
  @Output() save: EventEmitter<SaveContext> = new EventEmitter<SaveContext>();

  readonly ConflictTypeEnum = ConflictTypeEnum;

  faCheck = faCheck;
  faTimes = faTimes;

  saveSide(side: ConflictSide) {
    if (side !== undefined) {
      if (side.source === 'left') {
        this.save.emit({
          conflict: this.conflict,
          operation:
            this.conflict.leftChange === ConflictChangeTypeEnum.DELETED
              ? 'delete'
              : 'add',
          side: side
        });
      } else {
        this.save.emit({
          conflict: this.conflict,
          operation:
            this.conflict.rightChange === ConflictChangeTypeEnum.DELETED
              ? 'delete'
              : 'add',
          side: side
        });
      }
    }
    // If the saved side is undefined, delete the other side
    else {
      this.save.emit({
        conflict: this.conflict,
        operation: 'delete',
        side: this.conflict.left || this.conflict.right
      });
    }
  }
}
