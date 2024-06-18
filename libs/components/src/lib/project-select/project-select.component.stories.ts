import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { ProjectSelectComponent } from './project-select.component';

export default {
  title: 'Libs/Components/ProjectSelectComponent',
  component: ProjectSelectComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<ProjectSelectComponent>;

const Template: Story<ProjectSelectComponent> = (
  args: ProjectSelectComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {};
