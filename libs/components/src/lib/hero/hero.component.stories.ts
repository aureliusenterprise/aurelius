import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { HeroComponent } from './hero.component';

export default {
  title: 'Libs/Components/HeroComponent',
  component: HeroComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<HeroComponent>;

const Template: Story<HeroComponent> = (args: HeroComponent) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {
  subtitle: '',
  title: '',
};
