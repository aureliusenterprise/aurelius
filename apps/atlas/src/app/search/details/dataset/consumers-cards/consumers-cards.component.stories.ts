import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { ConsumersCardsComponent } from './consumers-cards.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Dataset/ConsumersCardsComponent',
  component: ConsumersCardsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<ConsumersCardsComponent>;

const Template: StoryFn<ConsumersCardsComponent> = (args: ConsumersCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
