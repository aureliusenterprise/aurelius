import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { PersonEditorComponent } from './person-editor.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Editor/PersonEditorComponent',
  component: PersonEditorComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<PersonEditorComponent>;

const Template: StoryFn<PersonEditorComponent> = (args: PersonEditorComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
