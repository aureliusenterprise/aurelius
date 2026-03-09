import { CreateNodesResult, CreateNodes } from "@nx/devkit";
import { dirname } from "path";

export interface SopsPluginOptions {
    readonly keygenTargetName?: string;
}

const glob = ".sops.yaml";

export const createNodes: CreateNodes<SopsPluginOptions> = [
    glob,
    async (configFilePath, options) => {
        return createNodesInternal(
            configFilePath,
            options,
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