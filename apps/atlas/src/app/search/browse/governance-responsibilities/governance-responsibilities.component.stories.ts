import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { GovernanceResponsibilitiesComponent } from './governance-responsibilities.component';

export default {
  title: 'Apps/Atlas/Components/Search/Browse/Governance/GovernanceResponsibilitiesComponent',
  component: GovernanceResponsibilitiesComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<GovernanceResponsibilitiesComponent>;

const Template: Story<GovernanceResponsibilitiesComponent> = (args: GovernanceResponsibilitiesComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}