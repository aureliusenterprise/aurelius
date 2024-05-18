const rootMain = require('../../../.storybook/main');

module.exports = {
  ...rootMain,

  core: { ...rootMain.core, builder: 'webpack5' },

  stories: ['../../../apps/atlas/**/src/**/*.mdx', '../../../libs/**/src/**/*.mdx', '../../../apps/atlas/**/src/**/*.stories.@(js|jsx|ts|tsx)', '../../../libs/**/src/**/*.stories.@(js|jsx|ts|tsx)'],
  addons: [...rootMain.addons, '@storybook/addon-mdx-gfm'],
  webpackFinal: async (config, { configType }) => {
    // apply any global webpack configs that might have been specified in .storybook/main.js
    if (rootMain.webpackFinal) {
      config = await rootMain.webpackFinal(config, { configType });
    }

    // add your own webpack tweaks if needed

    return config;
  },
};
