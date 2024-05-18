module.exports = {
  name: 'data2model',
  preset: '../../jest.config.js',
  coverageDirectory: '../../coverage/apps/data2model',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
