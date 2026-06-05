export default {
    displayName: 'http',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/http',
    snapshotSerializers: [
        'jest-preset-angular/build/serializers/no-ng-attributes',
        'jest-preset-angular/build/serializers/ng-snapshot',
        'jest-preset-angular/build/serializers/html-comment',
    ],
};
