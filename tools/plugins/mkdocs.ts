import { createNodesFromFiles, CreateNodesResult, CreateNodesV2 } from "@nx/devkit";
import { dirname } from "path";

export interface MkdocsPluginOptions {
    readonly docsTargetName?: string;
}

const glob = "mkdocs.yaml";

export const createNodesV2: CreateNodesV2<MkdocsPluginOptions> = [
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
                            description: "Serve the Mkdocs documentation locally",
                        },
                        options: {
                            command: "uv run mkdocs serve",
                        },
                    },
                },
            },
        },
    };
}
