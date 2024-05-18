import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { FilterComponent } from './filter.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Filter/FilterComponent',
  component: FilterComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<FilterComponent>;

const Template: Story<FilterComponent> = (args: FilterComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}