# CLAUDE.md

This file provides guidance to Claude Code when working with the Pebble Superledgible watchface project.

## Project Overview

**Superledgible** is a minimalist Pebble watchface focused on maximum readability using the Atkinson Hyperlegible font. The design philosophy is simple: display the time as large as possible with maximum legibility, nothing else.

**Key Features:**
- **Bitmap-based 2x2 quadrant layout** - Four individual digits in a clean grid
- **Maximum digit size** - Each digit uses full quadrant space (72×84px on 144×168 displays)
- Atkinson Hyperlegible font for exceptional readability
- Automatic 12h/24h format detection (leading zero hidden for single-digit hours in 12h)
- Universal support for all 5 Pebble platforms
- Platform-specific optimization (padding for round displays, full quadrants for rectangular)
- Battery efficient (updates once per minute)

## Technical Constraints

### Bitmap-Based Rendering Approach

The watchface uses **pre-rendered bitmap images** for digits 0-9, avoiding Pebble SDK font rendering limitations entirely. This approach provides:

**Advantages:**
- **No glyph size limits** - Bitmaps can be any size
- **Maximum quality** - High-quality anti-aliased rendering
- **Consistent appearance** - Identical rendering across all platforms
- **Optimized performance** - No runtime font rendering overhead

**Trade-offs:**
- **Fixed size** - Digit size determined at bitmap creation time
- **Memory usage** - 10 bitmap resources (digits 0-9) loaded into memory
- **Resource size** - Each bitmap adds to .pbw file size (~8-10KB total for all digits)

### Platform Display Resolutions

| Platform | Resolution | Aspect Ratio | Shape |
|----------|-----------|--------------|-------|
| Aplite (Pebble) | 144×168 | Portrait | Rectangular |
| Basalt (Time) | 144×168 | Portrait | Rectangular |
| Diorite (Pebble 2) | 144×168 | Portrait | Rectangular |
| Emery (Time 2) | 200×228 | Portrait | Rectangular |
| Chalk (Time Round) | 180×180 | Square | Round |

**Impact on Layout:**
- Rectangular displays use two-row layout (full width rows)
- Round display requires padding and text flow
- Platform-specific font sizes can be configured via `#ifdef PBL_ROUND`

**IMPORTANT OPTIMIZATION DIRECTIVE:**
> **Do not let circular display limitations constrain rectangular display optimization.**
> While the watchface must support all platforms, rectangular displays (aplite, basalt, diorite, emery) represent the majority of Pebble devices and should be optimized for maximum digit size and readability. Use platform-specific code (`#ifdef PBL_ROUND`) to provide appropriate handling for circular displays without compromising rectangular display performance.

### 2x2 Quadrant Layout

The watchface uses a clean **2x2 grid layout** with four individual BitmapLayers:

**Quadrant Dimensions (144×168 displays):**
```
Display: 144px wide × 168px tall
Quadrant width:  144 / 2 = 72px
Quadrant height: 168 / 2 = 84px

Grid Layout:
┌────────────┬────────────┐
│ Hour Tens  │ Hour Ones  │  ← Top row (y: 0-84)
│   (0-2)    │   (0-9)    │
├────────────┼────────────┤
│ Min Tens   │ Min Ones   │  ← Bottom row (y: 84-168)
│   (0-5)    │   (0-9)    │
└────────────┴────────────┘
```

**Bitmap Layer Positioning (Rectangular Displays):**
- **Hour Tens**:   GRect(0, 0, 72, 84)
- **Hour Ones**:   GRect(72, 0, 72, 84)
- **Minute Tens**: GRect(0, 84, 72, 84)
- **Minute Ones**: GRect(72, 84, 72, 84)

**Round Display Handling:**
- 10px padding applied to all sides
- Adjusted quadrant dimensions: (180 - 20) / 2 = 80px
- Prevents digits from clipping at curved edges

**12h Format Special Handling:**
- When hour < 10 in 12h format (e.g., 2:30)
- Hour tens layer is hidden: `layer_set_hidden(bitmap_layer_get_layer(s_hour_tens_layer), true)`
- Bitmap set to NULL: `bitmap_layer_set_bitmap(s_hour_tens_layer, NULL)`
- Creates clean appearance without leading zero

## Current Optimal Configuration

### Bitmap Resources (appinfo.json)

```json
"resources": {
  "media": [
    {
      "type": "bitmap",
      "name": "DIGIT_0",
      "file": "images/digit_0.png"
    },
    // ... DIGIT_1 through DIGIT_9
  ]
}
```

