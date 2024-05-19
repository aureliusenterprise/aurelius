import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { GovernanceResponsibilitiesInfoModalComponent } from './governance-responsibilities-info-modal.component';

export default {
  title: 'Apps/Atlas/Components/Search/Browse/Governance/GovernanceResponsibilitiesInfoModalComponent',
  component: GovernanceResponsibilitiesInfoModalComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<GovernanceResponsibilitiesInfoModalComponent>;

const Template: StoryFn<GovernanceResponsibilitiesInfoModalComponent> = (args: GovernanceResponsibilitiesInfoModalComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
