module.exports = {
  name: 'atlas',
  preset: '../../jest.config.js',
  coverageDirectory: '../../coverage/apps/atlas',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
