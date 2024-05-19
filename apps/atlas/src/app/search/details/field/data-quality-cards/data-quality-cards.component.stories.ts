import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { DataQualityCardsComponent } from './data-quality-cards.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Field/DataQualityCardsComponent',
  component: DataQualityCardsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<DataQualityCardsComponent>;

const Template: StoryFn<DataQualityCardsComponent> = (args: DataQualityCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
