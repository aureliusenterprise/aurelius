import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { ClassificationSourceComponent } from './classification-source.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/ClassificationSourceComponent',
  component: ClassificationSourceComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<ClassificationSourceComponent>;

const Template: StoryFn<ClassificationSourceComponent> = (args: ClassificationSourceComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
    source:  '',
}
