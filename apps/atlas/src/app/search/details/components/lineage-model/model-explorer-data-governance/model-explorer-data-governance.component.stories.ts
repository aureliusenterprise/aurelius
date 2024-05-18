import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { ModelExplorerDataGovernanceComponent } from './model-explorer-data-governance.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Components/ModelExplorerDataGovernanceComponent',
  component: ModelExplorerDataGovernanceComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<ModelExplorerDataGovernanceComponent>;

const Template: Story<ModelExplorerDataGovernanceComponent> = (args: ModelExplorerDataGovernanceComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}