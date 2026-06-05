export default {
    displayName: 'services-clickstream',
    preset: '../../../jest.preset.js',
    coverageDirectory: '../../../coverage/libs/services/clickstream',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
