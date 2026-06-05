export default {
    displayName: 'authentication',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/authentication',
    snapshotSerializers: [
        'jest-preset-angular/build/serializers/no-ng-attributes',
        'jest-preset-angular/build/serializers/ng-snapshot',
        'jest-preset-angular/build/serializers/html-comment',
    ],
};
