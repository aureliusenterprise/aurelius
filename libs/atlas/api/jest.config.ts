export default {
    displayName: 'atlas-api',
    preset: '../../../jest.preset.js',
    coverageDirectory: '../../../coverage/libs/atlas/api',
    snapshotSerializers: [
        'jest-preset-angular/build/serializers/no-ng-attributes',
        'jest-preset-angular/build/serializers/ng-snapshot',
        'jest-preset-angular/build/serializers/html-comment',
    ],
};
