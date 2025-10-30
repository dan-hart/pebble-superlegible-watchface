# CLAUDE.md

This file provides guidance to Claude Code when working with the Pebble Superledgible watchface project.

## Project Overview

**Superledgible** is a minimalist Pebble watchface focused on maximum readability using the Atkinson Hyperlegible font. The design philosophy is simple: display the time as large as possible with maximum legibility, nothing else.

**Key Features:**
- Two-row time display (HH on top, MM on bottom)
- Atkinson Hyperlegible Mono font for exceptional readability
- Automatic 12h/24h format detection (no leading zero for 12h hours)
- Universal support for all 5 Pebble platforms
- Platform-specific optimization (larger fonts on rectangular displays)
- Battery efficient (updates once per minute)

## Technical Constraints

### Critical Pebble SDK Limits

#### 1. Glyph Size Limit: 256 Bytes (Hard Limit)
The Pebble SDK imposes a **maximum glyph size of 256 bytes** per character when loading custom fonts. This is not a warning—it's a hard constraint that will cause build failures.

**Implications:**
- Font size and weight combinations must stay under 256 bytes per digit
- ExtraBold weight at 72pt = 263 bytes (exceeds limit)
- ExtraBold weight at 71pt = ~253 bytes (works)
- Regular weight allows slightly larger sizes but looks thinner

**Error Message:**
```
Exception: Glyph too large! codepoint 48: 263 > 256
```

#### 2. Maximum Achievable Font Size

**For Rectangular Displays (Current Configuration):**
- **71pt Atkinson Hyperlegible Mono ExtraBold**
- Results in glyphs approximately 95px tall
- Stays safely under 256-byte glyph limit (~253 bytes)
- Bold strokes provide maximum readability and legibility

**For Round Displays (Chalk):**
- Can use smaller font size if needed for text flow
- Platform-specific configuration via `#ifdef PBL_ROUND`

**Glyph Size Limits by Weight:**
- **ExtraBold**: 71pt maximum (72pt = 263 bytes, exceeds limit)
- **Regular**: 75pt maximum (76pt = 265 bytes, exceeds limit)
- **80pt**: Exceeds limit for all weights (294 bytes for Regular)

#### 3. Platform Display Resolutions

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
> While the watchface must support all platforms, rectangular displays (aplite, basalt, diorite, emery) represent the majority of Pebble devices and should be optimized for maximum font size and readability. Use platform-specific code (`#ifdef PBL_ROUND`) to provide appropriate handling for circular displays without compromising rectangular display performance. The rectangular displays should always use the largest possible font size that fits within the 256-byte glyph limit.

### Font Rendering Characteristics

#### Font Baseline Behavior
The 71pt ExtraBold font has specific rendering characteristics:
- Digits sit **high** in their bounding box due to font baseline
- Font height (≈95px) fits well within vertical space on all displays
- Two-row layout with vertical alignment brings time closer to center
- Center alignment handles single-digit hours in 12h format

**Two-Row Layout with Vertical Alignment:**
```
Example with 71pt font on 144×168 display:
- Half height = 84px (midpoint)
- Font height = 105px (used for positioning - oversized for tight centering)
- Hours: positioned at bottom of top half (y = 84 - 105 = -21)
- Minutes: positioned at top of bottom half (y = 84)
- This brings HH and MM very close together with minimal gap
- Full-width rows (144px) provide ample horizontal space
- Center alignment automatically handles variable digit widths
```

**Solution:**
Two-row layout with vertical alignment positioning and center horizontal alignment.

#### Monospace Digit Width
For 71pt ExtraBold:
- Approximate digit width: 60-70% of height
- Height ≈ 95px → Width ≈ 57-67px
- Tracking adjustment of -4 brings digits closer together
- Monospace ensures all digits have identical width
- Bold strokes enhance readability at this size

## Current Optimal Configuration

### Font Settings (appinfo.json)

```json
{
  "type": "font",
  "name": "FONT_ATKINSON_MONO_EXTRABOLD_71",
  "file": "fonts/AtkinsonHyperlegibleMono-ExtraBold.ttf",
  "targetSize": 71,
  "characterRegex": "[0-9]",
  "trackingAdjust": -4
}
```

**Why These Values:**
- **71pt**: Maximum size under glyph limit for ExtraBold weight (~253 bytes / 256 bytes max)
- **ExtraBold weight**: Boldest monospace font for maximum readability and legibility
- **targetSize: 71**: Explicit size specification for consistency
- **trackingAdjust: -4**: Tightest spacing without digit overlap
- **[0-9] only**: Reduces memory usage (only need digits)

### Layout Parameters (main.c)

