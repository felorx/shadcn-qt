import { defineConfig } from "vitepress";

export default defineConfig({
  base: "/shadcn-qt/",
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
          { text: "Native QtWidgets", link: "/guide/native-widgets" },
          { text: "Theming", link: "/guide/theming" },
          { text: "Visual Baseline", link: "/guide/visual-baseline" },
          { text: "Qt Designer", link: "/guide/designer" },
          { text: "Core and Pro", link: "/guide/pro" },
          { text: "Licensing", link: "/guide/licensing" },
          { text: "Publishing", link: "/guide/releasing" },
        ],
      },
      {
        text: "Components",
        items: [
          { text: "Catalog", link: "/components/catalog" },
          { text: "Button", link: "/components/button" },
          { text: "TabPane", link: "/components/tab-pane" },
        ],
      },
      { text: "License Tiers", link: "/tiers" },
    ],
  },
});
