# Windows compatibility fixes

## render.mjs (2026-10-24)

1. **Chrome path**: Added `win32` detection → defaults to `C:\Program Files\Google\Chrome\Application\chrome.exe`.
2. **GPU flags**: Windows uses `--use-angle=d3d11 --enable-gpu` (Direct3D 11 backend).
3. **LOCKDIR**: Changed from `/tmp/mg-render-slots` to `path.join(os.tmpdir(), 'mg-render-slots')` — works on all platforms.
