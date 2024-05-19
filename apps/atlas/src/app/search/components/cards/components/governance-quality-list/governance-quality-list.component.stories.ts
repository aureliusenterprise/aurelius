import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { GovernanceQualityListComponent } from './governance-quality-list.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Cards/GovernanceQualityListComponent',
  component: GovernanceQualityListComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<GovernanceQualityListComponent>;

const Template: StoryFn<GovernanceQualityListComponent> = (args: GovernanceQualityListComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