**Resource Structure:**
- **10 bitmap files**: `digit_0.png` through `digit_9.png`
- **Location**: `resources/images/`
- **Format**: PNG with transparency
- **Generated from**: Atkinson Hyperlegible font at optimal size
- **Dimensions**: Sized to fit within quadrant dimensions (72×84px for standard displays)

### Code Structure (main.c)

**Bitmap Loading** (main.c:82-85):
```c
// Load all digit bitmaps at window load
for (int i = 0; i < 10; i++) {
  s_digit_bitmaps[i] = gbitmap_create_with_resource(DIGIT_RESOURCE_IDS[i]);
}
```

**Rectangular Display Layout** (main.c:109-121):
```c
// Calculate quadrant dimensions
int16_t quadrant_width = bounds.size.w / 2;   // 72px
int16_t quadrant_height = bounds.size.h / 2;  // 84px

// Create bitmap layers for 2x2 grid
s_hour_tens_layer = bitmap_layer_create(GRect(0, 0, quadrant_width, quadrant_height));
s_hour_ones_layer = bitmap_layer_create(GRect(quadrant_width, 0, quadrant_width, quadrant_height));
s_minute_tens_layer = bitmap_layer_create(GRect(0, quadrant_height, quadrant_width, quadrant_height));
s_minute_ones_layer = bitmap_layer_create(GRect(quadrant_width, quadrant_height, quadrant_width, quadrant_height));
```

**Round Display Layout** (main.c:91-107):
```c
int16_t padding = 10;
int16_t adjusted_width = (bounds.size.w - 2 * padding) / 2;
int16_t adjusted_height = (bounds.size.h - 2 * padding) / 2;

// Apply padding to all quadrants
s_hour_tens_layer = bitmap_layer_create(GRect(padding, padding, adjusted_width, adjusted_height));
// ... etc
```

### Why 2x2 Quadrant Layout?

**Benefits:**
- **Maximum digit size**: Each digit gets full quadrant space (72×84px)
- **Clean visual grid**: Natural 2×2 organization is instantly readable
- **Simple code**: 4 bitmap layers, straightforward positioning
- **No layout constraints**: Digits don't need to flow or wrap
- **Platform scalable**: Quadrant math works for any display size
- **12h format friendly**: Easy to hide hour tens digit

**Evolution of Layout:**
- **Original**: Font-based two-row layout with TextLayers
- **Optimization attempts**: Various font sizes (48pt → 71pt → 75pt)
- **Glyph size limits**: Hit 256-byte per-glyph SDK limit at larger sizes
- **Current**: Bitmap-based 2×2 quadrant layout
- **Result**: Maximum size possible with no SDK font limitations

## Optimization History

### Font-Based Approaches (Historical)

These approaches were tried with Pebble SDK font rendering before switching to bitmaps:

#### Attempt 1: Increase Font Size
**Goal**: Use 72pt or larger font
**Result**: ❌ Failed - glyph size exceeds 256 bytes
**Learning**: Hit SDK's hard 256-byte per-glyph limit

#### Attempt 2: Use Regular Weight for Larger Size
**Goal**: Try 75pt Regular to achieve larger visual size
**Result**: ⚠️ Partial - fits glyph limit but thinner strokes reduce readability
**Learning**: Weight vs size trade-off exists with font rendering

#### Attempt 3-5: Layout Optimizations
**Goal**: Various attempts to optimize spacing and centering with font-based rendering
**Result**: Mixed success - found optimal tracking (-4), vertical alignment, etc.
**Learning**: Font-based approach was hitting fundamental size limitations

#### Attempt 6: ExtraBold Font with Vertical Alignment
**Goal**: Prioritize font boldness; use vertical alignment
**Result**: ✅ Success but limited - 71pt ExtraBold was maximum achievable
**Learning**: Font rendering approach was constrained by SDK limits

### Bitmap-Based Approach (CURRENT)

#### Attempt 7: Switch to Pre-Rendered Bitmaps with 2x2 Quadrant Layout ✅
**Goal**: Eliminate SDK font size limits; achieve maximum digit size
**Result**: ✅ Complete Success
**Implementation**:
- 10 pre-rendered PNG bitmaps (digits 0-9)
- Generated from Atkinson Hyperlegible font at optimal size
- 2×2 quadrant grid layout (72×84px per digit on 144×168 displays)
- 4 BitmapLayers instead of TextLayers
- Platform-specific padding for round displays

