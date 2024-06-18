import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { AddBranchMemberComponent } from './add-branch-member.component';

export default {
  title: 'Libs/Components/AddBranchMemberComponent',
  component: AddBranchMemberComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<AddBranchMemberComponent>;

const Template: Story<AddBranchMemberComponent> = (
  args: AddBranchMemberComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {};
