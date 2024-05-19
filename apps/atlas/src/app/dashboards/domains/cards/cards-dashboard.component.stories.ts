import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { CardDashboardComponent } from './cards-dashboard.component';

export default {
  title: 'Apps/Atlas/Components/Dashboards/Domains/CardDashboardComponent',
  component: CardDashboardComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<CardDashboardComponent>;

const Template: StoryFn<CardDashboardComponent> = (args: CardDashboardComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
