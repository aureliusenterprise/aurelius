import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { NonCompliantCardsComponent } from './non-compliant-cards.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Governance Quality/NonCompliantCardsComponent',
  component: NonCompliantCardsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<NonCompliantCardsComponent>;

const Template: Story<NonCompliantCardsComponent> = (args: NonCompliantCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}