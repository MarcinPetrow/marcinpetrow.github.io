# Marcin Petrów — Notes

A small Astro blog for `marcinpetrow.github.io`. Posts are Markdown files; GitHub Actions builds the static site and publishes it with GitHub Pages.

## Run locally

Use Node 24, then run:

```sh
npm install
npm run check
npm run build
npm run preview
```

The deployment workflow uses the committed `package-lock.json` to install the same dependency versions with `npm ci`.

## Write a post

Add a Markdown file under `src/content/posts/`. Its filename becomes the URL under `/notes/`.

```yaml
---
title: "Your title"
description: "A short introduction."
pubDate: 2026-10-19
tags: [Ideas]
draft: true
---
```

Draft posts are excluded from the generated site and RSS feed. The GitHub repository is public: a committed draft is still visible in the source and Git history. Change `draft` to `false` to publish.

## Deploy

Set Settings → Pages → Build and deployment → Source to **GitHub Actions**. Pull requests are checked without deployment; pushes to `master` build and publish. The existing Pages site remains the active version until a new deployment succeeds.

## Custom domain

The site is configured to use `https://marcin.petrow.pl` as its canonical address. The published `CNAME` file makes GitHub Pages serve that domain after it is configured in the repository’s Pages settings.

In DNS, create a `CNAME` record for `marcin` pointing to `marcinpetrow.github.io`. Then set `marcin.petrow.pl` as the custom domain in Settings → Pages and enable **Enforce HTTPS** once GitHub has issued the certificate.
