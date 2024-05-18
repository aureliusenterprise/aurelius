import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { AttributesCardsComponent } from './attributes-cards.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Field/AttributesCardsComponent',
  component: AttributesCardsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<AttributesCardsComponent>;

const Template: Story<AttributesCardsComponent> = (args: AttributesCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}