**Rectangular Displays** (aplite, basalt, diorite, emery):
```c
int16_t half_height = bounds.size.h / 2;
int16_t font_approx_height = 105;  // Oversized for maximum tight centering

// Vertically-aligned two-row layout:
// - Hours: bottom-aligned in top half
//   y = half_height - font_height (brings hours down to meet center)
// - Minutes: top-aligned in bottom half
//   y = half_height (starts right at center)
// This minimizes gap between HH and MM

// For 144×168 display:
// - Hours:   x=0, y=-21, w=144, h=105 (bottom-aligned in top half)
// - Minutes: x=0, y=84,  w=144, h=105 (top-aligned in bottom half)

// Text is horizontally center-aligned within each full-width row
// Single-digit hours (12h format) are automatically centered
```

**Round Display** (chalk):
```c
int16_t padding = 10;  // uniform padding

// Two-row layout with padding:
// - Top row: x=padding, y=padding, w=bounds.size.w - 2*padding, h=half_height - padding
// - Bottom row: x=padding, y=half_height, w=bounds.size.w - 2*padding, h=half_height - padding

// Enable text flow for edge wrapping:
text_layer_enable_screen_text_flow_and_paging(layer, 5);
```

### Why Two-Row Layout?

**Benefits:**
- **Simpler code**: 2 text layers instead of 4
- **Natural digit pairing**: HH and MM are visually grouped
- **Maximum horizontal space**: Full display width (144px) for each row
- **Automatic centering**: Single-digit hours in 12h format center automatically
- **Font tracking handles spacing**: -4 tracking brings digits in each pair close together
- **Larger fonts possible**: More vertical space allows for taller fonts

**Evolution of Layout:**
- **Original**: 4 separate single-digit layers with h_inset optimization
- **Intermediate**: 2 two-digit layers with full-width rows, 75pt Regular
- **Current**: 2 two-digit layers with vertical alignment, 71pt ExtraBold
- **Result**: Bolder, more readable font with time centered vertically

## Optimization History

### What Was Tried

#### Attempt 1: Increase Font Size
**Goal**: Use 72pt or larger font
**Result**: ❌ Failed - glyph size exceeds 256 bytes
```
Error: Glyph too large! codepoint 48: 263 > 256
```
**Learning**: 71pt is the hard maximum for ExtraBold weight

#### Attempt 2: Use Regular Weight for Larger Size
**Goal**: Try 75pt Regular to achieve larger visual size
**Result**: ⚠️ Partial - fits glyph limit but thinner strokes reduce readability
**Learning**: Weight vs size trade-off exists, but was later reconsidered
**Status**: Superseded by Attempt 6

#### Attempt 3: Asymmetric Vertical Insets for Centering
**Goal**: Use asymmetric vertical insets (6px top, 18px bottom) to center digits better
**Result**: ❌ Failed - caused clipping at bottom of digits (MM digits cut off)
**Learning**: Font baseline causes digits to sit high; vertical insets reduce available height below what's needed

#### Attempt 4: Aggressive Tracking Adjustment
**Goal**: Test tracking values from -3 to -5
**Result**: ✅ Success - tracking of -4 provides tight spacing without overlap
**Learning**: -3 still had noticeable gaps; -5 risked overlap; -4 is optimal

#### Attempt 5: Horizontal Insets Only
**Goal**: Reduce box width to bring digits closer horizontally while maintaining full vertical height
**Result**: ✅ Success - tested h_inset values from 8px to 16px
**Learning**: Horizontal optimization is safe; vertical optimization causes clipping
**Status**: Superseded by Attempt 6 which uses full-width rows

#### Attempt 6: ExtraBold Font with Vertical Alignment (CURRENT)
**Goal**: Prioritize font boldness for readability; use vertical alignment to center time
**Result**: ✅ Success - 71pt ExtraBold with hours bottom-aligned and minutes top-aligned
**Learning**: Bold weight is more important than size for readability; vertical alignment eliminates gap between HH and MM without clipping
**Implementation**:
- Font: 71pt ExtraBold (vs previous 75pt Regular)
- Hours: y = half_height - font_height (bottom-aligned in top half)
- Minutes: y = half_height (top-aligned in bottom half)
- Full-width rows (no h_inset needed)
- Result: Maximum boldness with centered time display

### What Works

✅ **ExtraBold at 71pt**: Maximum size within glyph limit, excellent readability with bold strokes
✅ **Tracking adjustment of -4**: Tight, visually appealing spacing
✅ **Vertical alignment positioning**: Hours at bottom of top half, minutes at top of bottom half
✅ **Full-width rows**: Provides maximum horizontal space, no h_inset needed
✅ **Platform-specific handling**: Round vs rectangular optimization
✅ **Center horizontal alignment**: Works perfectly with full-width rows and variable-width hours (12h format)

