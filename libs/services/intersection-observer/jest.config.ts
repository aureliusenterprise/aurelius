export default {
    displayName: 'services-intersection-observer',
    preset: '../../../jest.preset.js',
    coverageDirectory: '../../../coverage/libs/services/intersection-observer',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
