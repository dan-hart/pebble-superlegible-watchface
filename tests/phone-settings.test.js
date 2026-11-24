// Run after pebble build to exercise the same PebbleKit JS shipped in the PBW.
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { test } = require('node:test');
const { runInNewContext } = require('node:vm');

test('the bundled phone settings save, replay, and isolate palettes per watch', () => {
  const bundle = readFileSync('build/pebble-js-app.js', 'utf8');
  const manifest = JSON.parse(readFileSync('build/appinfo.json', 'utf8'));
  assert.ok(manifest.capabilities.includes('configurable'));
  const callbacks = {};
  const messages = [];
  const storage = new Map();
  let watch = 'emery';
  let url;
  const Pebble = {
    platform: 'ios',
    getActiveWatchInfo: () => ({ platform: watch, firmware: { major: 4 } }),
    getAccountToken: () => '',
    getWatchToken: () => watch,
    openURL: value => { url = value; },
    sendAppMessage: message => messages.push({ ...message }),
    addEventListener(name, handler) { (callbacks[name] ||= []).push(handler); }
  };
  const localStorage = {
    getItem: key => storage.get(key) ?? null,
    setItem: (key, value) => storage.set(key, value)
  };
  const fire = (name, event) => callbacks[name].forEach(handler => handler(event));
  const palette = (digits, background) => ({
    DigitColor: { value: digits }, BackgroundColor: { value: background }
  });
  runInNewContext(bundle, { Pebble, localStorage, console });
  fire('ready');
  assert.deepEqual(messages, []);
  fire('showConfiguration');
  assert.ok(url.startsWith('data:text/html'));
  const pickerState = () => JSON.parse(storage.get('clay-settings'));
  assert.deepEqual(pickerState(), { DigitColor: 0xff5500, BackgroundColor: 0x000055 });

  const response = encodeURIComponent(JSON.stringify(palette(0, 0xffffff)));
  fire('webviewclosed', { response });
  const wire = { [manifest.appKeys.DigitColor]: 0, [manifest.appKeys.BackgroundColor]: 0xffffff };
  assert.deepEqual(messages, [wire]);
  fire('ready');
  assert.deepEqual(messages, [wire, wire]);

  watch = 'diorite';
  fire('showConfiguration');
  assert.deepEqual(pickerState(), { DigitColor: 0xffffff, BackgroundColor: 0 });
  fire('webviewclosed', { response: '' });
  assert.equal(messages.length, 2);
  fire('showConfiguration');
  watch = 'emery';
  fire('webviewclosed', { response });
  assert.equal(messages.length, 2);
  fire('showConfiguration');
  assert.deepEqual(pickerState(), { DigitColor: 0, BackgroundColor: 0xffffff });
});
