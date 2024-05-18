module.exports = {
  name: 'metamodel',
  preset: '../../jest.config.js',
  coverageDirectory: '../../coverage/libs/metamodel',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
