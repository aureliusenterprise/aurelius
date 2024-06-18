import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { CommitButtonComponent } from './commit-button.component';

export default {
  title: 'Libs/Components/CommitButtonComponent',
  component: CommitButtonComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<CommitButtonComponent>;

const Template: Story<CommitButtonComponent> = (
  args: CommitButtonComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {};
