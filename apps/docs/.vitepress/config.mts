import { defineConfig } from "vitepress";

export default defineConfig({
  title: "qtshadcn",
  description: "shadcn-aligned Qt widgets for PySide, PyQt, and C++",
  themeConfig: {
    nav: [
      { text: "Guide", link: "/guide/install" },
      { text: "Components", link: "/components/button" },
      { text: "Tiers", link: "/tiers" },
    ],
    sidebar: [
      {
        text: "Guide",
        items: [
          { text: "Install", link: "/guide/install" },
          { text: "Theming", link: "/guide/theming" },
        ],
      },
      {
        text: "Components",
        items: [{ text: "Button", link: "/components/button" }],
      },
      { text: "Community vs Pro", link: "/tiers" },
    ],
  },
});
