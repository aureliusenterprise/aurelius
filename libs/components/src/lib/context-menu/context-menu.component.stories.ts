import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { ContextMenuComponent } from './context-menu.component';

export default {
  title: 'Libs/Components/ContextMenuComponent',
  component: ContextMenuComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<ContextMenuComponent>;

const Template: Story<ContextMenuComponent> = (args: ContextMenuComponent) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {
  menuItems: '',
};
