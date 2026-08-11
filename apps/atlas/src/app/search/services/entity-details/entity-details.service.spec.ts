import { EntityDetailsService } from './entity-details.service';

describe('EntityDetailsService', () => {
  it('clears previous entity details when a new entity id is set', async () => {
    const entityApiService = {
      getEntityById: jest.fn().mockReturnValue({
        toPromise: jest.fn().mockResolvedValue({ entity: { guid: 'new-guid' } }),
      }),
    } as any;

    const service = new EntityDetailsService(entityApiService, undefined as any);
    const previousEntityDetails = { entity: { guid: 'old-guid' } } as any;

    service.entityDetails = previousEntityDetails;
    service.entityId = 'new-guid';

    await expect(service.get('entityDetails')).resolves.toBeUndefined();
  });
});
