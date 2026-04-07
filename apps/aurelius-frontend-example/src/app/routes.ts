import { ActivatedRouteSnapshot, RouterStateSnapshot, Routes } from "@angular/router";
import { AuthGuardData, createAuthGuard } from "keycloak-angular";

async function rootAuthGuard(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot,
    { authenticated, keycloak }: AuthGuardData,
): Promise<boolean> {
    // If not authenticated, redirect to login
    if (!authenticated) {
        await keycloak.login({ redirectUri: globalThis.location.origin + state.url });
    }
    return authenticated;
}

export const routes: Routes = [
    {
        path: "",
        canActivate: [createAuthGuard(rootAuthGuard)],
        loadComponent: () => import("./home/home.component").then((m) => m.Home),
    },
];
