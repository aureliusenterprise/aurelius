module.exports = {
  name: 'shell',
  preset: '../../jest.config.js',
  coverageDirectory: '../../coverage/libs/shell',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
