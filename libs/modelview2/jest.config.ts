export default {
    displayName: 'modelview2',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/modelview2',
    snapshotSerializers: [
        'jest-preset-angular/build/serializers/no-ng-attributes',
        'jest-preset-angular/build/serializers/ng-snapshot',
        'jest-preset-angular/build/serializers/html-comment',
    ],
};
