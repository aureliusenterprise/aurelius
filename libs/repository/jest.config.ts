export default {
    displayName: 'repository',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/repository',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
