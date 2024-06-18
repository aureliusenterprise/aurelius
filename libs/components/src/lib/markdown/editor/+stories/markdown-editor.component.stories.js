import { moduleMetadata } from '@storybook/angular';
import { MarkdownEditorComponent } from '../markdown-editor.component';
import { MarkdownEditorModule } from '../markdown-editor.module';

export default {
  title: 'Libs/Components/Markdown Editor',

  decorators: [
    moduleMetadata({
      imports: [MarkdownEditorModule],
    }),
  ],
};

export const Primary = {
  render: () => ({
    component: MarkdownEditorComponent,
  }),

  name: 'Primary',
  height: '500px',
};
