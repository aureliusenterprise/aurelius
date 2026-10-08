import { createNodesFromFiles, CreateNodesResult, CreateNodes } from "@nx/devkit";
import { dirname } from "node:path";

export interface MkdocsPluginOptions {
    readonly docsTargetName?: string;
}

const glob = "mkdocs.yaml";

export const createNodes: CreateNodes<MkdocsPluginOptions> = [
    glob,
    async (configFiles, options, context) => {
        return await createNodesFromFiles(
            (configFile) => createNodesInternal(configFile, options),
            configFiles,
            options,
            context,
        );
    },
];

async function createNodesInternal(
    configFilePath: string,
    { docsTargetName = "docs" }: MkdocsPluginOptions = {},
): Promise<CreateNodesResult> {
    const projectRoot = dirname(configFilePath);

    return {
        projects: {
            [projectRoot]: {
                targets: {
                    [docsTargetName]: {
                        continuous: true,
                        executor: "@nxlv/python:run-commands",
                        metadata: {
                            description: "Serve the documentation locally with Zensical",
                        },
                        options: {
                            command: "uv run zensical serve",
                        },
                    },
                },
            },
        },
    };
}
