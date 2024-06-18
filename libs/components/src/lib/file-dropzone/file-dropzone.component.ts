import { Component, OnInit } from '@angular/core';
import { faUpload } from '@fortawesome/free-solid-svg-icons';
import {
  AbstractControlShell,
  ControlShellContext,
  defaultControlShellContext,
} from '../control-shell';

export interface FileDropzoneContext extends ControlShellContext {
  readonly title: string;
}

export const defaultFileDropzoneContext: FileDropzoneContext = {
  ...defaultControlShellContext,
  requiredErrorMessage: 'Please select a file to upload',
  title: 'File Upload',
};

@Component({
  selector: 'models4insight-file-dropzone',
  templateUrl: 'file-dropzone.component.html',
  styleUrls: ['file-dropzone.component.scss'],
})
export class FileDropzoneComponent
  extends AbstractControlShell
  implements OnInit
{
  faUpload = faUpload;

  // State for dropzone CSS toggling
  isHovering: boolean;

  ngOnInit() {
    if (this.context === defaultControlShellContext) {
      this.context = defaultFileDropzoneContext;
    }
  }

  toggleHover(event: boolean) {
    this.isHovering = event;
  }

  onFileChange(event: FileList) {
    if (event && event.length) {
      this.control.markAsTouched();
      const file = event.item(0);
      this.control.patchValue(file);
      this.control.markAsDirty();
    }
  }

  get currentFileName() {
    return this.control.value ? this.control.value.name : '';
  }
}
