import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { PermissionSelectComponent } from './permission-select.component';

export default {
  title: 'Libs/Components/PermissionSelectComponent',
  component: PermissionSelectComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<PermissionSelectComponent>;

const Template: Story<PermissionSelectComponent> = (
  args: PermissionSelectComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {
  user: '',
};
