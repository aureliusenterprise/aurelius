export default {
    displayName: 'modelview2',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/modelview2',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
