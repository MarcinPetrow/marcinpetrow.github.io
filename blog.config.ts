import type { BlogConfig } from './src/types/config';

// Set SITE_URL for a custom domain, or replace baseUrl below with a fixed URL.
const deploymentUrl =
  process.env.SITE_URL ||
  (process.env.VERCEL_PROJECT_PRODUCTION_URL
    ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`
    : process.env.URL) ||
  'https://marcin.petrow.pl/';

const config: BlogConfig = {
  site: {
    title: 'Marcin Petrów — Notes',
    baseUrl: deploymentUrl,
    defaultLocale: 'en',
    locales: ['en'],
    localePrefixPolicy: 'redirect-to-default',
    timezone: 'Europe/Warsaw',
  },
  author: {
    name: 'Marcin Petrów',
    bio: 'Notes, experiments, and things in progress.',
    avatar: '/favicon.svg',
    socials: [
      {
        label: 'GitHub',
        icon: 'github',
        href: 'https://github.com/MarcinPetrow',
      },
      { label: 'Projects', icon: 'lucide:link', href: 'https://petrow.pl/' },
    ],
  },
  text: {
    siteDescription: 'Notes, experiments, and things in progress.',
    tabs: { search: 'Search', posts: 'Notes' },
    homeHeading: 'What would you like to read?',
    searchHeading: 'Find a note, idea, or keyword',
    searchPlaceholder: 'Search notes and ideas',
    notFoundMessage: 'There is nothing here yet.',
    footerDescription: 'Notes, experiments, and things in progress.',
  },
  posts: {
    perPage: 10,
    homeLimit: 4,
    menuLimit: 12,
    randomLimit: 12,
    dateFormat: { year: 'numeric', month: 'short', day: 'numeric' },
    showDraftsInDev: true,
  },
  sidebar: {
    items: [
      {
        id: 'home',
        type: 'builtin',
        route: 'home',
        label: 'Home',
        icon: 'square-pen',
      },
      {
        id: 'posts',
        type: 'builtin',
        route: 'posts',
        label: 'Notes',
        icon: 'files',
      },
      { id: 'about', type: 'page', page: 'about', label: 'About', icon: 'info' },
    ],
    menu: [
      { id: 'home', type: 'builtin', route: 'home', label: 'Home' },
      { id: 'posts', type: 'builtin', route: 'posts', label: 'Notes' },
    ],
    width: { default: 340, min: 240, max: 480 },
  },
  appearance: {
    defaultTheme: 'system',
    pageTransition: 'fade',
    codeThemes: { light: 'github-light', dark: 'github-dark' },
    showCodeLineNumbers: false,
    categoryCoverStyle: 'thumbnail',
  },
  article: {
    math: true,
    mermaid: true,
    lightbox: true,
    callouts: true,
    toc: {
      enabled: true,
      minDepth: 2,
      maxDepth: 4,
      expandDelay: 1000,
      hideDelay: 800,
    },
    shareCover: {
      enabled: true,
      width: 1200,
      height: 630,
      background: '#f5f5f5',
      foreground: '#171717',
      accent: '#3b82f6',
    },
  },
  footer: {
    since: 2026,
    author: 'Marcin Petrów',
    showAttribution: true,
    license: {
      label: 'CC BY-NC-SA 4.0',
      url: 'https://creativecommons.org/licenses/by-nc-sa/4.0/',
    },
  },
};

export default config;
