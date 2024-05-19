import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { GovernanceQualityCardsComponent } from './governance-quality-cards.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Components/GovernanceQualityCardsComponent',
  component: GovernanceQualityCardsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<GovernanceQualityCardsComponent>;

const Template: StoryFn<GovernanceQualityCardsComponent> = (args: GovernanceQualityCardsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
