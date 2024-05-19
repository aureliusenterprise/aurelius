import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { DetailsCardsListComponent } from './details-cards-list.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Components/DetailsCardsListComponent',
  component: DetailsCardsListComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<DetailsCardsListComponent>;

const Template: StoryFn<DetailsCardsListComponent> = (args: DetailsCardsListComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
    enableDescendantsControl:  true,
    sortingOptions:  [],
    title:  '',
    defaultFilters:  '',
    defaultSorting:  '',
}
