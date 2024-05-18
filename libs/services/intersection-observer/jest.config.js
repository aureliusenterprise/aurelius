module.exports = {
  name: 'services-intersection-observer',
  preset: '../../../jest.config.js',
  coverageDirectory: '../../../coverage/libs/services/intersection-observer',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
