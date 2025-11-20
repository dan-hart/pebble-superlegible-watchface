module.exports = [
  {
    "type": "heading",
    "defaultValue": "Superlegible Watchface Configuration"
  },
  {
    "type": "text",
    "defaultValue": "Customize your watchface display settings."
  },
  {
    "type": "section",
    "items": [
      {
        "type": "heading",
        "defaultValue": "Date Display"
      },
      {
        "type": "toggle",
        "messageKey": "DATE_ENABLED",
        "label": "Show Date",
        "description": "Display day of week and date below the time",
        "defaultValue": true
      },
      {
        "type": "select",
        "messageKey": "LANGUAGE",
        "label": "Day of Week Language",
        "description": "Language for day abbreviations",
        "defaultValue": "0",
        "options": [
          {
            "label": "English",
            "value": "0"
          },
          {
            "label": "Spanish (Coming Soon)",
            "value": "1"
          },
          {
            "label": "French (Coming Soon)",
            "value": "2"
          },
          {
            "label": "Mandarin (Coming Soon)",
            "value": "3"
          },
          {
            "label": "Hindi (Coming Soon)",
            "value": "4"
          }
        ]
      }
    ]
  },
  {
    "type": "submit",
    "defaultValue": "Save Settings"
  }
];
