import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { EntityCardsComponent } from './entity-cards.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Domain/EntityCardsComponent',
  component: EntityCardsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<EntityCardsComponent>;

const Template: Story<EntityCardsComponent> = (args: EntityCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}