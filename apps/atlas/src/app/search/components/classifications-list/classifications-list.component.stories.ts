import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { ClassificationsListComponent } from './classifications-list.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/ClassificationsListComponent',
  component: ClassificationsListComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<ClassificationsListComponent>;

const Template: StoryFn<ClassificationsListComponent> = (args: ClassificationsListComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
