import type { APIRoute } from "astro";
import { publishedPosts, publishedTags } from "../lib/posts";
const escapeXml = (value: string) => value.replace(/[<>&'\"]/g, (character) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", "'": "&apos;", '"': "&quot;" })[character]!);
export const GET: APIRoute = async ({ site }) => {
  const posts = await publishedPosts(); const tags = await publishedTags();
  const entries: { path: string; lastmod?: string }[] = [...["/", "/about/", "/archive/", "/tags/"].map((path) => ({ path })), ...tags.map(({ slug }) => ({ path: `/tags/${slug}/` })), ...posts.map((post) => ({ path: `/notes/${post.id}/`, lastmod: post.data.pubDate.toISOString().slice(0, 10) }))];
  const urls = entries.map(({ path, lastmod }) => `<url><loc>${escapeXml(new URL(path, site).toString())}</loc>${lastmod ? `<lastmod>${lastmod}</lastmod>` : ""}</url>`).join("");
  return new Response(`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urls}</urlset>`, { headers: { "Content-Type": "application/xml; charset=utf-8" } });
};
