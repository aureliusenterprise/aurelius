import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { BreadCrumbsComponent } from './bread-crumbs.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/BreadCrumbsComponent',
  component: BreadCrumbsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<BreadCrumbsComponent>;

const Template: StoryFn<BreadCrumbsComponent> = (args: BreadCrumbsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
    activeGuid:  '',
    showLast:  true,
}
