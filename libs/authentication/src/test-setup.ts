import 'zone.js';
import 'jest-preset-angular/setup-jest';

// Mock keycloak-js for jsdom environment
jest.mock('keycloak-js', () => {
    class MockKeycloak {
        readonly clientId: string;
        readonly realm: string;
        readonly url: string;
        readonly authenticated = false;
        readonly token: string | null = null;
        readonly idToken: string | null = null;
        readonly refreshToken: string | null = null;
        readonly tokenParsed: any = null;
        readonly idTokenParsed: any = null;
        readonly profile: any = null;

        constructor(config?: { clientId?: string; realm?: string; url?: string }) {
            if (config) {
                this.clientId = config.clientId || '';
                this.realm = config.realm || '';
                this.url = config.url || '';
            }
        }

        init = () => Promise.resolve(true);
        login = () => Promise.resolve({});
        logout = () => Promise.resolve({});
        hasRealmRole = () => false;
        hasResourceRole = () => false;
        isTokenExpired = () => true;
        updateToken = () => Promise.resolve(true);
        getToken = () => null;
        getTimeSkew = () => 0;
        loadUserProfile = () => Promise.resolve({});
    }

    return { default: MockKeycloak };
});
