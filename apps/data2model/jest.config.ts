export default {
    displayName: 'data2model',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/apps/data2model',
    snapshotSerializers: [
        'jest-preset-angular/build/serializers/no-ng-attributes',
        'jest-preset-angular/build/serializers/ng-snapshot',
        'jest-preset-angular/build/serializers/html-comment',
    ],
};
