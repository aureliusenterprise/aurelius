import { Meta, moduleMetadata, Story } from '@storybook/angular';
import { isEqual } from 'lodash';
import { SelectComponent } from './select.component';

export default {
  title: 'Libs/Components/SelectComponent',
  component: SelectComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<SelectComponent>;

const Template: Story<SelectComponent> = (args: SelectComponent) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {
  comparator: isEqual,
  data: [],
  isDisabled: false,
};
