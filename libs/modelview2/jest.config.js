module.exports = {
  name: 'modelview2',
  preset: '../../jest.config.js',
  coverageDirectory: '../../coverage/libs/modelview2',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
