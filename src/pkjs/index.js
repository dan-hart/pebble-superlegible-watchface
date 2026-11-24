var Clay = require('@rebble/clay');

function requireDifferentColors() {
  var page = this;
  page.on(page.EVENTS.AFTER_BUILD, function () {
    var digits = page.getItemByMessageKey('DigitColor');
    var background = page.getItemByMessageKey('BackgroundColor');
    var save = page.getItemById('save');

    function validate() {
      if (digits.get() === background.get()) {
        save.set('Choose two different colors');
        save.disable();
      } else {
        save.set('Save');
        save.enable();
      }
    }
    // Clay reads an empty color field as black. Paint its initial swatch too.
    digits.trigger('change');
    background.trigger('change');
    digits.on('change', validate);
    background.on('change', validate);
    validate();
  });
}

var clay = new Clay([
  { type: 'heading', defaultValue: 'Superlegible' },
  { type: 'color', messageKey: 'DigitColor', label: 'Digits' },
  { type: 'color', messageKey: 'BackgroundColor', label: 'Background' },
  { type: 'submit', id: 'save', defaultValue: 'Save' }
], requireDifferentColors, { autoHandleEvents: false });

function activeWatch() {
  var info = Pebble.getActiveWatchInfo && Pebble.getActiveWatchInfo();
  var platform = info && info.platform;
  var watchId = Pebble.getWatchToken && Pebble.getWatchToken();
  return {
    info: info,
    key: 'palette:' + (watchId || platform || 'default'),
    defaults: platform === 'emery'
      ? { DigitColor: 0xff5500, BackgroundColor: 0x000055 }
      : { DigitColor: 0xffffff, BackgroundColor: 0x000000 }
  };
}

function savedColors(watch) {
  var json = localStorage.getItem(watch.key);
  if (!json) {
    return null;
  }
  try {
    return JSON.parse(json);
  } catch (error) {
    return null;
  }
}

function sendColors(colors) {
  Pebble.sendAppMessage(Clay.prepareSettingsForAppMessage(colors), function () {}, function (error) {
    console.log('Color settings will be sent again when the face opens: ' + JSON.stringify(error));
  });
}

// Keep the pending selection with its original watch if pairing changes mid-edit.
var editingWatch;
Pebble.addEventListener('showConfiguration', function () {
  editingWatch = activeWatch();
  clay.meta.activeWatchInfo = editingWatch.info;
  clay.setSettings(savedColors(editingWatch) || editingWatch.defaults);
  Pebble.openURL(clay.generateUrl());
});

Pebble.addEventListener('webviewclosed', function (event) {
  var watch = editingWatch;
  editingWatch = null;
  if (!watch || !event || !event.response || event.response === 'CANCELLED') {
    return;
  }
  var values;
  try {
    values = clay.getSettings(event.response, false);
  } catch (error) {
    return;
  }
  if (!values || !values.DigitColor || !values.BackgroundColor) {
    return;
  }
  var colors = {
    DigitColor: values.DigitColor.value,
    BackgroundColor: values.BackgroundColor.value
  };
  if (typeof colors.DigitColor !== 'number' || typeof colors.BackgroundColor !== 'number' ||
      colors.DigitColor === colors.BackgroundColor) {
    return;
  }
  localStorage.setItem(watch.key, JSON.stringify(colors));
  if (watch.key === activeWatch().key) {
    sendColors(colors);
  }
});

Pebble.addEventListener('ready', function () {
  var colors = savedColors(activeWatch());
  if (colors) {
    sendColors(colors);
  }
});
