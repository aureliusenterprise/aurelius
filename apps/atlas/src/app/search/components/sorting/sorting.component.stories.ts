import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { SortingComponent } from './sorting.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Filter/SortingComponent',
  component: SortingComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<SortingComponent>;

const Template: Story<SortingComponent> = (args: SortingComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
    sortingOptions:  [],
}