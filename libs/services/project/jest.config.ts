export default {
    displayName: 'services-project',
    preset: '../../../jest.preset.js',
    coverageDirectory: '../../../coverage/libs/services/project',
    snapshotSerializers: [
        'jest-preset-angular/build/serializers/no-ng-attributes',
        'jest-preset-angular/build/serializers/ng-snapshot',
        'jest-preset-angular/build/serializers/html-comment',
    ],
};
