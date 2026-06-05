export default {
    displayName: 'statistics',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/statistics',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
