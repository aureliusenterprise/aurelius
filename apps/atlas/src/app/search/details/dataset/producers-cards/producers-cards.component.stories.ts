import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { ProducersCardsComponent } from './producers-cards.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Dataset/ProducersCardsComponent',
  component: ProducersCardsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<ProducersCardsComponent>;

const Template: StoryFn<ProducersCardsComponent> = (args: ProducersCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
