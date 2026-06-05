export default {
    displayName: 'google-analytics',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/google-analytics',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
