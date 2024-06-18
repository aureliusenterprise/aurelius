import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { CreateProjectModalComponent } from './create-project-modal.component';

export default {
  title: 'Libs/Components/CreateProjectModalComponent',
  component: CreateProjectModalComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<CreateProjectModalComponent>;

const Template: Story<CreateProjectModalComponent> = (
  args: CreateProjectModalComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {};
