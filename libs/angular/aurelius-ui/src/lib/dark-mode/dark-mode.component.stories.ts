import type { Meta, StoryObj } from "@storybook/angular";
import { DarkMode } from "./dark-mode.component";

const meta: Meta<DarkMode> = {
    component: DarkMode,
    title: "Dark Mode",
};
export default meta;

type Story = StoryObj<DarkMode>;

export const Primary: Story = {};
