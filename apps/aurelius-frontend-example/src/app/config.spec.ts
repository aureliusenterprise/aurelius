import { AppConfig, parseAppConfig } from "./config";

const valid = {
    keycloak: { clientId: "aurelius", realm: "master", url: "http://keycloak.localhost:8080" },
    apiBaseUrl: "/api",
    otelExporterUrl: "/otel/v1/traces",
};

describe("parseAppConfig", () => {
    it("returns a typed config for a valid payload", () => {
        expect(parseAppConfig(valid)).toEqual(valid as AppConfig);
    });

    it("throws when the payload is not an object", () => {
        expect(() => parseAppConfig(null)).toThrow(/expected a JSON object/);
        expect(() => parseAppConfig("nope")).toThrow(/expected a JSON object/);
    });

    it("throws when keycloak is missing", () => {
        expect(() => parseAppConfig({ ...valid, keycloak: undefined })).toThrow(/missing "keycloak"/);
    });

    it.each([
        ["keycloak.clientId", { keycloak: { realm: "master", url: "u" }, apiBaseUrl: "/api", otelExporterUrl: "/o" }],
        ["keycloak.realm", { keycloak: { clientId: "c", url: "u" }, apiBaseUrl: "/api", otelExporterUrl: "/o" }],
        ["keycloak.url", { keycloak: { clientId: "c", realm: "r" }, apiBaseUrl: "/api", otelExporterUrl: "/o" }],
        ["apiBaseUrl", { keycloak: valid.keycloak, otelExporterUrl: "/o" }],
        ["otelExporterUrl", { keycloak: valid.keycloak, apiBaseUrl: "/api" }],
    ])("throws when %s is missing or empty", (name, payload) => {
        expect(() => parseAppConfig(payload)).toThrow(new RegExp(`"${name}" must be a non-empty string`));
    });
});
