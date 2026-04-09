import { signal, WritableSignal } from "@angular/core";
import { TestBed } from "@angular/core/testing";
import { KEYCLOAK_EVENT_SIGNAL, KeycloakEvent, KeycloakEventType, provideKeycloak } from "keycloak-angular";
import Keycloak from "keycloak-js";
import { AuthService } from "./auth.service";

describe("AuthService", () => {
    let eventsSignal: WritableSignal<KeycloakEvent>;
    let keycloak: Keycloak;
    let service: AuthService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                AuthService,
                provideKeycloak({
                    config: {
                        url: "keycloak-server-url",
                        realm: "realm-id",
                        clientId: "client-id",
                    },
                }),
                {
                    provide: KEYCLOAK_EVENT_SIGNAL,
                    useValue: signal<KeycloakEvent>({ type: KeycloakEventType.Ready, args: false }),
                },
            ],
        });
        eventsSignal = TestBed.inject(KEYCLOAK_EVENT_SIGNAL) as WritableSignal<KeycloakEvent>;
        keycloak = TestBed.inject(Keycloak);
        service = TestBed.inject(AuthService);
    });

    it("should initialize with unauthenticated state", () => {
        expect(service.authenticated()).toBe(false);
        expect(service.profile()).toBeNull();
    });

    it("should call accountManagement", async () => {
        const accountManagement = vi.spyOn(keycloak, "accountManagement").mockResolvedValueOnce();
        await service.accountManagement();

        expect(accountManagement).toHaveBeenCalled();
    });

    it("should call login", async () => {
        const login = vi.spyOn(keycloak, "login").mockResolvedValueOnce();
        await service.login();

        expect(login).toHaveBeenCalledWith({ redirectUri: globalThis.location.origin });
    });

    it("should call logout", async () => {
        const logout = vi.spyOn(keycloak, "logout").mockResolvedValueOnce();
        await service.logout();

        expect(logout).toHaveBeenCalledWith({ redirectUri: globalThis.location.origin });
    });

    it(
        "should load user profile when authenticated",
        async () =>
            new Promise<void>((done) => {
                const loadUserProfile = vi
                    .spyOn(keycloak, "loadUserProfile")
                    .mockResolvedValueOnce({ username: "testuser" });

                eventsSignal.set({ type: KeycloakEventType.Ready, args: true });

                setTimeout(() => {
                    expect(loadUserProfile).toHaveBeenCalled();
                    expect(service.profile()).toEqual({ username: "testuser" });
                    done();
                }, 50);
            }),
        100,
    );

    it("should return null profile when not authenticated", async () => {
        expect(service.authenticated()).toBe(false);
        expect(service.profile()).toBeNull();
    });
});
