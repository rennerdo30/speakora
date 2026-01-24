import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import starlightThemeGalaxy from "starlight-theme-galaxy";

export default defineConfig({
  site: "https://rennerdo30.github.io",
  base: "/speakora",
  integrations: [
    starlight({
      title: "Speakora",
      description: "Speech-to-Speech Translation Made Simple - Powered by Meta's SeamlessM4T v2",
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
