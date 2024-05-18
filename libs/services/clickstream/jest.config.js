module.exports = {
  name: 'services-clickstream',
  preset: '../../../jest.config.js',
  coverageDirectory: '../../../coverage/libs/services/clickstream',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
