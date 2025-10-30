#include <pebble.h>

// UI Elements - 4 TextLayers for quadrant layout
static Window *s_main_window;
static TextLayer *s_hour_tens_layer;
static TextLayer *s_hour_ones_layer;
static TextLayer *s_minute_tens_layer;
static TextLayer *s_minute_ones_layer;
static GFont s_time_font;

// Buffers for individual digits
static char s_hour_tens_buffer[2];
static char s_hour_ones_buffer[2];
static char s_minute_tens_buffer[2];
static char s_minute_ones_buffer[2];

// Update the time display
static void update_time() {
  // Get a tm structure
  time_t temp = time(NULL);
  struct tm *tick_time = localtime(&temp);

  // Get hours based on 12h/24h preference
  int hours;
  if (clock_is_24h_style()) {
    hours = tick_time->tm_hour;
  } else {
    // Convert to 12-hour format
    hours = tick_time->tm_hour % 12;
    if (hours == 0) {
      hours = 12;  // Midnight/noon should display as 12
    }
  }

  int minutes = tick_time->tm_min;

  // Extract individual digits
  int hour_tens = hours / 10;
  int hour_ones = hours % 10;
  int minute_tens = minutes / 10;
  int minute_ones = minutes % 10;

  // Convert digits to strings
  snprintf(s_hour_tens_buffer, sizeof(s_hour_tens_buffer), "%d", hour_tens);
  snprintf(s_hour_ones_buffer, sizeof(s_hour_ones_buffer), "%d", hour_ones);
  snprintf(s_minute_tens_buffer, sizeof(s_minute_tens_buffer), "%d", minute_tens);
  snprintf(s_minute_ones_buffer, sizeof(s_minute_ones_buffer), "%d", minute_ones);

  // Update all four TextLayers
  text_layer_set_text(s_hour_tens_layer, s_hour_tens_buffer);
  text_layer_set_text(s_hour_ones_layer, s_hour_ones_buffer);
  text_layer_set_text(s_minute_tens_layer, s_minute_tens_buffer);
  text_layer_set_text(s_minute_ones_layer, s_minute_ones_buffer);
}

// Tick handler - called every minute
static void tick_handler(struct tm *tick_time, TimeUnits units_changed) {
  update_time();
}

// Helper function to create and configure a digit TextLayer
static TextLayer* create_digit_layer(GRect frame, GFont font) {
  TextLayer *layer = text_layer_create(frame);
  text_layer_set_background_color(layer, GColorBlack);
  text_layer_set_text_color(layer, GColorWhite);
  text_layer_set_font(layer, font);
  text_layer_set_text_alignment(layer, GTextAlignmentCenter);
  return layer;
}

// Window load handler
static void main_window_load(Window *window) {
  // Get window information
  Layer *window_layer = window_get_root_layer(window);
  GRect bounds = layer_get_bounds(window_layer);

  // Load custom font (ExtraBold Mono for maximum readability and even spacing)
  s_time_font = fonts_load_custom_font(resource_get_handle(RESOURCE_ID_FONT_ATKINSON_MONO_EXTRABOLD_71));

  // Calculate quadrant dimensions
  int16_t half_width = bounds.size.w / 2;
  int16_t half_height = bounds.size.h / 2;

  // Platform-specific positioning
  #ifdef PBL_ROUND
    // For round displays (Chalk), adjust positioning to avoid edge clipping
    // Use slightly smaller quadrants with padding
    int16_t padding = 10;
    half_width = (bounds.size.w - 2 * padding) / 2;
    half_height = (bounds.size.h - 2 * padding) / 2;

    // Create quadrant TextLayers
    s_hour_tens_layer = create_digit_layer(
      GRect(padding, padding, half_width, half_height), s_time_font);
    s_hour_ones_layer = create_digit_layer(
      GRect(padding + half_width, padding, half_width, half_height), s_time_font);
    s_minute_tens_layer = create_digit_layer(
      GRect(padding, padding + half_height, half_width, half_height), s_time_font);
    s_minute_ones_layer = create_digit_layer(
      GRect(padding + half_width, padding + half_height, half_width, half_height), s_time_font);

    // Enable text flow for round displays
    text_layer_enable_screen_text_flow_and_paging(s_hour_tens_layer, 5);
    text_layer_enable_screen_text_flow_and_paging(s_hour_ones_layer, 5);
    text_layer_enable_screen_text_flow_and_paging(s_minute_tens_layer, 5);
    text_layer_enable_screen_text_flow_and_paging(s_minute_ones_layer, 5);
  #else
    // For rectangular displays - optimize horizontal spacing only
    // Bring digits closer together horizontally while maintaining full vertical height
    int16_t h_inset = 16;  // horizontal inset to bring digits closer to center

    // Create quadrant TextLayers (reduced width, full height):
    // Top-left: Hour tens
    s_hour_tens_layer = create_digit_layer(
      GRect(h_inset, 0, half_width - h_inset, half_height), s_time_font);

    // Top-right: Hour ones
    s_hour_ones_layer = create_digit_layer(
      GRect(half_width, 0, half_width - h_inset, half_height), s_time_font);

    // Bottom-left: Minute tens
    s_minute_tens_layer = create_digit_layer(
      GRect(h_inset, half_height, half_width - h_inset, half_height), s_time_font);

    // Bottom-right: Minute ones
    s_minute_ones_layer = create_digit_layer(
      GRect(half_width, half_height, half_width - h_inset, half_height), s_time_font);
  #endif

  // Add all layers to the window
  layer_add_child(window_layer, text_layer_get_layer(s_hour_tens_layer));
  layer_add_child(window_layer, text_layer_get_layer(s_hour_ones_layer));
  layer_add_child(window_layer, text_layer_get_layer(s_minute_tens_layer));
  layer_add_child(window_layer, text_layer_get_layer(s_minute_ones_layer));

  // Set window background to black
  window_set_background_color(window, GColorBlack);
}

// Window unload handler
static void main_window_unload(Window *window) {
  // Destroy all TextLayers
  text_layer_destroy(s_hour_tens_layer);
  text_layer_destroy(s_hour_ones_layer);
  text_layer_destroy(s_minute_tens_layer);
  text_layer_destroy(s_minute_ones_layer);

  // Unload custom font
  fonts_unload_custom_font(s_time_font);
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
