import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { GovernanceQualityEditorComponent } from './gov-quality-editor.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Editor/GovernanceQualityEditorComponent',
  component: GovernanceQualityEditorComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<GovernanceQualityEditorComponent>;

const Template: StoryFn<GovernanceQualityEditorComponent> = (args: GovernanceQualityEditorComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
