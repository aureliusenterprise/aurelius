import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { InputsCardsComponent } from './inputs-cards.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Process/InputsCardsComponent',
  component: InputsCardsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<InputsCardsComponent>;

const Template: StoryFn<InputsCardsComponent> = (args: InputsCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
