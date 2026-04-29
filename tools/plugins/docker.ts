import { createNodesFromFiles, CreateNodesResult, CreateNodesV2 } from "@nx/devkit";
import { dirname } from "node:path";

export interface DockerPluginOptions {
    readonly buildTargetName?: string;
    readonly licenseScanTargetName?: string;
    readonly publishTargetName?: string;
    readonly sbomTargetName?: string;
    readonly setupBuilderTargetName?: string;
    readonly signTargetName?: string;
    readonly verifyTargetName?: string;
    readonly vulnScanTargetName?: string;
}

const glob = "**/Dockerfile";

export const createNodesV2: CreateNodesV2<DockerPluginOptions> = [
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
        buildTargetName = "docker-build",
        licenseScanTargetName = "docker-license-scan",
        publishTargetName = "docker-publish",
        sbomTargetName = "docker-sbom",
        setupBuilderTargetName = "docker-setup-builder",
        signTargetName = "docker-sign",
        verifyTargetName = "docker-verify",
        vulnScanTargetName = "docker-vuln-scan",
    }: DockerPluginOptions = {},
): Promise<CreateNodesResult> {
    const projectRoot = dirname(configFilePath);

    return {
        projects: {
            ["."]: {
                targets: {
                    [setupBuilderTargetName]: {
                        command:
                            "docker buildx create --name {args.builder} --node {args.builder} --driver docker-container",
                        metadata: {
                            description: "Set up the Docker Buildx builder instance",
                        },
                        options: {
                            builder: "container",
                            env: {
                                DOCKER_BUILDKIT: "1",
                            },
                        },
                    },
                },
            },
            [projectRoot]: {
                tags: ["docker"],
                targets: {
                    [buildTargetName]: {
                        command: `docker buildx build . -f ${configFilePath} -t {args.namespace}/{projectName}:{args.version} --build-arg VERSION={args.version}`,
                        dependsOn: [
                            { target: "build" },
                            { target: setupBuilderTargetName, projects: ["."], params: "forward" },
                            { target: buildTargetName, dependencies: true },
                        ],
                        metadata: {
                            description: "Build the Docker image for the application",
                        },
                        options: {
                            env: {
                                DOCKER_BUILDKIT: "1",
                            },
                            namespace: "ghcr.io/aureliusenterprise",
                            version: "local",
                        },
                    },
                    [publishTargetName]: {
                        command: `docker buildx build . -f ${configFilePath} -t {args.namespace}/{projectName}:{args.version} --build-arg VERSION={args.version} --builder {args.builder} --provenance=true --sbom=true --push`,
                        options: {
                            env: {
                                DOCKER_BUILDKIT: "1",
                            },
                            builder: "container",
                            namespace: "ghcr.io/aureliusenterprise",
                            version: "latest",
                        },
                        dependsOn: [
                            { target: "build" },
                            { target: setupBuilderTargetName, projects: ["."], params: "forward" },
                            { target: publishTargetName, dependencies: true, params: "forward" },
                        ],
                        metadata: {
                            description: "Publish the Docker image for the application",
                        },
                    },
                    [sbomTargetName]: {
                        command: `syft {args.namespace}/{projectName}:{args.version} -o spdx-json=${projectRoot}/sbom.json --enrich=all`,
                        options: {
                            namespace: "ghcr.io/aureliusenterprise",
                            version: "local",
                        },
                        dependsOn: [{ target: buildTargetName, dependencies: true, params: "forward" }],
                        metadata: {
                            description: "Generate a Software Bill of Materials (SBOM) for the Docker image",
                        },
                    },
                    [signTargetName]: {
                        command:
                            "DIGEST=$(docker buildx imagetools inspect {args.namespace}/{projectName}:{args.version} --format '{{.Manifest.Digest}}') && cosign sign --yes {args.namespace}/{projectName}@${DIGEST}",
                        options: {
                            namespace: "ghcr.io/aureliusenterprise",
                            version: "local",
                        },
                        metadata: {
                            description: "Sign the Docker image with Cosign",
                        },
                    },
                    [verifyTargetName]: {
                        command:
                            "DIGEST=$(docker buildx imagetools inspect {args.namespace}/{projectName}:{args.version} --format '{{.Manifest.Digest}}') && cosign verify {args.namespace}/{projectName}@${DIGEST} --certificate-identity-regexp '{args.identity}' --certificate-oidc-issuer-regexp '{args.issuer}'",
                        options: {
                            identity: ".*",
                            issuer: ".*",
                            namespace: "ghcr.io/aureliusenterprise",
                            version: "local",
                        },
                        metadata: {
                            description: "Verify Cosign signatures for the Docker image",
                        },
                    },
                    [licenseScanTargetName]: {
                        command: `trivy image {args.namespace}/{projectName}:{args.version} --scanners license --format json --output {projectRoot}/licenses.json --exit-code {args.exitCode}`,
                        options: {
                            exitCode: 0,
                            namespace: "ghcr.io/aureliusenterprise",
                            version: "local",
                        },
                        metadata: {
                            description: "Scan the Docker image for license compliance using Trivy",
                        },
                        parallelism: false,
                    },
                    [vulnScanTargetName]: {
                        command: `trivy image {args.namespace}/{projectName}:{args.version} --scanners vuln --format json --output {projectRoot}/vulnerabilities.json --exit-code {args.exitCode}`,
                        options: {
                            exitCode: 0,
                            namespace: "ghcr.io/aureliusenterprise",
                            version: "local",
                        },
                        metadata: {
                            description: "Scan the Docker image for vulnerabilities using Trivy",
                        },
                        parallelism: false,
                    },
                },
            },
        },
    };
}
