import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { FieldEditorComponent } from './field-editor.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Editor/FieldEditorComponent',
  component: FieldEditorComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<FieldEditorComponent>;

const Template: Story<FieldEditorComponent> = (args: FieldEditorComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}