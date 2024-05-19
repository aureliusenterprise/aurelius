import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { ClassificationsInputComponent } from './classifications-input.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Editor/Components/ClassificationsInputComponent',
  component: ClassificationsInputComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<ClassificationsInputComponent>;

const Template: StoryFn<ClassificationsInputComponent> = (args: ClassificationsInputComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
