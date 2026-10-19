import rss from "@astrojs/rss";
import type { APIRoute } from "astro";
import { publishedPosts } from "../lib/posts";

export const GET: APIRoute = async (context) => rss({
  title: "Marcin Petrów — Notes",
  description: "Notes, experiments, and things in progress.",
  site: context.site!,
  items: (await publishedPosts()).map((post) => ({
    title: post.data.title,
    description: post.data.description,
    pubDate: post.data.pubDate,
    link: `/notes/${post.id}/`,
  })),
});
