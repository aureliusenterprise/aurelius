import { Directive, EventEmitter, HostListener, Output } from '@angular/core';

@Directive({
  exportAs: 'models4insight-dropzone',
  selector: 'models4insight-dropzone, [models4insight-dropzone]',
})
export class DropzoneDirective {
  @Output() dropped = new EventEmitter<FileList>();
  @Output() hovered = new EventEmitter<boolean>();

  constructor() {}

  @HostListener('dragenter', ['$event'])
  onDragEnter($event: any) {
    $event.preventDefault();
    $event.dataTransfer.effectAllowed = 'none';
    $event.dataTransfer.dropEffect = 'none';
  }

  @HostListener('dragleave', ['$event'])
  onDragLeave($event: any) {
    $event.preventDefault();
    $event.dataTransfer.effectAllowed = 'none';
    $event.dataTransfer.dropEffect = 'none';
    this.hovered.emit(false);
  }

  @HostListener('dragover', ['$event'])
  onDragOver($event: any) {
    $event.preventDefault();
    this.hovered.emit(true);
  }

  @HostListener('drop', ['$event'])
  onDrop($event: any) {
    $event.preventDefault();
    $event.dataTransfer.effectAllowed = 'none';
    $event.dataTransfer.dropEffect = 'none';
    this.dropped.emit($event.dataTransfer.files);
    this.hovered.emit(false);
  }
}
