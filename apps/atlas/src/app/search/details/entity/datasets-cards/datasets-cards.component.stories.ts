import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { DatasetsCardsComponent } from './datasets-cards.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Entity/DatasetsCardsComponent',
  component: DatasetsCardsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<DatasetsCardsComponent>;

const Template: StoryFn<DatasetsCardsComponent> = (args: DatasetsCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
