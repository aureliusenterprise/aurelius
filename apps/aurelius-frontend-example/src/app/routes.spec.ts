import { ActivatedRouteSnapshot, RouterStateSnapshot } from "@angular/router";

const createAuthGuardMock = vi.hoisted(() => vi.fn((guard) => guard));

vi.mock("keycloak-angular", () => ({
    createAuthGuard: createAuthGuardMock,
}));

import { routes } from "./routes";

describe("routes", () => {
    it("should configure the root route", () => {
        expect(routes).toHaveLength(1);

        const [route] = routes;
        expect(route.path).toBe("");
        expect(route.canActivate).toHaveLength(1);
        expect(typeof route.loadComponent).toBe("function");
    });

    it("should call login and return false when unauthenticated", async () => {
        const [route] = routes;
        const guard = route.canActivate?.[0] as (
            route: ActivatedRouteSnapshot,
            state: RouterStateSnapshot,
            authData: {
                authenticated: boolean;
                keycloak: { login: (options: { redirectUri: string }) => Promise<void> };
            },
        ) => Promise<boolean>;

        const login = vi.fn().mockResolvedValue(undefined);
        const state = { url: "/search" } as RouterStateSnapshot;

        const result = await guard({} as ActivatedRouteSnapshot, state, {
            authenticated: false,
            keycloak: { login },
        });

        expect(result).toBe(false);
        expect(login).toHaveBeenCalledWith({
            redirectUri: `${globalThis.location.origin}/search`,
        });
    });

    it("should not call login and return true when authenticated", async () => {
        const [route] = routes;
        const guard = route.canActivate?.[0] as (
            route: ActivatedRouteSnapshot,
            state: RouterStateSnapshot,
            authData: {
                authenticated: boolean;
                keycloak: { login: (options: { redirectUri: string }) => Promise<void> };
            },
        ) => Promise<boolean>;

        const login = vi.fn().mockResolvedValue(undefined);
        const state = { url: "/search" } as RouterStateSnapshot;

        const result = await guard({} as ActivatedRouteSnapshot, state, {
            authenticated: true,
            keycloak: { login },
        });

        expect(result).toBe(true);
        expect(login).not.toHaveBeenCalled();
    });

    it("should register rootAuthGuard with createAuthGuard", () => {
        expect(createAuthGuardMock).toHaveBeenCalledTimes(1);
        const [guardArg] = createAuthGuardMock.mock.calls[0] ?? [];
        expect(typeof guardArg).toBe("function");
    });
});
