import { Meta, moduleMetadata, Story } from '@storybook/angular';
import {
  ControlShellComponent,
  defaultControlShellContext,
} from './control-shell.component';

export default {
  title: 'Libs/Components/ControlShellComponent',
  component: ControlShellComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<ControlShellComponent>;

const Template: Story<ControlShellComponent> = (
  args: ControlShellComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {
  context: defaultControlShellContext,
  isSubmitted: false,
};
