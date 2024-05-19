import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { CollectionDetailsComponent } from './collection-details.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Collection/CollectionDetailsComponent',
  component: CollectionDetailsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<CollectionDetailsComponent>;

const Template: StoryFn<CollectionDetailsComponent> = (args: CollectionDetailsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
