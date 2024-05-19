import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { ClassificationComponent } from './classification.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/ClassificationComponent',
  component: ClassificationComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<ClassificationComponent>;

const Template: StoryFn<ClassificationComponent> = (args: ClassificationComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
    classificationName:  '',
    sources:  '',
}
