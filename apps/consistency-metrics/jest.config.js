module.exports = {
  name: 'consistency-metrics',
  preset: '../../jest.config.js',
  coverageDirectory: '../../coverage/apps/consistency-metrics',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
