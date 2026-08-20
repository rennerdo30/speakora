import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import starlightThemeGalaxy from "starlight-theme-galaxy";
import mermaid from "astro-mermaid";

export default defineConfig({
  // site and base are set via CLI args in CI (from actions/configure-pages)
  integrations: [
    // Must be listed before starlight: astro-mermaid registers the remark
    // plugin that has to see ```mermaid fences before Starlight processes
    // the markdown.
    mermaid({
      // Follows Starlight's light/dark toggle via the data-theme attribute.
      autoTheme: true,
    }),
    starlight({
      title: "Speakora",
      description: "Speech-to-Speech Translation Made Simple - Powered by Meta's SeamlessM4T v2",
      logo: { src: "./public/logo.svg", alt: "Speakora" },
      favicon: "/logo.svg",
      plugins: [starlightThemeGalaxy()],
      customCss: ["./src/styles/custom.css"],
      social: [
        { icon: "github", label: "GitHub", href: "https://github.com/rennerdo30/speakora" },
      ],
      sidebar: [
        { label: "Home", slug: "index" },
        {
          label: "Getting Started",
          items: [
            { label: "Installation", slug: "getting-started/installation" },
            { label: "Quick Start", slug: "getting-started/quickstart" },
            { label: "Configuration", slug: "getting-started/configuration" },
          ],
        },
      ],
    }),
  ],
});
