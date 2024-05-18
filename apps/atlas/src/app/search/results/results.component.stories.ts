import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { ResultsComponent } from './results.component';

export default {
  title: 'Apps/Atlas/Components/Search/Results/ResultsComponent',
  component: ResultsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<ResultsComponent>;

const Template: Story<ResultsComponent> = (args: ResultsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}