# Canvas presets

Choose the preset from the requested platform or use case. Platform interfaces can change; treat these as production presets and verify current platform requirements when exact upload compliance matters.

| Preset | Size | Ratio | Typical use |
|---|---:|---:|---|
| `xhs-portrait` | 1242×1660 | 3:4 | Xiaohongshu carousel/card |
| `wechat-cover` | 900×383 | ≈2.35:1 | WeChat Official Account main cover |
| `wechat-square-cover` | 500×500 | 1:1 | WeChat secondary/share cover |
| `wechat-inline-portrait` | 1080×1440 | 3:4 | WeChat article inline editorial card |
| `landscape-16x9` | 1920×1080 | 16:9 | Landscape cover, presentation, video title |
| `portrait-9x16` | 1080×1920 | 9:16 | Story, Reel, vertical video cover |
| `square-1x1` | 1080×1080 | 1:1 | Square social post |
| `portrait-4x5` | 1080×1350 | 4:5 | Portrait social feed |
| `landscape-3x2` | 1800×1200 | 3:2 | Editorial landscape image |
| `custom` | explicit | any | User-specified canvas |

## Responsive adaptation

- Do not merely crop one composition into every ratio. Reflow the focal cluster, text blocks, and negative space for each target.
- Portrait canvases may use vertical separation and lower/upper clusters. Landscape canvases should distribute the focal event along a horizontal axis.
- `wechat-cover` needs a simpler composition and larger essential text because it appears small and may be cropped in previews.
- `portrait-9x16` must keep essential content away from the top and bottom interface zones. Use a central safe area unless the user provides platform-specific overlays.
- For multiple requested formats, create one master content plan, then export a separately composed version for each ratio. Count them as variants, not additional carousel cards.
