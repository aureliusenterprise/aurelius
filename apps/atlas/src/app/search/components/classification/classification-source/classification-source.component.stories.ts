import { moduleMetadata, Story, Meta } from '@storybook/angular';
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

const Template: Story<ClassificationSourceComponent> = (args: ClassificationSourceComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
    source:  '',
}