import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { EntitiesCardsComponent } from './entities-cards.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Entity/EntitiesCardsComponent',
  component: EntitiesCardsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<EntitiesCardsComponent>;

const Template: Story<EntitiesCardsComponent> = (args: EntitiesCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}