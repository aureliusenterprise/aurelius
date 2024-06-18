import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { GroupMembersComponent } from './group-members.component';

export default {
  title: 'Libs/Components/GroupMembersComponent',
  component: GroupMembersComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<GroupMembersComponent>;

const Template: Story<GroupMembersComponent> = (
  args: GroupMembersComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {};
