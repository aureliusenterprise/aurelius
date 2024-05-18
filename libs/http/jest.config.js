module.exports = {
  name: 'http',
  preset: '../../jest.config.js',
  coverageDirectory: '../../coverage/libs/http',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
