import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { AttributeEditorComponent } from './attribute-editor.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Editor/AttributeEditorComponent',
  component: AttributeEditorComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<AttributeEditorComponent>;

const Template: Story<AttributeEditorComponent> = (args: AttributeEditorComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}