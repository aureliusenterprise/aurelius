import { createNodesFromFiles, CreateNodesResult, CreateNodesV2 } from "@nx/devkit";
import { dirname } from "path";

export interface SopsDecryptPluginOptions {
    readonly decryptDefaultConfiguration?: string;
    readonly decryptTargetName?: string;
    readonly updateKeys?: string;
}

const glob = "**/.env.enc";

export const createNodesV2: CreateNodesV2<SopsDecryptPluginOptions> = [
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
    {
        decryptDefaultConfiguration = ".env",
        decryptTargetName = "decrypt",
        updateKeys = "update-keys",
    }: SopsDecryptPluginOptions = {},
): Promise<CreateNodesResult> {
    const projectRoot = dirname(configFilePath);

    return {
        projects: {
            [projectRoot]: {
                targets: {
                    [decryptTargetName]: {
                        command: `sops decrypt --input-type={args.inputType} --output-type={args.outputType} --output={args.outputPath} {args.inputPath}`,
                        configurations: {
                            ".env": {
                                inputPath: `${projectRoot}/.env.enc`,
                                inputType: "dotenv",
                                outputPath: `${projectRoot}/.env`,
                                outputType: "dotenv",
                            },
                        },
                        defaultConfiguration: decryptDefaultConfiguration,
                        metadata: {
                            description: "Decrypt a file so that it can be used locally",
                        },
                    },
                    [updateKeys]: {
                        command: `sops updatekeys --input-type={args.inputType} --yes {args.inputPath}`,
                        configurations: {
                            ".env": {
                                inputPath: `${projectRoot}/.env.enc`,
                                inputType: "dotenv",
                            },
                        },
                        defaultConfiguration: decryptDefaultConfiguration,
                        metadata: {
                            description: "Sync an encrypted file with the keys from .sops.yaml",
                        },
                    },
                },
            },
        },
    };
}
