import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { FieldsCardsComponent } from './fields-cards.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Dataset/FieldsCardsComponent',
  component: FieldsCardsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<FieldsCardsComponent>;

const Template: Story<FieldsCardsComponent> = (args: FieldsCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}