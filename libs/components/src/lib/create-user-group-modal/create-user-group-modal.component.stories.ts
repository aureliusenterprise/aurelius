import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { CreateUserGroupModalComponent } from './create-user-group-modal.component';

export default {
  title: 'Libs/Components/CreateUserGroupModalComponent',
  component: CreateUserGroupModalComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<CreateUserGroupModalComponent>;

const Template: Story<CreateUserGroupModalComponent> = (
  args: CreateUserGroupModalComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {};