### What Doesn't Work

❌ **Fonts larger than 71pt ExtraBold**: Exceeds 256-byte glyph limit
❌ **Asymmetric vertical insets**: Causes clipping with tall fonts
❌ **Regular weight at 75pt+**: Exceeds glyph limit (280 bytes); also less readable than smaller ExtraBold
❌ **Tracking tighter than -4**: Risk of digit overlap
❌ **Simple centered layout**: Leaves large gap between hours and minutes
❌ **Same layout for round and rectangular**: Round displays need special handling

## Layout Reference Tables

### Horizontal Inset Testing (144×168 Rectangular Displays)

**Note**: Current configuration uses full-width rows (h_inset = 0) with vertical alignment instead of horizontal insets.

| h_inset | Box Width | Per-Digit Shift | Total Shift (4 digits) | Tested | Result |
|---------|-----------|-----------------|------------------------|--------|--------|
| **0px** | **144px (full)** | **0px** | **0px** | ✅ Yes | ✅ **Current - full width** |
| 8px | 128px | 4px | 16px | ✅ Yes | ✅ Conservative (deprecated) |
| 10px | 124px | 5px | 20px | ✅ Yes | ✅ Moderate (deprecated) |
| 16px | 112px | 8px | 32px | ✅ Yes | ⚠️ Aggressive (deprecated) |
| 18px | 108px | 9px | 36px | ❌ No | ⚠️ Untested - may be too tight |

### Font Size Testing (Atkinson Hyperlegible Mono ExtraBold)

| Size | Glyph Size (bytes) | Height (approx) | Width (approx) | Result |
|------|-------------------|-----------------|----------------|--------|
| 70pt | ~245 bytes | 93px | 56-65px | ✅ Works |
| **71pt** | **~253 bytes** | **95px** | **57-67px** | ✅ **Optimal (current)** |
| 72pt | 263 bytes | 97px | 58-68px | ❌ Exceeds glyph limit |
| 75pt | ~280 bytes | 101px | 61-71px | ❌ Exceeds glyph limit |

### Tracking Adjustment Testing

| Tracking | Visual Appearance | Digit Spacing | Result |
|----------|------------------|---------------|--------|
| 0 (default) | Wide gaps | Comfortable | Too much empty space |
| -2 | Moderate gaps | Reduced | Still noticeable gaps |
| -3 | Small gaps | Tight | Better but improvable |
| **-4** | **Minimal gaps** | **Very tight** | ✅ **Optimal (current)** |
| -5 | No gaps | Risk of overlap | ⚠️ Too aggressive |

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

**To adjust vertical alignment:**

1. **Edit `src/main.c`** around line 71:
   ```c
   int16_t font_approx_height = 105;  // Adjust this value
   ```

2. **Safe ranges:**
   - **95-105px**: Safe range for 71pt ExtraBold (current: 105px for maximum tight centering)
   - Increase to bring time closer together (tighter gap)
   - Decrease to add more gap between hours and minutes
   - 105px provides optimal tight centering with minimal gap

3. **Test thoroughly** - check for clipping on all platforms

4. **Automated screenshot testing** (optional):
   ```bash
   # Build and install
   nix-shell --run "pebble build && pebble install --emulator basalt"

   # Capture screenshot with Peekaboo
   sleep 1 && peekaboo image --app "qemu-pebble" --path /tmp/watchface.png

   # View the screenshot
   open /tmp/watchface.png
   ```

**To adjust font size:**

1. **Check glyph size first** - 71pt ExtraBold is the maximum
2. **Edit `appinfo.json`** - change font name, file, and size
3. **Update `src/main.c` line 65** - update resource ID to match
4. **Rebuild and test immediately** - glyph limit errors appear at build time

**To adjust tracking:**

1. **Edit `appinfo.json`** line 19:
   ```json
   "trackingAdjust": -4  // Change this value
   ```

2. **Safe ranges:**
   - **0 to -3**: Safe but more spacing
   - **-4**: Current optimal
   - **-5 or lower**: Risk of overlap

### Common Tasks for Claude Code

When the user says:
- **"Test larger font"** → Check glyph size limit (256 bytes max); 71pt ExtraBold is the maximum
- **"Move time closer to center"** → Adjust `font_approx_height` value (currently 105px for maximum tight centering)
- **"Add more gap"** → Decrease `font_approx_height` (try 95-100px)
- **"Make font bolder"** → Already using ExtraBold (boldest available monospace)
- **"Vertical centering issue"** → Adjust vertical alignment positioning via `font_approx_height`
- **"Build and test"** → Use nix-shell with pebble CLI
- **"Different platform"** → Use `--emulator <platform>` flag
- **"Make digits larger"** → Explain 71pt is maximum due to glyph limit for ExtraBold weight
- **"Take a screenshot"** → Use Peekaboo: `peekaboo image --app "qemu-pebble" --path /tmp/watchface.png`

