import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { BranchMembersComponent } from './branch-members.component';

export default {
  title: 'Libs/Components/BranchMembersComponent',
  component: BranchMembersComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<BranchMembersComponent>;

const Template: Story<BranchMembersComponent> = (
  args: BranchMembersComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {};
