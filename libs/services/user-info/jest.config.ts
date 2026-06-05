export default {
    displayName: 'services-user-info',
    preset: '../../../jest.preset.js',
    coverageDirectory: '../../../coverage/libs/services/user-info',
    snapshotSerializers: [
        'jest-preset-angular/build/serializers/no-ng-attributes',
        'jest-preset-angular/build/serializers/ng-snapshot',
        'jest-preset-angular/build/serializers/html-comment',
    ],
};
