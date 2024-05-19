import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
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

const Template: StoryFn<NonCompliantCardsComponent> = (args: NonCompliantCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
