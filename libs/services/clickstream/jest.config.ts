export default {
    displayName: 'services-clickstream',
    preset: '../../../jest.preset.js',
    coverageDirectory: '../../../coverage/libs/services/clickstream',
    snapshotSerializers: [
        'jest-preset-angular/build/serializers/no-ng-attributes',
        'jest-preset-angular/build/serializers/ng-snapshot',
        'jest-preset-angular/build/serializers/html-comment',
    ],
};
