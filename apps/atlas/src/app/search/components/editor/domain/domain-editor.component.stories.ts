import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { DomainEditorComponent } from './domain-editor.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Editor/DomainEditorComponent',
  component: DomainEditorComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<DomainEditorComponent>;

const Template: Story<DomainEditorComponent> = (args: DomainEditorComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}