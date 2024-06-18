import {
  Directive,
  EventEmitter,
  HostListener,
  Input,
  Output,
} from '@angular/core';
import { copyToClipboard } from '@models4insight/utils';

@Directive({
  exportAs: 'models4insight-copy',
  selector: 'models4insight-copy, [models4insight-copy]',
})
export class CopyDirective {
  @Input('models4insight-copy') value: string;

  @Output() valueCopied: EventEmitter<void> = new EventEmitter<void>();

  @HostListener('click')
  async onHostElementClicked() {
    await copyToClipboard(this.value);
    this.valueCopied.next();
  }
}
