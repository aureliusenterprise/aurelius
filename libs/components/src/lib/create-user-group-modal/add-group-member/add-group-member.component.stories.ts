import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { AddGroupMemberComponent } from './add-group-member.component';

export default {
  title: 'Libs/Components/AddGroupMemberComponent',
  component: AddGroupMemberComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<AddGroupMemberComponent>;

const Template: Story<AddGroupMemberComponent> = (
  args: AddGroupMemberComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {};
