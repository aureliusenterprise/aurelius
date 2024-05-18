import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { GovQualityDisplayComponent } from './gov-quality-display.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Editor/Components/GovQualityDisplayComponent',
  component: GovQualityDisplayComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<GovQualityDisplayComponent>;

const Template: Story<GovQualityDisplayComponent> = (args: GovQualityDisplayComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}