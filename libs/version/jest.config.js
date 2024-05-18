module.exports = {
  name: 'version',
  preset: '../../jest.config.js',
  coverageDirectory: '../../coverage/libs/version',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
