import { defineConfig } from "vitepress";

export default defineConfig({
  title: "shadcn-qt",
  description: "shadcn-aligned Qt widgets for PySide, PyQt, and C++",
  themeConfig: {
    nav: [
      { text: "Guide", link: "/guide/install" },
      { text: "Components", link: "/components/button" },
      { text: "License", link: "/guide/licensing" },
    ],
    sidebar: [
      {
        text: "Guide",
        items: [
          { text: "Install", link: "/guide/install" },
          { text: "Existing Projects", link: "/guide/migration" },
          { text: "Theming", link: "/guide/theming" },
          { text: "Qt Designer", link: "/guide/designer" },
          { text: "Licensing", link: "/guide/licensing" },
          { text: "Publishing", link: "/guide/releasing" },
        ],
      },
      {
        text: "Components",
        items: [
          { text: "Catalog", link: "/components/catalog" },
          { text: "Button", link: "/components/button" },
        ],
      },
      { text: "License Tiers", link: "/tiers" },
    ],
  },
});
