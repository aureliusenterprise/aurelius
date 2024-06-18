import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { CommitOptionsModalComponent } from './commit-options-modal.component';

export default {
  title: 'Libs/Components/CommitOptionsModalComponent',
  component: CommitOptionsModalComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<CommitOptionsModalComponent>;

const Template: Story<CommitOptionsModalComponent> = (
  args: CommitOptionsModalComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {};
