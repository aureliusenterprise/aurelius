import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { UserSearchModalComponent } from './user-search-modal.component';

export default {
  title: 'Libs/Components/UserSearchModalComponent',
  component: UserSearchModalComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<UserSearchModalComponent>;

const Template: Story<UserSearchModalComponent> = (
  args: UserSearchModalComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {
  currentUsers: [],
};
