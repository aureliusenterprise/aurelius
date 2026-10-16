import { Observable, of } from 'rxjs';
import { delay } from 'rxjs/operators';
import { StoreService } from '@models4insight/redux';
import { TaskManagerModule, TaskManagerService } from '@models4insight/task-manager';
import { EditEntityResolver } from '../../edit-entity/edit-entity-resolver';
import { EntityDetailsService } from './entity-details.service';

describe('EditEntityResolver', () => {
    it('clears previous entity state before setting the next edit guid', () => {
        const entityDetailsService = {
            clear: jest.fn(),
            entityId: undefined as string | undefined,
        } as any;

        const resolver = new EditEntityResolver(entityDetailsService);
        const route = { paramMap: { get: jest.fn().mockReturnValue('new-guid') } } as any;

        resolver.resolve(route);

        expect(entityDetailsService.clear).toHaveBeenCalledTimes(1);
        expect(entityDetailsService.entityId).toBe('new-guid');
    });
});

describe('EntityDetailsService', () => {
    let consoleErrorSpy: jest.SpyInstance;

    const createService = (getEntityById: jest.Mock) => {
        const taskManagerService = new TaskManagerService({ navigate: jest.fn() } as any, new StoreService());
        (TaskManagerModule as any).injector = { get: () => taskManagerService };

        return new EntityDetailsService({ getEntityById } as any, undefined as any);
    };

    beforeEach(() => {
        consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
        jest.spyOn(console, 'time').mockImplementation();
        jest.spyOn(console, 'timeEnd').mockImplementation();
    });

    afterEach(() => {
        jest.restoreAllMocks();
    });

    it('stores the retrieved entity details', async () => {
        const entityDetails = { entity: { guid: 'guid-1', typeName: 'm4i_domain' } } as any;
        const service = createService(jest.fn().mockReturnValue(of(entityDetails).pipe(delay(0))));

        service.entityId = 'guid-1';
        await new Promise((resolve) => setTimeout(resolve, 20));

        expect(await service.get('entityDetails')).toBe(entityDetails);
    });

    it('does not fail with an EmptyError when the store is destroyed while a retrieval is in flight', async () => {
        let resolveFetch: (value: any) => void;
        const fetch = new Promise<any>((resolve) => (resolveFetch = resolve));
        const getEntityById = jest.fn().mockReturnValue(
            new Observable<any>((subscriber) => {
                fetch.then((value) => {
                    subscriber.next(value);
                    subscriber.complete();
                });
            }),
        );
        const service = createService(getEntityById);

        service.entityId = 'guid-1';

        // Simulate a route change that tears down the details component, and with it this store,
        // while the entity retrieval is still in flight.
        service.ngOnDestroy();
        resolveFetch({ entity: { guid: 'guid-1' } });

        await new Promise((resolve) => setTimeout(resolve, 20));

        // Before the fix, the stale-fetch guard read the destroyed store, which completed without
        // emitting and surfaced 'EmptyError: no elements in sequence' through the Task Manager.
        expect(consoleErrorSpy).not.toHaveBeenCalledWith(expect.stringContaining('no elements in sequence'));
    });
});
