export default {
    displayName: 'services-model',
    preset: '../../../jest.preset.js',
    coverageDirectory: '../../../coverage/libs/services/model',
    snapshotSerializers: [
        'jest-preset-angular/build/serializers/no-ng-attributes',
        'jest-preset-angular/build/serializers/ng-snapshot',
        'jest-preset-angular/build/serializers/html-comment',
    ],
};
