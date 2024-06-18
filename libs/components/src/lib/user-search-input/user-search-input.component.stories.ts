import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { UserSearchInputComponent } from './user-search-input.component';

export default {
  title: 'Libs/Components/UserSearchInputComponent',
  component: UserSearchInputComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<UserSearchInputComponent>;

const Template: Story<UserSearchInputComponent> = (
  args: UserSearchInputComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {};
