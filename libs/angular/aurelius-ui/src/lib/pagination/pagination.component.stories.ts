import type { Meta, StoryObj } from "@storybook/angular";
import { Pagination } from "./pagination.component";

const meta: Meta<Pagination> = {
    component: Pagination,
    title: "Pagination",
};

export default meta;

type Story = StoryObj<Pagination>;

export const Primary: Story = {
    args: {
        pageIndex: 0,
        pageSize: 4,
        totalItems: 20,
    },
    render: (args) => ({
        props: args,
    }),
};

export const SecondPage: Story = {
    args: {
        pageIndex: 1,
        pageSize: 4,
        totalItems: 20,
    },
    render: (args) => ({
        props: args,
    }),
};

export const LastPage: Story = {
    args: {
        pageIndex: 4,
        pageSize: 4,
        totalItems: 20,
    },
    render: (args) => ({
        props: args,
    }),
};

export const LongForm: Story = {
    args: {
        pageIndex: 12,
        pageSize: 4,
        totalItems: 100,
    },
    render: (args) => ({
        props: args,
    }),
};

export const Empty: Story = {
    args: {
        pageIndex: 0,
        pageSize: 4,
        totalItems: 0,
    },
    render: (args) => ({
        props: args,
    }),
};