**Benefits Achieved:**
- No glyph size limit (can make digits as large as needed)
- Consistent high-quality rendering across all platforms
- Simpler runtime code (no font rendering overhead)
- Maximum digit size: 72×84px per character
- Clean 2×2 visual grid that's instantly readable

**Trade-offs:**
- Fixed digit size (but optimal for Pebble displays)
- 10 bitmap resources (~8-10KB total)
- Cannot dynamically resize (not needed for this use case)

### What Works Now

✅ **Bitmap-based rendering**: No SDK font size limits
✅ **2×2 quadrant layout**: Maximum digit size, clean visual grid
✅ **72×84px per digit**: Optimal size for 144×168 displays
✅ **Platform-specific handling**: Padding for round, full quadrants for rectangular
✅ **Hidden hour tens in 12h**: Clean appearance for single-digit hours
✅ **Simple, maintainable code**: Straightforward bitmap layer positioning

### What Doesn't Work

❌ **Font-based rendering above 71pt**: Exceeds 256-byte glyph limit (historical issue)
❌ **Single bitmap for all digits**: Need individual bitmaps for each digit 0-9
❌ **No padding on round displays**: Causes clipping at curved edges
❌ **Dynamic digit sizing**: Bitmaps are fixed size (but this is optimal for our use case)

## Layout Reference Tables

### Quadrant Dimensions by Platform

| Platform | Display Size | Quadrant Size | Padding | Notes |
|----------|-------------|---------------|---------|-------|
| Aplite | 144×168 | 72×84 | None | Full quadrants |
| Basalt | 144×168 | 72×84 | None | Full quadrants |
| Diorite | 144×168 | 72×84 | None | Full quadrants |
| Emery | 200×228 | 100×114 | None | Larger quadrants |
| Chalk (Round) | 180×180 | 80×80 | 10px all sides | Prevents edge clipping |

### Bitmap Resource Specifications

| Resource | File | Dimensions | Format | Usage |
|----------|------|------------|--------|-------|
| DIGIT_0 | images/digit_0.png | ~60×75px | PNG-8/24 | Zero digit |
| DIGIT_1 | images/digit_1.png | ~60×75px | PNG-8/24 | One digit |
| ... | ... | ... | ... | ... |
| DIGIT_9 | images/digit_9.png | ~60×75px | PNG-8/24 | Nine digit |

**Note**: Actual bitmap dimensions are optimized for quadrant size while maintaining aspect ratio and legibility.

---

### Historical Reference: Font-Based Approach (Deprecated)

These tables document the font-based approach that was used before switching to bitmaps:

**Font Size Testing (Atkinson Hyperlegible Mono ExtraBold)**
- 71pt was maximum achievable before hitting 256-byte glyph limit
- 72pt+ exceeded SDK limits
- Led to decision to switch to bitmap approach for larger sizes

**Tracking Adjustment Testing**
- Optimal tracking was -4 for font-based rendering
- Not applicable to bitmap approach (spacing built into bitmap images)

## Development Workflow

### Building and Testing

**Prerequisites:**
- Nix package manager
- pebble.nix environment

**Build:**
```bash
cd ~/Developer/pebble-superledgible-watchface
nix-shell --run "pebble build"
```

**Test on Emulator:**
```bash
# Start basalt (Pebble Time) emulator
nix-shell --run "pebble install --emulator basalt"

# Test on other platforms:
nix-shell --run "pebble install --emulator aplite"   # Original Pebble
nix-shell --run "pebble install --emulator chalk"    # Round display
nix-shell --run "pebble install --emulator diorite"  # Pebble 2
nix-shell --run "pebble install --emulator emery"    # Pebble Time 2
```

**Install to Physical Watch:**
```bash
# First, ensure Pebble app is in Developer Mode with IP shown
nix-shell --run "pebble install --phone <IP_ADDRESS>"
```

**Testing Checklist:**
- [ ] Verify all digits 0-9 display without clipping
- [ ] Test at midnight (00:00 or 12:00)
- [ ] Test at various times to see different digit combinations
- [ ] Test on rectangular platforms (aplite, basalt, diorite, emery)
- [ ] Test on round platform (chalk)
- [ ] Verify 12h and 24h format switching

### Making Layout Changes

**To adjust quadrant dimensions:**

