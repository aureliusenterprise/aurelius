import { Meta, moduleMetadata, Story } from '@storybook/angular';
import { isEqual } from 'lodash';
import { SortableTableShellComponent } from './sortable-table-shell.component';

export default {
  title: 'Libs/Components/SortableTableShellComponent',
  component: SortableTableShellComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<SortableTableShellComponent>;

const Template: Story<SortableTableShellComponent> = (
  args: SortableTableShellComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {
  config: {},
  enableTableContainer: true,
  itemsPerPage: 10,
  rowComparator: isEqual,
  rowsSelectable: true,
  showHeaderRow: true,
  totalItems: 0,
  data: [],
};
