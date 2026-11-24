#include <pebble.h>

// Screenshot mode - uncomment and set time for screenshots
// Format: SCREENSHOT_TIME_24H 1 for 24h mode, 0 for 12h mode
// Format: SCREENSHOT_HOUR (0-23 for 24h, 1-12 for 12h)
// Format: SCREENSHOT_MINUTE (0-59)
// #define SCREENSHOT_MODE
// #define SCREENSHOT_TIME_24H 1
// #define SCREENSHOT_HOUR 23
// #define SCREENSHOT_MINUTE 59

// UI Elements - 4 BitmapLayers for individual digits
static Window *s_main_window;
static BitmapLayer *s_hour_tens_layer;
static BitmapLayer *s_hour_ones_layer;
static BitmapLayer *s_minute_tens_layer;
static BitmapLayer *s_minute_ones_layer;

// Bitmaps for digits 0-9
static GBitmap *s_digit_bitmaps[10];

typedef struct {
  GColor digits;
  GColor background;
} Palette;

enum { PERSIST_PALETTE = 1 };
static Palette s_palette;

static bool palette_is_valid(Palette palette) {
  if (palette.digits.a != 3 || palette.background.a != 3 ||
      gcolor_equal(palette.digits, palette.background)) {
    return false;
  }
#ifdef PBL_BW
  return (gcolor_equal(palette.digits, GColorWhite) && gcolor_equal(palette.background, GColorBlack)) ||
         (gcolor_equal(palette.digits, GColorBlack) && gcolor_equal(palette.background, GColorWhite));
#else
  return true;
#endif
}

static void load_palette(void) {
  Palette saved;
  if (persist_read_data(PERSIST_PALETTE, &saved, sizeof(saved)) == sizeof(saved) &&
      palette_is_valid(saved)) {
    s_palette = saved;
    return;
  }
#ifdef PBL_PLATFORM_EMERY
  s_palette = (Palette){GColorFromHEX(0xff5500), GColorFromHEX(0x000055)};
#else
  s_palette = (Palette){GColorWhite, GColorBlack};
#endif
}

static void apply_palette(void) {
  // All digit resources use a four-entry palette. Keep each entry's edge coverage.
  for (size_t i = 0; i < ARRAY_LENGTH(s_digit_bitmaps); ++i) {
    if (!s_digit_bitmaps[i]) {
      continue;
    }
    GColor *entries = gbitmap_get_palette(s_digit_bitmaps[i]);
    if (entries) {
      for (size_t j = 0; j < 4; ++j) {
        uint8_t alpha = entries[j].a;
        entries[j] = s_palette.digits;
        entries[j].a = alpha;
      }
    }
  }
  BitmapLayer *layers[] = {s_hour_tens_layer, s_hour_ones_layer, s_minute_tens_layer, s_minute_ones_layer};
  for (size_t i = 0; i < ARRAY_LENGTH(layers); ++i) {
    bitmap_layer_set_background_color(layers[i], s_palette.background);
    layer_mark_dirty(bitmap_layer_get_layer(layers[i]));
  }
  window_set_background_color(s_main_window, s_palette.background);
}

static bool read_color(Tuple *tuple, GColor *color) {
  if (!tuple || (tuple->type != TUPLE_UINT && tuple->type != TUPLE_INT)) {
    return false;
  }
  uint32_t rgb;
  switch (tuple->length) {
    case 1: rgb = tuple->value->uint8; break;
    case 2: rgb = tuple->value->uint16; break;
    case 4: rgb = tuple->value->uint32; break;
    default: return false;
  }
  if (rgb > 0xffffff) {
    return false;
  }
  *color = GColorFromHEX(rgb);
  return true;
}

static void receive_colors(DictionaryIterator *message, void *context) {
  Palette next;
  if (!read_color(dict_find(message, MESSAGE_KEY_DigitColor), &next.digits) ||
      !read_color(dict_find(message, MESSAGE_KEY_BackgroundColor), &next.background) ||
      !palette_is_valid(next)) {
    return;
  }
  if (gcolor_equal(next.digits, s_palette.digits) && gcolor_equal(next.background, s_palette.background)) {
    return;
  }
  if (persist_write_data(PERSIST_PALETTE, &next, sizeof(next)) == sizeof(next)) {
    s_palette = next;
    apply_palette();
  }
}

// Resource IDs for digit bitmaps
#ifdef PBL_PLATFORM_EMERY
static const uint32_t DIGIT_RESOURCE_IDS[] = {
  RESOURCE_ID_DIGIT_EMERY_0,
  RESOURCE_ID_DIGIT_EMERY_1,
  RESOURCE_ID_DIGIT_EMERY_2,
  RESOURCE_ID_DIGIT_EMERY_3,
  RESOURCE_ID_DIGIT_EMERY_4,
  RESOURCE_ID_DIGIT_EMERY_5,
  RESOURCE_ID_DIGIT_EMERY_6,
  RESOURCE_ID_DIGIT_EMERY_7,
  RESOURCE_ID_DIGIT_EMERY_8,
  RESOURCE_ID_DIGIT_EMERY_9
};
#else
static const uint32_t DIGIT_RESOURCE_IDS[] = {
  RESOURCE_ID_DIGIT_0,
  RESOURCE_ID_DIGIT_1,
  RESOURCE_ID_DIGIT_2,
  RESOURCE_ID_DIGIT_3,
  RESOURCE_ID_DIGIT_4,
  RESOURCE_ID_DIGIT_5,
  RESOURCE_ID_DIGIT_6,
  RESOURCE_ID_DIGIT_7,
  RESOURCE_ID_DIGIT_8,
  RESOURCE_ID_DIGIT_9
};
#endif

