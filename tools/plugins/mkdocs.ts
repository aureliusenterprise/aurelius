import { CreateNodes, CreateNodesResult } from '@nx/devkit';
import { dirname } from 'path';

export interface MkDocsPluginOptions {
    readonly docsTargetName?: string;
}

const glob = 'mkdocs.yaml';

export const createNodes: CreateNodes<MkDocsPluginOptions> = [
    glob,
    async (configFilePath, options) => {
        return createNodesInternal(configFilePath, options);
    },
];

async function createNodesInternal(
    configFilePath: string,
    { docsTargetName = 'docs' }: MkDocsPluginOptions = {},
): Promise<CreateNodesResult> {
    const projectRoot = dirname(configFilePath);

    return {
        projects: {
            [projectRoot]: {
                targets: {
                    [docsTargetName]: {
                        executor: '@nxlv/python:run-commands',
                        metadata: {
                            description: 'Serve the Mkdocs documentation locally',
                        },
                        options: {
                            command: 'poetry run mkdocs serve',
                        },
                    },
                },
            },
        },
    };
}
