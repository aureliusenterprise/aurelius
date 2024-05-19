import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { DetailsNavigationComponent } from './details-navigation.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Components/DetailsNavigationComponent',
  component: DetailsNavigationComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<DetailsNavigationComponent>;

const Template: StoryFn<DetailsNavigationComponent> = (args: DetailsNavigationComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
