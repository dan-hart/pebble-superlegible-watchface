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

// Date display TextLayers
static TextLayer *s_day_layer;   // Day of week (e.g., "Wed")
static TextLayer *s_date_layer;  // Date number (e.g., "19")

// Custom font for date display
static GFont s_date_font;


// Bitmaps for digits 0-9
static GBitmap *s_digit_bitmaps[10];

// Language support
typedef enum {
  LANGUAGE_ENGLISH = 0,
  LANGUAGE_SPANISH = 1,
  LANGUAGE_FRENCH = 2,
  LANGUAGE_MANDARIN = 3,
  LANGUAGE_HINDI = 4,
  LANGUAGE_COUNT
} Language;

// Day abbreviations for each language
static const char *DAY_ABBREVIATIONS[LANGUAGE_COUNT][7] = {
  // English
  {"Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"},
  // Spanish (placeholder - ready for expansion)
  {"Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"},
  // French (placeholder - ready for expansion)
  {"Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"},
  // Mandarin Pinyin (placeholder - ready for expansion)
  {"日", "一", "二", "三", "四", "五", "六"},
  // Hindi Romanized (placeholder - ready for expansion)
  {"Ravi", "Som", "Mangal", "Budh", "Guru", "Shukra", "Shani"}
};

// Settings
#define SETTINGS_KEY_DATE_ENABLED 1
#define SETTINGS_KEY_LANGUAGE 2

static bool s_date_enabled = true;
static Language s_language = LANGUAGE_ENGLISH;

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

// Update the date display
static void update_date() {
  if (!s_date_enabled) {
    layer_set_hidden(text_layer_get_layer(s_day_layer), true);
    layer_set_hidden(text_layer_get_layer(s_date_layer), true);
    return;
  }

  // Get current time
  time_t temp = time(NULL);
  struct tm *tick_time = localtime(&temp);

  // Get day of week (0 = Sunday, 6 = Saturday)
  int day_of_week = tick_time->tm_wday;

  // Get day of month
  int day_of_month = tick_time->tm_mday;

  // Format day of month as string
  static char date_buffer[8];
  snprintf(date_buffer, sizeof(date_buffer), "%d", day_of_month);

  // Update TextLayers
  text_layer_set_text(s_day_layer, DAY_ABBREVIATIONS[s_language][day_of_week]);
  text_layer_set_text(s_date_layer, date_buffer);

  // Show layers
  layer_set_hidden(text_layer_get_layer(s_day_layer), false);
  layer_set_hidden(text_layer_get_layer(s_date_layer), false);
}

// Tick handler - called every minute
static void tick_handler(struct tm *tick_time, TimeUnits units_changed) {
  update_time();

  // Update date if day changed
  if (units_changed & DAY_UNIT) {
    update_date();
  }
}

