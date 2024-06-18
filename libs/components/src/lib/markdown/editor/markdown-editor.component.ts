import { Component, Input } from '@angular/core';
import { FormControl } from '@angular/forms';

@Component({
  selector: 'models4insight-markdown-editor',
  templateUrl: 'markdown-editor.component.html',
  styleUrls: ['markdown-editor.component.scss'],
})
export class MarkdownEditorComponent {
  /**
   * The control that maintains the state of the text area
   */
  protected readonly control: FormControl<string>;

  constructor() {
    this.control = new FormControl<string>(null);
  }

  /**
   * The markdown content
   */
  @Input() set markdown(markdown: string) {
    this.control.setValue(markdown);
  }

  get markdown() {
    return this.control.value;
  }
}
