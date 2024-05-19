import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { AttributesCardsComponent } from './attributes-cards.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Entity/AttributesCardsComponent',
  component: AttributesCardsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<AttributesCardsComponent>;

const Template: StoryFn<AttributesCardsComponent> = (args: AttributesCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
