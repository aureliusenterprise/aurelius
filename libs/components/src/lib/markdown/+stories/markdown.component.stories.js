import { moduleMetadata } from '@storybook/angular';
import { MarkdownComponent } from '../markdown.component';
import { MarkdownModule } from '../markdown.module';
import { markdown } from './content';

export default {
  title: 'Libs/Components/Markdown',

  decorators: [
    moduleMetadata({
      imports: [MarkdownModule],
    }),
  ],

  argTypes: {
    markdown: {
      control: 'text',
    },
  },
};

export const Primary = {
  render: () => ({
    component: MarkdownComponent,

    props: {
      markdown,
    },
  }),

  name: 'Primary',
  height: '500px',

  args: {
    markdown,
  },
};