// Window load handler
static void main_window_load(Window *window) {
  // Get window information
  Layer *window_layer = window_get_root_layer(window);
  GRect bounds = layer_get_bounds(window_layer);


  // Load custom font for date display
  s_date_font = fonts_load_custom_font(resource_get_handle(RESOURCE_ID_ATKINSON_MONO_EXTRABOLD_28));

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

  // Create date display TextLayers (below time)
  // Position at very bottom of screen with larger font
  int16_t date_y_position = bounds.size.h - 35;  // Position at bottom
  int16_t day_width = 72;  // Half screen width for day
  int16_t date_width = 72;  // Half screen width for date

  #ifdef PBL_ROUND
    // For round displays, adjust positioning
    int16_t date_y_offset = bounds.size.h - 45;
    s_day_layer = text_layer_create(GRect(10, date_y_offset, day_width, 40));
    s_date_layer = text_layer_create(GRect(bounds.size.w - date_width - 10, date_y_offset, date_width, 40));
  #else
    // For rectangular displays - full width split in half
    s_day_layer = text_layer_create(GRect(0, date_y_position, day_width, 40));
    s_date_layer = text_layer_create(GRect(quadrant_width, date_y_position, date_width, 40));
  #endif

  // Configure day layer (left-aligned)
  text_layer_set_background_color(s_day_layer, GColorClear);
  text_layer_set_text_color(s_day_layer, GColorWhite);
  text_layer_set_text_alignment(s_day_layer, GTextAlignmentCenter);
  text_layer_set_font(s_day_layer, s_date_font);

  // Configure date layer (right-aligned)
  text_layer_set_background_color(s_date_layer, GColorClear);
  text_layer_set_text_color(s_date_layer, GColorWhite);
  text_layer_set_text_alignment(s_date_layer, GTextAlignmentCenter);
  text_layer_set_font(s_date_layer, s_date_font);

  // Add date layers to window
  layer_add_child(window_layer, text_layer_get_layer(s_day_layer));
  layer_add_child(window_layer, text_layer_get_layer(s_date_layer));

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

  // Destroy date TextLayers
  text_layer_destroy(s_day_layer);
  text_layer_destroy(s_date_layer);

  // Unload custom font
  fonts_unload_custom_font(s_date_font);


  // Unload all digit bitmaps
  for (int i = 0; i < 10; i++) {
    gbitmap_destroy(s_digit_bitmaps[i]);
  }
}

// AppMessage inbox received handler
static void inbox_received_handler(DictionaryIterator *iter, void *context) {
  // Read DATE_ENABLED setting
  Tuple *date_enabled_tuple = dict_find(iter, MESSAGE_KEY_DATE_ENABLED);
  if (date_enabled_tuple) {
    s_date_enabled = date_enabled_tuple->value->int32 == 1;
    persist_write_bool(SETTINGS_KEY_DATE_ENABLED, s_date_enabled);
    update_date();  // Refresh display
  }

  // Read LANGUAGE setting
  Tuple *language_tuple = dict_find(iter, MESSAGE_KEY_LANGUAGE);
  if (language_tuple) {
    s_language = (Language)language_tuple->value->int32;
    persist_write_int(SETTINGS_KEY_LANGUAGE, (int)s_language);
    update_date();  // Refresh display
  }
}

// AppMessage inbox dropped handler
static void inbox_dropped_handler(AppMessageResult reason, void *context) {
  APP_LOG(APP_LOG_LEVEL_ERROR, "Message dropped! Reason: %d", (int)reason);
}

// AppMessage outbox failed handler
static void outbox_failed_handler(DictionaryIterator *iter, AppMessageResult reason, void *context) {
  APP_LOG(APP_LOG_LEVEL_ERROR, "Outbox send failed! Reason: %d", (int)reason);
}

// AppMessage outbox sent handler
static void outbox_sent_handler(DictionaryIterator *iter, void *context) {
  APP_LOG(APP_LOG_LEVEL_INFO, "Outbox send success!");
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

  // Register AppMessage callbacks
  app_message_register_inbox_received(inbox_received_handler);
  app_message_register_inbox_dropped(inbox_dropped_handler);
  app_message_register_outbox_failed(outbox_failed_handler);
  app_message_register_outbox_sent(outbox_sent_handler);

  // Open AppMessage with buffer sizes
  app_message_open(128, 128);

  // Show the Window on the watch, with animated=true
  window_stack_push(s_main_window, true);

  // Load settings from persistent storage
  s_date_enabled = persist_exists(SETTINGS_KEY_DATE_ENABLED)
                   ? persist_read_bool(SETTINGS_KEY_DATE_ENABLED)
                   : true;
  s_language = persist_exists(SETTINGS_KEY_LANGUAGE)
               ? (Language)persist_read_int(SETTINGS_KEY_LANGUAGE)
               : LANGUAGE_ENGLISH;

  // Register with TickTimerService for minute and day updates
  tick_timer_service_subscribe(MINUTE_UNIT | DAY_UNIT, tick_handler);

  // Display the initial time and date
  update_time();
  update_date();
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
