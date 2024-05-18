import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { CompliantCardsComponent } from './compliant-cards.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Governance Quality/CompliantCardsComponent',
  component: CompliantCardsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<CompliantCardsComponent>;

const Template: Story<CompliantCardsComponent> = (args: CompliantCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}