import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { RelationshipOptionComponent } from './relationship-option.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Editor/Components/RelationshipOptionComponent',
  component: RelationshipOptionComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<RelationshipOptionComponent>;

const Template: Story<RelationshipOptionComponent> = (args: RelationshipOptionComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
    searchResult:  '',
}