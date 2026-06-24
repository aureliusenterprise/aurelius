import { createNodesFromFiles, CreateNodesResult, CreateNodes } from "@nx/devkit";
import { dirname } from "node:path";

export interface AlembicPluginOptions {
    readonly generateMigrationsTargetName?: string;
}

const glob = "**/alembic.ini";

export const createNodes: CreateNodes<AlembicPluginOptions> = [
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
    { generateMigrationsTargetName = "generate-migrations" }: AlembicPluginOptions = {},
): Promise<CreateNodesResult> {
    const projectRoot = dirname(configFilePath);

    return {
        projects: {
            [projectRoot]: {
                targets: {
                    [generateMigrationsTargetName]: {
                        cache: true,
                        dependsOn: [
                            {
                                target: "decrypt",
                            },
                        ],
                        executor: "@nxlv/python:run-commands",
                        metadata: {
                            description: "Generate alembic migrations",
                        },
                        options: {
                            command: "alembic revision --autogenerate",
                            cwd: projectRoot,
                        },
                    },
                },
            },
        },
    };
}
