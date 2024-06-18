import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { DatePickerComponent } from './date-picker.component';

export default {
  title: 'Libs/Components/DatePickerComponent',
  component: DatePickerComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<DatePickerComponent>;

const Template: Story<DatePickerComponent> = (args: DatePickerComponent) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {
  date: '',
};
