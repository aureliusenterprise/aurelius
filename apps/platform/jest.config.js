module.exports = {
  name: 'platform',
  preset: '../../jest.config.js',
  coverageDirectory: '../../coverage/apps/platform',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
