#pragma once

#include <QtGlobal>

namespace shadcn_qt {

struct ThemeTokens {
    struct Light {
        static constexpr const char* kbackground = "#ffffff";
        static constexpr const char* kforeground = "#09090b";
        static constexpr const char* kcard = "#ffffff";
        static constexpr const char* kcardForeground = "#09090b";
        static constexpr const char* kpopover = "#ffffff";
        static constexpr const char* kpopoverForeground = "#09090b";
        static constexpr const char* kprimary = "#18181b";
        static constexpr const char* kprimaryForeground = "#fafafa";
        static constexpr const char* ksecondary = "#f4f4f5";
        static constexpr const char* ksecondaryForeground = "#18181b";
        static constexpr const char* kmuted = "#f4f4f5";
        static constexpr const char* kmutedForeground = "#71717a";
        static constexpr const char* kaccent = "#f4f4f5";
        static constexpr const char* kaccentForeground = "#18181b";
        static constexpr const char* kdestructive = "#ef4444";
        static constexpr const char* kdestructiveForeground = "#fafafa";
        static constexpr const char* kborder = "#e4e4e7";
        static constexpr const char* kinput = "#e4e4e7";
        static constexpr const char* kring = "#18181b";
    };
    struct Dark {
        static constexpr const char* kbackground = "#09090b";
        static constexpr const char* kforeground = "#fafafa";
        static constexpr const char* kcard = "#09090b";
        static constexpr const char* kcardForeground = "#fafafa";
        static constexpr const char* kpopover = "#09090b";
        static constexpr const char* kpopoverForeground = "#fafafa";
        static constexpr const char* kprimary = "#fafafa";
        static constexpr const char* kprimaryForeground = "#18181b";
        static constexpr const char* ksecondary = "#27272a";
        static constexpr const char* ksecondaryForeground = "#fafafa";
        static constexpr const char* kmuted = "#27272a";
        static constexpr const char* kmutedForeground = "#a1a1aa";
        static constexpr const char* kaccent = "#27272a";
        static constexpr const char* kaccentForeground = "#fafafa";
        static constexpr const char* kdestructive = "#7f1d1d";
        static constexpr const char* kdestructiveForeground = "#fafafa";
        static constexpr const char* kborder = "#27272a";
        static constexpr const char* kinput = "#27272a";
        static constexpr const char* kring = "#d4d4d8";
    };
    struct Radius {
        static constexpr const char* ksm = "4px";
        static constexpr const char* kmd = "6px";
        static constexpr const char* klg = "8px";
        static constexpr const char* kxl = "12px";
    };
};

} // namespace shadcn_qt
