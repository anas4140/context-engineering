// @ts-check
const path = require('path');
const { themes: prismThemes } = require('prism-react-renderer');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title:   'Context Engineering for AI',
  tagline: 'A free, open-source course on building robust, reliable, and efficient context-aware AI applications.',
  favicon: 'img/favicon.ico',

  url:     'https://anas4140.github.io',
  baseUrl: '/context-engineering/',

  organizationName: 'anas4140',
  projectName:      'context-engineering',
  deploymentBranch: 'gh-pages',
  trailingSlash:    false,

  onBrokenLinks:        'warn',
  onBrokenMarkdownLinks: 'warn',

  // Use plain CommonMark for .md files (lesson files use [] notation that
  // MDX would try to parse as JSX — format:'md' avoids that)
  markdown: { format: 'md' },

  i18n: { defaultLocale: 'en', locales: ['en'] },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          // Point directly at the existing Lessons/ folder in the repo root
          path:        path.resolve(__dirname, '../Lessons'),
          sidebarPath: require.resolve('./sidebars.js'),
          routeBasePath: 'docs',
          showLastUpdateTime: true,
        },
        blog:  false,
        theme: { customCss: require.resolve('./src/css/custom.css') },
        gtag:  false,
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/og-card.png',

      navbar: {
        title: 'Context Engineering for AI',
        logo:  { alt: 'Course logo', src: 'img/logo.svg' },
        items: [
          {
            type:      'docSidebar',
            sidebarId: 'courseSidebar',
            position:  'left',
            label:     'Lessons',
          },
          {
            href:     'https://github.com/anas4140/context-engineering',
            label:    'GitHub',
            position: 'right',
          },
        ],
      },

      footer: {
        style: 'dark',
        links: [
          {
            title: 'Course',
            items: [
              { label: 'Start Here',       to: '/docs/Module1/Lesson1_What_is_Context' },
              { label: 'Final Project',    to: '/docs/Module7/Lesson4_CWA' },
              { label: 'GitHub Repo',      href: 'https://github.com/anas4140/context-engineering' },
            ],
          },
          {
            title: 'Modules',
            items: [
              { label: 'Module 1 — Foundations',     to: '/docs/Module1/Lesson1_What_is_Context' },
              { label: 'Module 5 — Agents',          to: '/docs/Module5/Lesson1_ReAct_Pattern' },
              { label: 'Module 8 — Extended Thinking', to: '/docs/Module8/Lesson1_Extended_Thinking' },
              { label: 'Module 10 — MCP',            to: '/docs/Module10/Lesson1_MCP_Introduction' },
            ],
          },
          {
            title: 'Resources',
            items: [
              { label: 'Anthropic Console', href: 'https://console.anthropic.com' },
              { label: 'Anthropic Docs',    href: 'https://docs.anthropic.com' },
            ],
          },
        ],
        copyright: `MIT License · Built with Docusaurus`,
      },

      prism: {
        theme:           prismThemes.github,
        darkTheme:       prismThemes.dracula,
        additionalLanguages: ['python', 'bash', 'json', 'yaml'],
      },

      colorMode: {
        defaultMode:          'light',
        disableSwitch:        false,
        respectPrefersColorScheme: true,
      },

      docs: {
        sidebar: {
          hideable:          true,
          autoCollapseCategories: true,
        },
      },
    }),
};

module.exports = config;
