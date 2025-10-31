#include <pebble.h>

// UI Elements - 4 BitmapLayers for individual digits
static Window *s_main_window;
static BitmapLayer *s_hour_tens_layer;
static BitmapLayer *s_hour_ones_layer;
static BitmapLayer *s_minute_tens_layer;
static BitmapLayer *s_minute_ones_layer;

// Bitmaps for digits 0-9
static GBitmap *s_digit_bitmaps[10];

// Resource IDs for digit bitmaps
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

// Update the time display
static void update_time() {
  // Get a tm structure
  time_t temp = time(NULL);
  struct tm *tick_time = localtime(&temp);

  // Get hours based on 12h/24h preference
  int hours;
  int hour_tens, hour_ones;

  if (clock_is_24h_style()) {
    hours = tick_time->tm_hour;
    hour_tens = hours / 10;
    hour_ones = hours % 10;
  } else {
    // Convert to 12-hour format
    hours = tick_time->tm_hour % 12;
    if (hours == 0) {
      hours = 12;  // Midnight/noon should display as 12
    }
    hour_tens = hours / 10;
    hour_ones = hours % 10;
  }

  // Get minutes
  int minutes = tick_time->tm_min;
  int minute_tens = minutes / 10;
  int minute_ones = minutes % 10;

  // Update all four bitmap layers
  // In 12h format, hide hour_tens if it's 0 (e.g., for times like 2:23)
  if (!clock_is_24h_style() && hour_tens == 0) {
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
  GRect bounds = layer_get_bounds(window_layer);

  // Load all digit bitmaps
  for (int i = 0; i < 10; i++) {
    s_digit_bitmaps[i] = gbitmap_create_with_resource(DIGIT_RESOURCE_IDS[i]);
  }

  // Calculate quadrant dimensions (2x2 grid)
  int16_t quadrant_width = bounds.size.w / 2;   // 72px
  int16_t quadrant_height = bounds.size.h / 2;  // 84px

  #ifdef PBL_ROUND
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

  // Set background color to black for all layers
  bitmap_layer_set_background_color(s_hour_tens_layer, GColorBlack);
  bitmap_layer_set_background_color(s_hour_ones_layer, GColorBlack);
  bitmap_layer_set_background_color(s_minute_tens_layer, GColorBlack);
  bitmap_layer_set_background_color(s_minute_ones_layer, GColorBlack);

  // Add all layers to the window
  layer_add_child(window_layer, bitmap_layer_get_layer(s_hour_tens_layer));
  layer_add_child(window_layer, bitmap_layer_get_layer(s_hour_ones_layer));
  layer_add_child(window_layer, bitmap_layer_get_layer(s_minute_tens_layer));
  layer_add_child(window_layer, bitmap_layer_get_layer(s_minute_ones_layer));

  // Set window background to black
  window_set_background_color(window, GColorBlack);
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
  // Create main Window element
  s_main_window = window_create();

  // Set window handlers
  window_set_window_handlers(s_main_window, (WindowHandlers) {
    .load = main_window_load,
    .unload = main_window_unload
  });

  // Show the Window on the watch, with animated=true
  window_stack_push(s_main_window, true);

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
