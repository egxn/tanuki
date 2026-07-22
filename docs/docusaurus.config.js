// @ts-check
const { themes: prismThemes } = require('prism-react-renderer');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Tanuki',
  tagline: 'A declarative Python DSL for procedural geometry',
  favicon: 'img/favicon.ico',

  url: 'https://your-site.example.com',
  baseUrl: '/',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          routeBasePath: '/docs',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: 'Tanuki',
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'docsSidebar',
            position: 'left',
            label: 'Docs',
          },
          {
            to: '/docs/dsl/overview',
            label: 'DSL',
            position: 'left',
          },
          {
            to: '/docs/backends/overview',
            label: 'Backends',
            position: 'left',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              { label: 'Introduction', to: '/docs/intro' },
              { label: 'Quickstart', to: '/docs/quickstart' },
              { label: 'DSL Reference', to: '/docs/dsl/overview' },
            ],
          },
          {
            title: 'Backends',
            items: [
              { label: 'Blender', to: '/docs/backends/blender' },
              { label: 'OpenSCAD', to: '/docs/backends/openscad' },
              { label: 'JSCAD', to: '/docs/backends/jscad' },
              { label: 'OpenCascade.js', to: '/docs/backends/opencascade' },
            ],
          },
          {
            title: 'More',
            items: [
              { label: 'IR Reference', to: '/docs/ir/overview' },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Tanuki. Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['python', 'bash', 'javascript'],
      },
    }),
};

module.exports = config;
