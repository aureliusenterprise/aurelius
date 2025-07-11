import { createNodesFromFiles, CreateNodesResult, CreateNodesV2 } from "@nx/devkit";
import { dirname } from "path";

export interface SopsPluginOptions {
    readonly keygenTargetName?: string;
}

const glob = ".sops.yaml";

export const createNodesV2: CreateNodesV2<SopsPluginOptions> = [
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
    { keygenTargetName = "keygen" }: SopsPluginOptions = {},
): Promise<CreateNodesResult> {
    const projectRoot = dirname(configFilePath);

    return {
        projects: {
            [projectRoot]: {
                targets: {
                    [keygenTargetName]: {
                        command: `age-keygen -o $SOPS_AGE_KEY_FILE`,
                        metadata: {
                            description: "Generate a new SOPS key pair",
                        },
                    },
                },
            },
        },
    };
}