1. **For rectangular displays** - Edit `src/main.c` around lines 88-89:
   ```c
   int16_t quadrant_width = bounds.size.w / 2;   // Currently 72px on 144×168
   int16_t quadrant_height = bounds.size.h / 2;  // Currently 84px on 144×168
   ```

2. **For round displays** - Edit `src/main.c` around line 93:
   ```c
   int16_t padding = 10;  // Adjust padding value
   ```

3. **Test thoroughly** - check for clipping on all platforms

4. **Automated screenshot testing**:
   ```bash
   # Build and install
   nix-shell --run "pebble build && pebble install --emulator basalt"

   # Capture screenshot with Peekaboo
   sleep 1 && peekaboo image --app "qemu-pebble" --path screenshots/watchface.png

   # View the screenshot
   open screenshots/watchface.png
   ```

**To change digit appearance:**

1. **Regenerate bitmap images** - Would need external tool to render Atkinson Hyperlegible font to PNG
2. **Replace files** in `resources/images/digit_0.png` through `digit_9.png`
3. **Rebuild and test** - verify new bitmaps display correctly

**To adjust digit positioning within quadrants:**

1. Currently digits fill entire quadrant space
2. To add margins, would need to regenerate bitmaps at smaller size
3. Or add custom positioning logic in BitmapLayer creation

### Common Tasks for Claude Code

When the user says:
- **"Make digits larger"** → Would require regenerating bitmap images at larger size; current size is optimized for quadrant dimensions
- **"Change font"** → Would require regenerating all 10 digit bitmaps with new font
- **"Adjust spacing"** → For bitmap approach, spacing is baked into images; would need to regenerate bitmaps
- **"Add padding on rectangular"** → Adjust quadrant dimensions in main.c (currently using full width/height)
- **"Fix round display clipping"** → Adjust padding value in `#ifdef PBL_ROUND` section (currently 10px)
- **"Build and test"** → Use nix-shell with pebble CLI: `nix-shell --run "pebble build && pebble install --emulator basalt"`
- **"Different platform"** → Use `--emulator <platform>` flag (aplite, basalt, chalk, diorite, emery)
- **"Take a screenshot"** → Use Peekaboo: `peekaboo image --app "qemu-pebble" --path screenshots/watchface.png`
- **"Test 12h format"** → Toggle Pebble system time format in emulator settings
- **"Regenerate bitmaps"** → Would need external tool to render Atkinson Hyperlegible font to PNG images

## Known Issues and Gotchas

### 1. Bitmap Resources Must Be Present
**Symptom**: Build error about missing resources or blank digits on display
**Cause**: Missing digit bitmap files in `resources/images/`
**Solution**: Ensure all files digit_0.png through digit_9.png exist
**Prevention**: Keep all 10 bitmap files in version control

### 2. Round Display Edge Clipping
**Symptom**: Digits cut off at curved edges on Chalk (round display)
**Cause**: Insufficient padding for round display
**Solution**: Adjust padding value in `#ifdef PBL_ROUND` section (currently 10px)
**Prevention**: Test on chalk emulator after layout changes

### 3. Platform-Specific Behavior
**Symptom**: Layout looks different on chalk (round) vs basalt (rectangular)
**Cause**: Round displays use padding; rectangular use full quadrants
**Solution**: Already implemented with `#ifdef PBL_ROUND`
**Prevention**: Test on both rectangular and round emulators

### 4. Time Format Detection
**Symptom**: Watchface shows 24h when expecting 12h (or vice versa)
**Cause**: Watchface automatically detects system time format preference
**Solution**: Change time format in Pebble settings (not watchface settings)
**Prevention**: Document that format is auto-detected, not configurable

### 5. Hour Tens Not Hidden in 12h Format
**Symptom**: Leading zero shows for single-digit hours (e.g., "02:30" instead of "2:30")
**Cause**: Missing or incorrect logic in `update_time()` function
**Solution**: Verify lines 58-64 in main.c properly hide hour_tens layer
**Prevention**: Test with various times in 12h format (1:00, 2:30, 11:45, 12:00)

### 6. Bitmap Size Doesn't Match Quadrant
**Symptom**: Digits appear too small, too large, or cut off
**Cause**: Bitmap images not optimized for quadrant dimensions
**Solution**: Regenerate bitmaps at appropriate size for target quadrant (72×84px for standard displays)
**Prevention**: Design bitmaps to fit within smallest target quadrant with some margin

## Future Optimization Ideas

### If Pebble SDK Changes

