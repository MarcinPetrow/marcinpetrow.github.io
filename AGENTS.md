# Repository Guidelines

## Project Structure & Module Organization

This is a static Astro blog based on BlogGPT. Site configuration lives in `blog.config.ts`; update the title, domain, author profile, sidebar, and appearance there. Markdown and MDX content belongs in `content/`:

- `content/posts/` holds dated articles.
- `content/pages/` holds standalone pages such as `about.md`.
- `content/categories/` and `content/tags/` may hold taxonomy metadata.

Astro components, routes, integrations, and shared helpers are under `src/`. Use `custom/` for project-specific CSS, head markup, body markup, or client code instead of editing theme internals when possible. Static assets belong in `public/`; keep `public/CNAME` for the custom domain. Build and content tooling is in `scripts/`.

## Build, Test, and Development Commands

Use Node 24 and pnpm 11.23.0. Install dependencies with `pnpm install --frozen-lockfile`.

- `pnpm dev` starts Astro locally.
- `pnpm check` runs Astro and TypeScript diagnostics.
- `pnpm build` validates content, builds `dist/`, generates the Pagefind search index, RSS, sitemap, and OG images.
- `pnpm preview` serves the production build.
- `pnpm lint` and `pnpm format:check` check style; `pnpm format` applies Prettier.
- `pnpm new post my-note --title "My note"` scaffolds a post.

## Coding Style & Naming Conventions

Use TypeScript and Astro with two-space indentation, single quotes, and trailing commas, matching existing files. Prettier plus `prettier-plugin-astro` and `prettier-plugin-tailwindcss` define formatting. Name route and content files with lowercase kebab-case, for example `content/posts/what-is-boldmerge.md`. Post front matter requires `title`, `date` (`YYYY-MM-DD`), and usually `description`; use lowercase ASCII slugs for tags and categories, such as `product-development`.

## Testing Guidelines

There is no separate unit-test suite. Before submitting changes, run `pnpm check` and `pnpm build`. Verify visual changes in `pnpm dev` or `pnpm preview`, including desktop and mobile sidebars, search, article routes, and dark mode when relevant.

## Commit & Pull Request Guidelines

Use short, imperative commit subjects consistent with history: `Add BoldMerge bottom bar`, `Publish dummy note`, or `Migrate blog to BlogGPT theme`. Keep commits focused. Pull requests should explain the user-visible change, list validation commands, link relevant issues when available, and include screenshots for layout or styling changes. Pushes to `master` deploy through GitHub Actions; pull requests build but do not deploy.
