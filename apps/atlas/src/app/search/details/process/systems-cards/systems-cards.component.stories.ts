import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { SystemsCardsComponent } from './systems-cards.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Process/SystemsCardsComponent',
  component: SystemsCardsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<SystemsCardsComponent>;

const Template: Story<SystemsCardsComponent> = (args: SystemsCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}