## Known Issues and Gotchas

### 1. Glyph Size Limit is Hard
**Symptom**: Build error "Glyph too large! codepoint XX: XXX > 256"
**Cause**: Font size + weight combination exceeds 256-byte limit
**Solution**: Use 71pt ExtraBold (maximum safe size)
**Prevention**: Don't exceed 71pt for ExtraBold weight

### 2. Vertical Positioning and Clipping
**Symptom**: Top or bottom of digits cut off on display
**Cause**: Incorrect `font_approx_height` value or positioning calculation
**Solution**: Adjust `font_approx_height` to optimal value (105px for maximum tight centering)
**Prevention**: Use safe height values (95-105px range) and test on all platforms; use Peekaboo for automated screenshot verification

### 3. Font Baseline Positioning
**Symptom**: Digits appear to sit high in their boxes
**Cause**: Font baseline metrics cause vertical positioning quirks
**Solution**: Accept the positioning; it's a font characteristic, not a bug
**Prevention**: Use center text alignment to minimize visual impact

### 4. Platform-Specific Behavior
**Symptom**: Layout looks different on chalk (round) vs basalt (rectangular)
**Cause**: Round displays need padding and text flow
**Solution**: Already implemented with `#ifdef PBL_ROUND`
**Prevention**: Test on both rectangular and round emulators

### 5. Tracking Affects Spacing
**Symptom**: Changing tracking makes digits wider or narrower
**Cause**: Tracking adjustment changes horizontal spacing between character strokes
**Solution**: Adjust `h_inset` if tracking changes significantly
**Prevention**: Test digit width when changing tracking values

### 6. Time Format Detection
**Symptom**: Watchface shows 24h when expecting 12h (or vice versa)
**Cause**: Watchface automatically detects system time format preference
**Solution**: Change time format in Pebble settings (not watchface settings)
**Prevention**: Document that format is auto-detected, not configurable

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

### "Glyph too large! codepoint XX: XXX > 256"
- **Cause**: Font size + weight exceeds glyph size limit
- **Solution**: Use 71pt ExtraBold (maximum safe size)
- **Prevention**: Don't exceed 71pt for ExtraBold weight

### Digits Clipped at Top or Bottom
- **Cause**: Incorrect `font_approx_height` value
- **Solution**: Adjust `font_approx_height` to match actual font dimensions
- **Prevention**: Use conservative height estimates and test on all platforms

### Digits Overlapping
- **Cause**: Tracking too tight (more negative than -4)
- **Solution**: Reduce tracking (make less negative, e.g., from -5 to -4)
- **Prevention**: Test with all digits 0-9 after tracking changes; -4 is optimal

### Round Display Clipping at Edges
- **Cause**: Missing text flow or insufficient padding
- **Solution**: Verify `text_layer_enable_screen_text_flow_and_paging()` is called
- **Prevention**: Always test on chalk emulator

### Wrong Time Format (12h vs 24h)
- **Cause**: Pebble system setting
- **Solution**: Change time format in Pebble settings (not watchface)
- **Prevention**: Document that format is auto-detected

---

**Last Updated**: 2025-10-30
**Version**: 2.2 (Maximum tight centering + screenshot automation)
**Maintainer**: Dan Hart
**Claude Code**: This file is optimized for Claude Code assistance

## Changelog

### 2025-10-30 v2.2 - Maximum Tight Centering + Screenshot Automation
- Increased `font_approx_height` from 95px to **105px** for maximum tight centering
- Hours now positioned at y=-21, bringing rows significantly closer together
- Added **Peekaboo screenshot automation** workflow for visual testing
- Documented automated testing process: build → install → capture → verify

### 2025-10-30 v2.1 - Tighter Vertical Centering
- Increased `font_approx_height` from 90px to **95px** for minimal gap
- Hours and minutes now positioned closer together for better symmetry around center
- Matches actual font height for optimal vertical centering

### 2025-10-30 v2.0 - ExtraBold with Vertical Alignment
- Switched from 75pt Regular to **71pt ExtraBold** for maximum readability
- Implemented **vertical alignment**: hours bottom-aligned in top half, minutes top-aligned in bottom half
- Removed horizontal insets (h_inset); now using full-width rows
- Time display now centered vertically with minimal gap between HH and MM
- Bold strokes significantly improve legibility at slightly smaller size

### 2025-10-30 v1.0 - Initial Documentation
- Documented 75pt Regular font configuration
- Two-row layout with full-width rows
- Initial optimization guidelines
