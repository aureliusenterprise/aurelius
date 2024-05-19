import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { FieldsCardsComponent } from './fields-cards.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Attribute/FieldsCardsComponent',
  component: FieldsCardsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<FieldsCardsComponent>;

const Template: StoryFn<FieldsCardsComponent> = (args: FieldsCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
