import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { RelationshipsInputComponent } from './relationships-input.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Editor/Components/RelationshipsInputComponent',
  component: RelationshipsInputComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<RelationshipsInputComponent>;

const Template: Story<RelationshipsInputComponent> = (args: RelationshipsInputComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
    relationshipTypeName:  '',
    typeName:  '',
}