import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { ContextMenuItemComponent } from './context-menu-item.component';

export default {
  title: 'Libs/Components/ContextMenuItemComponent',
  component: ContextMenuItemComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<ContextMenuItemComponent>;

const Template: Story<ContextMenuItemComponent> = (
  args: ContextMenuItemComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {};
