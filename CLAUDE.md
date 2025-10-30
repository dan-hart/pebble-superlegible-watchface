# CLAUDE.md

This file provides guidance to Claude Code when working with the Pebble Superledgible watchface project.

## Project Overview

**Superledgible** is a minimalist Pebble watchface focused on maximum readability using the Atkinson Hyperlegible font. The design philosophy is simple: display the time as large as possible with maximum legibility, nothing else.

**Key Features:**
- Four-digit time display using quadrant layout (2×2 grid)
- Atkinson Hyperlegible Mono font for exceptional readability
- Automatic 12h/24h format detection
- Universal support for all 5 Pebble platforms
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
Through testing, the maximum viable configuration is:
- **71pt Atkinson Hyperlegible Mono ExtraBold**
- Results in glyphs approximately 95px tall
- Monospace digit width approximately 57-67px
- Stays safely under 256-byte glyph limit

**Why Not Larger:**
- 72pt ExtraBold = 263 bytes (exceeds limit)
- 75pt Regular = exceeds glyph limit (280 bytes)
- 80pt+ = glyph limit exceeded regardless of weight

#### 3. Platform Display Resolutions

| Platform | Resolution | Aspect Ratio | Shape |
|----------|-----------|--------------|-------|
| Aplite (Pebble) | 144×168 | Portrait | Rectangular |
| Basalt (Time) | 144×168 | Portrait | Rectangular |
| Diorite (Pebble 2) | 144×168 | Portrait | Rectangular |
| Emery (Time 2) | 200×228 | Portrait | Rectangular |
| Chalk (Time Round) | 180×180 | Square | Round |

**Impact on Layout:**
- Rectangular displays use quadrant optimization (h_inset)
- Round display requires padding and text flow
- All platforms share the same font resource (must work for all)

### Font Rendering Characteristics

#### Font Baseline Behavior
The 71pt ExtraBold font has specific rendering characteristics:
- Digits sit **high** in their bounding box due to font baseline
- Using asymmetric vertical insets causes **clipping at the bottom**
- Horizontal-only insets are safe and effective

**Why Vertical Insets Don't Work:**
```
Example with 71pt font on 144×168 display:
- Half height = 84px per quadrant
- Font height ≈ 95px (taller than quadrant)
- Adding vertical inset (e.g., v_inset=10) reduces box to 74px
- Result: Bottom of digits get clipped
```

**Solution:**
Use horizontal insets only to maintain full vertical height.

#### Monospace Digit Width
For 71pt ExtraBold:
- Approximate digit width: 60-70% of height
- Height ≈ 95px → Width ≈ 57-67px
- Tracking adjustment of -4 brings digits even closer

## Current Optimal Configuration

### Font Settings (appinfo.json)

```json
{
  "type": "font",
  "name": "FONT_ATKINSON_MONO_EXTRABOLD_71",
  "file": "fonts/AtkinsonHyperlegibleMono-ExtraBold.ttf",
  "characterRegex": "[0-9]",
  "trackingAdjust": -4
}
```

**Why These Values:**
- **71pt**: Maximum size under glyph limit (256 bytes)
- **ExtraBold**: Maximum weight for maximum readability
- **trackingAdjust: -4**: Tightest spacing without digit overlap
- **[0-9] only**: Reduces memory usage (only need digits)

### Layout Parameters (main.c)

**Rectangular Displays** (aplite, basalt, diorite, emery):
```c
int16_t h_inset = 16;  // horizontal inset

// Quadrant calculations:
// - Box width: half_width - h_inset
//   - For 144px wide: 72 - 16 = 56px per digit
// - Box height: half_height (full vertical space)
//   - For 168px tall: 84px per quadrant

// Positioning:
// Top-left (hour tens):      x=16,  y=0,   w=56, h=84
// Top-right (hour ones):     x=72,  y=0,   w=56, h=84
// Bottom-left (minute tens):  x=16,  y=84,  w=56, h=84
// Bottom-right (minute ones): x=72,  y=84,  w=56, h=84
```

**Round Display** (chalk):
```c
int16_t padding = 10;  // uniform padding

// Reduced quadrant size with padding:
half_width = (bounds.size.w - 2 * padding) / 2;
half_height = (bounds.size.h - 2 * padding) / 2;

// Enable text flow for edge wrapping:
text_layer_enable_screen_text_flow_and_paging(layer, 5);
```

### Why h_inset = 16?

| h_inset | Box Width (144×168) | Horizontal Shift | Safety | Notes |
|---------|---------------------|------------------|--------|-------|
| 0px | 72px | 0px (baseline) | ✅ Safe | Full quadrants, digits far apart |
| 8px | 64px | 16px closer | ✅ Safe | Conservative optimization |
| 10px | 62px | 20px closer | ✅ Works | Moderate compression |
| 12px | 60px | 24px closer | ⚠️ Edge | Approaching limit |
| 14px | 58px | 28px closer | ⚠️ Risk | High compression |
| **16px** | **56px** | **32px closer** | ⚠️ **Aggressive** | **Current setting - works but tight** |
| 18px | 54px | 36px closer | ❌ Risk | May cause overlap/clipping |

