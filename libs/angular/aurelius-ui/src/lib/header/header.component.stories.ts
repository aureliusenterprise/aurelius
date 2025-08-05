import type { Meta, StoryObj } from "@storybook/angular";
import { expect } from "storybook/test";
import { Header } from "./header.component";

const meta: Meta<Header> = {
    component: Header,
    title: "Header",
};
export default meta;

type Story = StoryObj<Header>;

const template = `
<aurelius-ui-header [expanded]="expanded" [logo]="logo" [name]="name">
    <ng-container navbar-start>
        <a class="navbar-item" routerLink="/">Home</a>
        <a class="navbar-item" routerLink="/about">About</a>
    </ng-container>
    <ng-container navbar-end>
        <div class="navbar-item">
            <div class="buttons">
                <a class="button is-primary">Log in</a>
            </div>
        </div>
    </ng-container>
</aurelius-ui-header>
`;

export const Primary: Story = {
    args: {
        expanded: false,
        logo: "assets/favicon.ico",
        name: "Aurelius UI",
    },
    play: async ({ canvas }) => {
        await expect(canvas.getByText(/Home/gi)).toBeTruthy();
        await expect(canvas.getByText(/About/gi)).toBeTruthy();
        await expect(canvas.getByText(/Log in/gi)).toBeTruthy();
    },
    render: (args) => ({
        props: args,
        template,
    }),
};

export const Expanded: Story = {
    args: {
        expanded: true,
        logo: "assets/favicon.ico",
        name: "Aurelius UI",
    },
    play: async ({ canvas }) => {
        await expect(canvas.getByText(/Home/gi)).toBeTruthy();
        await expect(canvas.getByText(/About/gi)).toBeTruthy();
        await expect(canvas.getByText(/Log in/gi)).toBeTruthy();
    },
    render: (args) => ({
        props: args,
        template,
    }),
};

export const Empty: Story = {
    args: {
        expanded: false,
        logo: "assets/favicon.ico",
        name: "Aurelius UI",
    },
};
