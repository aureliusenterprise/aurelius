import { Meta, moduleMetadata, Story } from '@storybook/angular';
import { isEqual } from 'lodash';
import { SearchModalComponent } from './search-modal.component';

export default {
  title: 'Libs/Components/SearchModalComponent',
  component: SearchModalComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<SearchModalComponent<unknown>>;

const Template: Story<SearchModalComponent<unknown>> = (
  args: SearchModalComponent<unknown>
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {
  isTimestamp: false,
  rowComparator: isEqual,
  data: [],
  displayField: '',
};
