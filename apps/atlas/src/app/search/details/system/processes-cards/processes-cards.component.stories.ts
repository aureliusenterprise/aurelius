import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { ProcessesCardsComponent } from './processes-cards.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/System/ProcessesCardsComponent',
  component: ProcessesCardsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<ProcessesCardsComponent>;

const Template: Story<ProcessesCardsComponent> = (args: ProcessesCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}