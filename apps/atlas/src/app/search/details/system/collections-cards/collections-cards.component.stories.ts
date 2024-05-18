import { moduleMetadata, Story, Meta } from '@storybook/angular';
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

const Template: Story<CollectionsCardsComponent> = (args: CollectionsCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}