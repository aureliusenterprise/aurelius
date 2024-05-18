module.exports = {
  name: 'statistics',
  preset: '../../jest.config.js',
  coverageDirectory: '../../coverage/libs/statistics',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
