module.exports = {
  name: 'logger',
  preset: '../../jest.config.js',
  coverageDirectory: '../../coverage/libs/logger',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
