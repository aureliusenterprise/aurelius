import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { QuickviewComponent } from './quickview.component';

export default {
  title: 'Libs/Components/QuickviewComponent',
  component: QuickviewComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<QuickviewComponent>;

const Template: Story<QuickviewComponent> = (args: QuickviewComponent) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {
  isPinned: false,
  name: 'Details',
};
