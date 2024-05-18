import { Component, OnInit, ViewChild } from '@angular/core';
import { UntypedFormBuilder, UntypedFormGroup } from '@angular/forms';
import {
  FileDropzone,
  FileDropzoneComponent,
  FileDropzoneContext
} from '@models4insight/components';
import { Observable } from 'rxjs';
import { FileUploadService } from './file-upload.service';

const fileDropzoneContext: FileDropzoneContext = {
  title: 'Your data goes here'
};

@Component({
  selector: 'models4insight-file-upload',
  templateUrl: 'file-upload.component.html',
  styleUrls: ['file-upload.component.scss']
})
export class FileUploadComponent implements OnInit {
  isParsingFile$: Observable<boolean>;

  fileUploadForm: UntypedFormGroup;
  isSubmitted: boolean;

  @ViewChild(FileDropzoneComponent, { static: true })
  private readonly dropzone: FileDropzoneComponent;

  constructor(
    private fileUploadService: FileUploadService,
    private formBuilder: UntypedFormBuilder
  ) {
    this.createForm();
  }

  ngOnInit() {
    this.isParsingFile$ = this.fileUploadService.select('isParsingFile');
    this.dropzone.context = fileDropzoneContext;
  }

  submitCurrentFile() {
    this.fileUploadForm.updateValueAndValidity();
    this.isSubmitted = true;
    if (this.fileUploadForm.valid) {
      const { file } = this.fileUploadForm.value;
      this.fileUploadService.submitFile(file);
      this.isSubmitted = false;
    }
  }

  private createForm() {
    this.fileUploadForm = this.formBuilder.group({
      file: new FileDropzone(['csv', 'json', 'xls', 'xlsx'])
    });
  }
}
