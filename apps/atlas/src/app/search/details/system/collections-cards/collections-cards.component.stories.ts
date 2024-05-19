import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { CollectionsCardsComponent } from './collections-cards.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/System/CollectionsCardsComponent',
  component: CollectionsCardsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<CollectionsCardsComponent>;

const Template: StoryFn<CollectionsCardsComponent> = (args: CollectionsCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
