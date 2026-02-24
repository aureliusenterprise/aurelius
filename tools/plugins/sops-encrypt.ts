import { CreateNodesResult, CreateNodes } from "@nx/devkit";
import { dirname } from "path";

export interface SopsEncryptPluginOptions {
    readonly encryptDefaultConfiguration?: string;
    readonly encryptTargetName?: string;
}

const glob = "**/.env";

export const createNodes: CreateNodes<SopsEncryptPluginOptions> = [
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
    { encryptDefaultConfiguration = ".env", encryptTargetName = "encrypt" }: SopsEncryptPluginOptions = {},
): Promise<CreateNodesResult> {
    const projectRoot = dirname(configFilePath);

    return {
        projects: {
            [projectRoot]: {
                targets: {
                    [encryptTargetName]: {
                        configurations: {
                            ".env": {
                                inputPath: `${projectRoot}/.env`,
                                inputType: "dotenv",
                                outputPath: `${projectRoot}/.env.enc`,
                                outputType: "dotenv",
                            },
                        },
                        command: `sops encrypt --input-type={args.inputType} --output-type={args.outputType} --output={args.outputPath} {args.inputPath}`,
                        defaultConfiguration: encryptDefaultConfiguration,
                        metadata: {
                            description: "Encrypt a file so that it can be securely committed to the repository",
                        },
                    },
                },
            },
        },
    };
}