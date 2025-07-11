import { createNodesFromFiles, CreateNodesResult, CreateNodesV2 } from "@nx/devkit";
import { dirname } from "path";

export interface SopsDecryptPluginOptions {
    readonly decryptDefaultConfiguration?: string;
    readonly decryptTargetName?: string;
}

const glob = "**/.env.lock";

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
    { decryptDefaultConfiguration = ".env", decryptTargetName = "decrypt" }: SopsDecryptPluginOptions = {},
): Promise<CreateNodesResult> {
    const projectRoot = dirname(configFilePath);

    return {
        projects: {
            [projectRoot]: {
                targets: {
                    [decryptTargetName]: {
                        configurations: {
                            ".env": {
                                inputPath: `${projectRoot}/.env.lock`,
                                inputType: "dotenv",
                                outputPath: `${projectRoot}/.env`,
                                outputType: "dotenv",
                            },
                        },
                        command: `sops decrypt --input-type={args.inputType} --output-type={args.outputType} --output={args.outputPath} {args.inputPath}`,
                        defaultConfiguration: decryptDefaultConfiguration,
                        metadata: {
                            description: "Decrypt a file so that it can be used locally",
                        },
                    },
                },
            },
        },
    };
}