#ifdef PBL_PLATFORM_GABBRO
// Fixed-size glyphs share a baseline. Center the two-column grid on the round display.
enum { ROUND2_WIDTH = 80, ROUND2_HEIGHT = 94, ROUND2_COLUMN_GAP = 4, ROUND2_ROW_GAP = 6 };

static GRect round2_digit_frame(int column, int row) {
  GRect bounds = layer_get_bounds(window_get_root_layer(s_main_window));
  int row_width = 2 * ROUND2_WIDTH + ROUND2_COLUMN_GAP;
  int x = (bounds.size.w - row_width) / 2 + column * (ROUND2_WIDTH + ROUND2_COLUMN_GAP);
  int y = (bounds.size.h - 2 * ROUND2_HEIGHT - ROUND2_ROW_GAP) / 2 + row * (ROUND2_HEIGHT + ROUND2_ROW_GAP);
  return GRect(x, y, ROUND2_WIDTH, ROUND2_HEIGHT);
}
#endif

// Update the time display
static void update_time() {
  // Get hours and minutes
  int hours, minutes;
  int hour_tens, hour_ones, minute_tens, minute_ones;
  bool use_24h;

#ifdef SCREENSHOT_MODE
  // Use screenshot mode time
  use_24h = SCREENSHOT_TIME_24H;
  hours = SCREENSHOT_HOUR;
  minutes = SCREENSHOT_MINUTE;
#else
  // Get actual time
  time_t temp = time(NULL);
  struct tm *tick_time = localtime(&temp);
  use_24h = clock_is_24h_style();
  hours = tick_time->tm_hour;
  minutes = tick_time->tm_min;
#endif

  // Get hours based on 12h/24h preference
  if (use_24h) {
    hour_tens = hours / 10;
    hour_ones = hours % 10;
  } else {
    // Convert to 12-hour format
    hours = hours % 12;
    if (hours == 0) {
      hours = 12;  // Midnight/noon should display as 12
    }
    hour_tens = hours / 10;
    hour_ones = hours % 10;
  }

  // Get minutes
  minute_tens = minutes / 10;
  minute_ones = minutes % 10;

  // Update all four bitmap layers
  // In 12h format, hide hour_tens if it's 0 (e.g., for times like 2:23)
  if (!use_24h && hour_tens == 0) {
    bitmap_layer_set_bitmap(s_hour_tens_layer, NULL);
    layer_set_hidden(bitmap_layer_get_layer(s_hour_tens_layer), true);
  } else {
    bitmap_layer_set_bitmap(s_hour_tens_layer, s_digit_bitmaps[hour_tens]);
    layer_set_hidden(bitmap_layer_get_layer(s_hour_tens_layer), false);
  }

  bitmap_layer_set_bitmap(s_hour_ones_layer, s_digit_bitmaps[hour_ones]);
  bitmap_layer_set_bitmap(s_minute_tens_layer, s_digit_bitmaps[minute_tens]);
  bitmap_layer_set_bitmap(s_minute_ones_layer, s_digit_bitmaps[minute_ones]);
}

// Tick handler - called every minute
static void tick_handler(struct tm *tick_time, TimeUnits units_changed) {
  update_time();
}

