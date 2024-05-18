import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { GovQualityDetailsComponent } from './gov-quality-details.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Governance Quality/GovQualityDetailsComponent',
  component: GovQualityDetailsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<GovQualityDetailsComponent>;

const Template: Story<GovQualityDetailsComponent> = (args: GovQualityDetailsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}