**If glyph size limit is increased:**
- Try 72pt, 73pt, or 74pt ExtraBold
- May achieve even larger, more readable display
- Would need to test h_inset values again

**If font rendering improves:**
- Revisit vertical centering with insets
- May be able to achieve better positioning

### Alternative Approaches Considered

**1. Custom Font Subset**
- **Idea**: Create font file with only digits 0-9 to reduce glyph size
- **Status**: Already doing this with `characterRegex: "[0-9]"`
- **Impact**: Minimal; glyph size is per-character, not total

**2. Vector Graphics Instead of Font**
- **Idea**: Draw digits as vector paths instead of using font
- **Pros**: No glyph size limit
- **Cons**: Much more complex, harder to maintain, loses Atkinson Hyperlegible design
- **Verdict**: Not worth the effort

**3. Two-Digit Display (HH:MM format)**
- **Idea**: Show "12:34" as two two-digit numbers instead of four single digits
- **Pros**: Simpler layout
- **Cons**: Loses visual impact of quadrant design; harder to optimize spacing
- **Verdict**: Current four-digit approach is better

**4. Variable h_inset Based on Platform**
- **Idea**: Use different h_inset values for different screen sizes (144px vs 200px)
- **Pros**: Could optimize for each platform individually
- **Cons**: More complex, harder to maintain
- **Verdict**: Could revisit if supporting more platforms

## Appendix: Error Messages and Solutions

### "Resource not found: RESOURCE_ID_DIGIT_X"
- **Cause**: Missing bitmap resource definition or file
- **Solution**: Verify appinfo.json includes all digit resources (DIGIT_0 through DIGIT_9)
- **Prevention**: Keep all bitmap definitions in appinfo.json

### Blank/Missing Digits on Display
- **Cause**: Bitmap file missing or corrupted, or bitmap not loaded
- **Solution**: Check resources/images/ has all digit_*.png files; verify bitmap loading in main_window_load()
- **Prevention**: Test after any resource changes

### Round Display Clipping at Edges
- **Cause**: Insufficient padding for round display
- **Solution**: Increase padding value in `#ifdef PBL_ROUND` section
- **Prevention**: Always test on chalk emulator

### Wrong Time Format (12h vs 24h)
- **Cause**: Pebble system setting
- **Solution**: Change time format in Pebble settings (not watchface)
- **Prevention**: Document that format is auto-detected

### Build Fails with "Resource file not found"
- **Cause**: Bitmap files not in correct location
- **Solution**: Ensure all digit_*.png files are in resources/images/
- **Prevention**: Keep resource directory structure intact

---

**Last Updated**: 2025-10-30
**Version**: 3.0 (Bitmap-based 2×2 quadrant layout)
**Maintainer**: Dan Hart
**Claude Code**: This file is optimized for Claude Code assistance

## Changelog

### 2025-10-30 v3.0 - Bitmap-Based 2×2 Quadrant Layout (CURRENT)
- **Major architectural change**: Switched from font-based TextLayers to bitmap-based BitmapLayers
- Implemented clean **2×2 quadrant grid** with 4 individual digit displays
- **10 pre-rendered bitmap images** (digit_0.png through digit_9.png) generated from Atkinson Hyperlegible font
- Eliminated SDK font size limitations (no more 256-byte glyph limit)
- **72×84px per digit** on 144×168 displays (maximum achievable size)
- Platform-specific handling: full quadrants for rectangular, 10px padding for round
- 12h format intelligently hides hour tens digit for single-digit hours
- Comprehensive documentation update to reflect bitmap approach

### 2025-10-30 v2.2 - Maximum Tight Centering + Screenshot Automation (Historical)
- Font-based approach: 71pt ExtraBold with vertical alignment
- Increased `font_approx_height` to 105px for maximum tight centering
- Added Peekaboo screenshot automation workflow
- **Superseded by v3.0 bitmap approach**

### 2025-10-30 v2.1 - Tighter Vertical Centering (Historical)
- Font-based approach: Adjusted vertical positioning
- **Superseded by v3.0 bitmap approach**

### 2025-10-30 v2.0 - ExtraBold with Vertical Alignment (Historical)
- Font-based approach: 71pt ExtraBold (maximum size within glyph limit)
- Implemented vertical alignment positioning
- **Superseded by v3.0 bitmap approach**

### 2025-10-30 v1.0 - Initial Documentation (Historical)
- Font-based approach: 75pt Regular font configuration
- **Superseded by v3.0 bitmap approach**