// Window load handler
static void main_window_load(Window *window) {
  // Get window information
  Layer *window_layer = window_get_root_layer(window);
#ifndef PBL_PLATFORM_GABBRO
  GRect bounds = layer_get_bounds(window_layer);
#endif

  // Load all digit bitmaps
  for (int i = 0; i < 10; i++) {
    s_digit_bitmaps[i] = gbitmap_create_with_resource(DIGIT_RESOURCE_IDS[i]);
  }

#if !defined(PBL_ROUND) && !defined(PBL_PLATFORM_EMERY)
  // Calculate rectangular quadrant dimensions (2x2 grid)
  int16_t quadrant_width = bounds.size.w / 2;
  int16_t quadrant_height = bounds.size.h / 2;
#endif

#ifdef PBL_PLATFORM_EMERY
    // Pebble Time 2 keeps a small perimeter inset while using the full
    // remaining display area for paired hour and minute digits.
    int16_t padding = 10;
    int16_t adjusted_width = (bounds.size.w - 2 * padding) / 2;
    int16_t adjusted_height = (bounds.size.h - 2 * padding) / 2;

    s_hour_tens_layer = bitmap_layer_create(GRect(padding, padding, adjusted_width, adjusted_height));
    s_hour_ones_layer = bitmap_layer_create(GRect(padding + adjusted_width, padding, adjusted_width, adjusted_height));
    s_minute_tens_layer = bitmap_layer_create(GRect(padding, padding + adjusted_height, adjusted_width, adjusted_height));
    s_minute_ones_layer = bitmap_layer_create(GRect(padding + adjusted_width, padding + adjusted_height, adjusted_width, adjusted_height));
#elif defined(PBL_PLATFORM_GABBRO)
    s_hour_tens_layer = bitmap_layer_create(round2_digit_frame(0, 0));
    s_hour_ones_layer = bitmap_layer_create(round2_digit_frame(1, 0));
    s_minute_tens_layer = bitmap_layer_create(round2_digit_frame(0, 1));
    s_minute_ones_layer = bitmap_layer_create(round2_digit_frame(1, 1));
#elif defined(PBL_ROUND)
    // For round displays, use padding in quadrant layout
    int16_t padding = 10;
    int16_t adjusted_width = (bounds.size.w - 2 * padding) / 2;
    int16_t adjusted_height = (bounds.size.h - 2 * padding) / 2;

    // Top-left quadrant: hour tens (reduced height by 1px for row padding)
    s_hour_tens_layer = bitmap_layer_create(GRect(padding, padding, adjusted_width, adjusted_height - 1));

    // Top-right quadrant: hour ones (reduced height by 1px for row padding)
    s_hour_ones_layer = bitmap_layer_create(GRect(padding + adjusted_width, padding, adjusted_width, adjusted_height - 1));

    // Bottom-left quadrant: minute tens
    s_minute_tens_layer = bitmap_layer_create(GRect(padding, padding + adjusted_height, adjusted_width, adjusted_height));

    // Bottom-right quadrant: minute ones
    s_minute_ones_layer = bitmap_layer_create(GRect(padding + adjusted_width, padding + adjusted_height, adjusted_width, adjusted_height));
#else
    // For rectangular displays - 2x2 quadrant grid
    // Top-left quadrant: hour tens (reduced height by 1px for row padding)
    s_hour_tens_layer = bitmap_layer_create(GRect(0, 0, quadrant_width, quadrant_height - 1));

    // Top-right quadrant: hour ones (reduced height by 1px for row padding)
    s_hour_ones_layer = bitmap_layer_create(GRect(quadrant_width, 0, quadrant_width, quadrant_height - 1));

    // Bottom-left quadrant: minute tens
    s_minute_tens_layer = bitmap_layer_create(GRect(0, quadrant_height, quadrant_width, quadrant_height));

    // Bottom-right quadrant: minute ones
    s_minute_ones_layer = bitmap_layer_create(GRect(quadrant_width, quadrant_height, quadrant_width, quadrant_height));
#endif

  // Configure all bitmap layers
  bitmap_layer_set_compositing_mode(s_hour_tens_layer, GCompOpSet);
  bitmap_layer_set_compositing_mode(s_hour_ones_layer, GCompOpSet);
  bitmap_layer_set_compositing_mode(s_minute_tens_layer, GCompOpSet);
  bitmap_layer_set_compositing_mode(s_minute_ones_layer, GCompOpSet);

  // Add all layers to the window
  layer_add_child(window_layer, bitmap_layer_get_layer(s_hour_tens_layer));
  layer_add_child(window_layer, bitmap_layer_get_layer(s_hour_ones_layer));
  layer_add_child(window_layer, bitmap_layer_get_layer(s_minute_tens_layer));
  layer_add_child(window_layer, bitmap_layer_get_layer(s_minute_ones_layer));

  apply_palette();
}

// Window unload handler
static void main_window_unload(Window *window) {
  // Destroy all BitmapLayers
  bitmap_layer_destroy(s_hour_tens_layer);
  bitmap_layer_destroy(s_hour_ones_layer);
  bitmap_layer_destroy(s_minute_tens_layer);
  bitmap_layer_destroy(s_minute_ones_layer);

  // Unload all digit bitmaps
  for (int i = 0; i < 10; i++) {
    gbitmap_destroy(s_digit_bitmaps[i]);
  }
}

// Initialize the app
static void init() {
  load_palette();

  // Create main Window element
  s_main_window = window_create();

  // Set window handlers
  window_set_window_handlers(s_main_window, (WindowHandlers) {
    .load = main_window_load,
    .unload = main_window_unload
  });

  // Show the Window on the watch, with animated=true
  window_stack_push(s_main_window, true);

  app_message_register_inbox_received(receive_colors);
  app_message_open(64, 16);

  // Register with TickTimerService for minute updates
  tick_timer_service_subscribe(MINUTE_UNIT, tick_handler);

  // Display the initial time
  update_time();
}

// Deinitialize the app
static void deinit() {
  // Unsubscribe from tick timer service
  tick_timer_service_unsubscribe();

  // Destroy Window
  window_destroy(s_main_window);
}

// Main entry point
int main(void) {
  init();
  app_event_loop();
  deinit();

  return 0;
}
