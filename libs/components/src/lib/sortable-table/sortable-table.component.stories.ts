import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { SortableTableComponent } from './sortable-table.component';

export default {
  title: 'Libs/Components/SortableTableComponent',
  component: SortableTableComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<SortableTableComponent>;

const Template: Story<SortableTableComponent> = (
  args: SortableTableComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {};
