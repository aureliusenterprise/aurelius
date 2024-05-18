import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { GovernanceRolesCardsComponent } from './governance-roles-cards.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Person/GovernanceRolesCardsComponent',
  component: GovernanceRolesCardsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<GovernanceRolesCardsComponent>;

const Template: Story<GovernanceRolesCardsComponent> = (args: GovernanceRolesCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}