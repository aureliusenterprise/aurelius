import { Meta, moduleMetadata, Story } from '@storybook/angular';
import { ColorSquareComponent } from './color-square.component';
import { ColorSquareModule } from './color-square.module';

export default {
  title: 'Libs/Components/ColorSquareComponent',
  component: ColorSquareComponent,
  decorators: [
    moduleMetadata({
      imports: [ColorSquareModule],
    }),
  ],
  argTypes: {
    color: { control: 'text' },
    enableColorPicker: { control: 'boolean' },
    position: {
      control: 'select',
      options: ['bottom-left', 'bottom-right', 'top-left', 'top-right'],
    },
  },
} as Meta<ColorSquareComponent>;

const Template: Story<ColorSquareComponent> = (args: ColorSquareComponent) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {
  enableColorPicker: true,
  color: '#FFFFFF',
  position: 'bottom-right',
};
