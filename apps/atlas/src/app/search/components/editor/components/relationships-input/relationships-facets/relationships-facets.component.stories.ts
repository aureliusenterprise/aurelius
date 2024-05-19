import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { RelationshipsFacetsComponent } from './relationships-facets.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Editor/Components/RelationshipsFacetsComponent',
  component: RelationshipsFacetsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<RelationshipsFacetsComponent>;

const Template: StoryFn<RelationshipsFacetsComponent> = (args: RelationshipsFacetsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
