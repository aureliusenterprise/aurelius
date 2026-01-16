module.exports = {
    flowFile: "flows.json",
    uiPort: process.env.PORT || 1880,
    disableEditor: true,
    diagnostics: {
        enabled: true,
    },
    runtimeState: {
        enabled: false,
    },
    logging: {
        console: {
            level: "info",
            metrics: false,
            audit: false,
        },
    },
};
