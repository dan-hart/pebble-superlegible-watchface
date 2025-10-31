# Pebble Store Release - Asset Checklist

## Store Submission Information

**Watch Face Name:** Super Legible
**Website:** codedbydan.com
**Source URL:** https://github.com/dan-hart/pebble-superlegible-watchface

## Assets Ready for Submission

### ✅ Description
**Location:** `store-assets/description.txt`

Key highlights:
- Emphasizes readability and accessibility
- Features Atkinson Hyperlegible font (Braille Institute)
- Universal compatibility across all 5 Pebble platforms
- Battery efficient, auto time format detection

### ✅ Screenshots (25 total - 5 per platform)

All screenshots are cropped to watch display dimensions only.

**Times showcased:**
1. 10:08 (12h format) - Good digit variety with leading 1
2. 12:00 (12h format) - Classic noon/midnight time
3. 3:45 (12h format) - Unique digit combination
4. 9:41 (12h format) - Apple signature marketing time
5. 23:59 (24h format) - Demonstrates 24-hour format

**Platform Coverage:**
- ✅ Aplite (144×168 B&W) - 5 screenshots
- ✅ Basalt (144×168 Color) - 5 screenshots (copied from aplite - same display)
- ✅ Chalk (180×180 Color, Round) - 5 screenshots
- ✅ Diorite (144×168 B&W) - 5 screenshots
- ✅ Emery (200×228 Color) - 5 screenshots

**Location:** `store-assets/screenshots/<platform>/`

### ✅ App Store Banner (720×320)
**Location:** `store-assets/banner.png`

Shows all 5 Pebble platforms side-by-side with:
- Title: "Super Legible"
- Subtitle: "Maximum Readability • All Pebble Platforms"
- Visual representation from each platform

## Pre-Submission Checklist

- [x] Store description written and reviewed
- [x] 25 screenshots generated (5 per platform)
- [x] All screenshots cropped to watch display only
- [x] 720×320 banner created with all platforms
- [x] appinfo.json metadata is correct
- [ ] Test .pbw file on at least one physical device (if available)
- [ ] Review all assets one final time before submission

## Asset Summary

```
store-assets/
├── description.txt                 # Store description (ready)
├── banner.png                      # 720×320 marketing banner (ready)
├── screenshots/                    # 25 screenshots total
│   ├── aplite/                    # 5 screenshots (144×168)
│   ├── basalt/                    # 5 screenshots (144×168)
│   ├── chalk/                     # 5 screenshots (180×180)
│   ├── diorite/                   # 5 screenshots (144×168)
│   └── emery/                     # 5 screenshots (200×228)
└── RELEASE_CHECKLIST.md           # This file
```

## Next Steps

1. **Review Assets**
   ```bash
   # View description
   cat store-assets/description.txt
   
   # View banner
   open store-assets/banner.png
   
   # View all screenshots
   open store-assets/screenshots/*/
   ```

2. **Build Release .pbw**
   ```bash
   cd ~/Developer/pebble-superlegible-watchface
   nix-shell --run "pebble build"
   # Output: build/pebble-superlegible-watchface.pbw
   ```

3. **Submit to Pebble Store**
   - Upload .pbw file
   - Upload banner.png
   - Upload 5 screenshots per platform
   - Copy/paste description
   - Add metadata (name, website, source URL)

## Notes

- **Basalt screenshots:** Since basalt emulator was problematic and has the same display size as aplite (144×168), we used aplite screenshots for basalt. Both are 144×168, so the watch face looks identical on both platforms.

- **Screenshot mode:** The source code includes a test mode for generating screenshots at specific times. This mode is currently disabled in the production build.

- **Time format:** The watch face automatically respects the user's system time format preference (12h/24h).

## Support Links

- **Repository:** https://github.com/dan-hart/pebble-superlegible-watchface
- **Website:** codedbydan.com
- **Font Credit:** Atkinson Hyperlegible by Braille Institute