**Rationale for 16px:**
- Brings time digits significantly closer to center
- 56px box width accommodates 57-67px digit width with tight tracking (-4)
- Maximizes visual impact on small display
- Tested and verified with all digits 0-9
- No clipping or overlap observed

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
**Result**: ⚠️ Partial - fits glyph limit but thinner, may clip on small displays
**Learning**: Weight vs size trade-off; ExtraBold preferred for readability

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

### What Works

✅ **ExtraBold at 71pt**: Maximum size within glyph limit, excellent readability
✅ **Tracking adjustment of -4**: Tight, visually appealing spacing
✅ **Horizontal insets (h_inset=8 to 16)**: Brings digits closer to center
✅ **Full vertical height**: No vertical insets prevents clipping
✅ **Platform-specific handling**: Round vs rectangular optimization
✅ **Center text alignment**: Works well with reduced box width

### What Doesn't Work

❌ **Fonts larger than 71pt ExtraBold**: Exceeds 256-byte glyph limit
❌ **Asymmetric vertical insets**: Causes clipping with tall fonts
❌ **Regular weight at 75pt+**: Exceeds glyph limit (280 bytes)
❌ **Tracking tighter than -4**: Risk of digit overlap
❌ **h_inset > 16px**: Box width becomes too narrow for digit width
❌ **Same layout for round and rectangular**: Round displays need special handling

## Layout Reference Tables

### Horizontal Inset Testing (144×168 Rectangular Displays)

| h_inset | Box Width | Per-Digit Shift | Total Shift (4 digits) | Tested | Result |
|---------|-----------|-----------------|------------------------|--------|--------|
| 0px | 72px | 0px | 0px | ✅ Yes | ✅ Safe baseline |
| 8px | 64px | 4px | 16px | ✅ Yes | ✅ Conservative improvement |
| 10px | 62px | 5px | 20px | ✅ Yes | ✅ Moderate compression |
| 16px | 56px | 8px | 32px | ✅ Yes | ⚠️ Aggressive (current) |
| 18px | 54px | 9px | 36px | ❌ No | ⚠️ Untested - may be too tight |

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

**To adjust horizontal spacing:**

1. **Edit `src/main.c`** line 110:
   ```c
   int16_t h_inset = 16;  // Change this value
   ```

2. **Safe ranges:**
   - **0-10px**: Conservative (safe)
   - **11-16px**: Aggressive (current range)
   - **17+px**: High risk (untested)

3. **Test thoroughly** - check all digits 0-9

**To adjust font size:**

1. **Check glyph size first** - 71pt ExtraBold is the maximum
2. **Edit `appinfo.json`** - change font name, file, and size
3. **Update `src/main.c` line 78** - update resource ID to match
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
- **"Move digits closer"** → Adjust `h_inset` value (currently 16px, range 0-18px)
- **"Vertical centering issue"** → Remind about font baseline problems; avoid vertical insets
- **"Build and test"** → Use nix-shell with pebble CLI
- **"Different platform"** → Use `--emulator <platform>` flag
- **"Make digits larger"** → Explain 71pt is maximum due to glyph limit

## Known Issues and Gotchas

### 1. Glyph Size Limit is Hard
**Symptom**: Build error "Glyph too large! codepoint XX: XXX > 256"
**Cause**: Font size + weight combination exceeds 256-byte limit
**Solution**: Use 71pt ExtraBold (maximum safe size)
**Prevention**: Don't exceed 71pt for ExtraBold weight

### 2. Asymmetric Insets Cause Clipping
**Symptom**: Bottom of digits cut off on display (MM digits clipped)
**Cause**: Vertical insets reduce box height below font height; font baseline positioning
**Solution**: Use horizontal insets only (`h_inset`); maintain full vertical height
**Prevention**: Never reduce quadrant height with vertical insets for tall fonts

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

### Digits Clipped at Bottom (MM digits cut off)
- **Cause**: Vertical insets reducing box height
- **Solution**: Remove vertical insets; use horizontal insets only
- **Prevention**: Never reduce quadrant height with tall fonts

### Digits Overlapping
- **Cause**: Tracking too tight or h_inset too large
- **Solution**: Reduce tracking (make less negative) or reduce h_inset
- **Prevention**: Test with all digits 0-9 after layout changes

### Round Display Clipping at Edges
- **Cause**: Missing text flow or insufficient padding
- **Solution**: Verify `text_layer_enable_screen_text_flow_and_paging()` is called
- **Prevention**: Always test on chalk emulator

### Wrong Time Format (12h vs 24h)
- **Cause**: Pebble system setting
- **Solution**: Change time format in Pebble settings (not watchface)
- **Prevention**: Document that format is auto-detected

---

**Last Updated**: 2025-10-30 (initial documentation)
**Maintainer**: Dan Hart
**Claude Code**: This file is optimized for Claude Code assistance
