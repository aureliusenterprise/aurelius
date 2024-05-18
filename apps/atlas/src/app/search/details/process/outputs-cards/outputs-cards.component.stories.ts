import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { OutputsCardsComponent } from './outputs-cards.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Process/OutputsCardsComponent',
  component: OutputsCardsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<OutputsCardsComponent>;

const Template: Story<OutputsCardsComponent> = (args: OutputsCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}