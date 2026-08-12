import { EditEntityResolver } from '../../edit-entity/edit-entity-resolver';

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
