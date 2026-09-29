# Interactive Tideglass card

Tideglass 0.2.0 bundles a responsive Home Assistant card. Its colors match Coast: deep navy, seafoam tide lines, warm gold solar markers, and a quiet blue offset for nighttime.

After upgrading in HACS, restart Home Assistant and reload the browser. The integration registers the bundled JavaScript automatically; no CDN, extra HACS card, new API key, or manual resource entry is needed. Choose **Tideglass** in the card picker, or use:

```yaml
type: custom:tideglass-card
entity: sensor.provincetown_tideglass_week
weather_entity: weather.coast_weather
grid_options:
  columns: full
  rows: auto
```

`entity` selects an existing sensor belonging to the Tideglass station. `weather_entity` is optional and can be any Home Assistant weather entity supporting hourly forecasts. `title` overrides the heading; `expanded: true` opens the weather section initially. Configuration is available in the visual card editor.

## Using the timeline

- Swipe horizontally, scroll with a trackpad, or drag with a mouse. Days use native **proximity** snapping: you can pause between days. Previous/next buttons move to a local midnight; Now returns to the current tide with four hours of context. Initial display also follows the current time.
- Tap the curve for the local time and height. Focus the timeline and use left/right arrows for days, Home for Now, End for the end, and Enter to inspect the center time. Focus indicators and reduced-motion preferences are respected.
- Expand Weather to show condition icons, temperature, wind speed, and rain probability every four local hours. The curve and weather use a **single scroll container and time scale**, so swipes keep them aligned. Temperature and wind units come from the selected weather entity.
- Tide heights use one vertical scale for the whole seven-day view, keeping days comparable. Solar crossings use the tide station's coordinates and time zone, including 23/25-hour DST days. Weather remains aligned by actual timestamps. Polar day/night does not invent crossings.
- The responsive layout keeps page width fixed, gives touch controls at least 44px height, and keeps four-hour columns legible. On narrow screens part of a day is visible, inviting horizontal exploration.

## Data and failure behavior

The authenticated `tideglass/timeline` WebSocket command takes `entity_id`, checks read permission, resolves the station through the entity registry, and returns seven local days of the coordinator's cached NOAA samples/events plus locally calculated solar crossings. It never contacts NOAA itself and does not add large series to recorder state attributes. The card refreshes this payload every five minutes; its Now marker refreshes every minute. Existing sensors, images and automation IDs are unchanged.

Actual six-minute NOAA samples are joined directly. Missing sample gaps are not bridged and values are never extrapolated. Subordinate stations retain their explicitly labeled illustrative curve. Stored prediction fallback is identified; expired/unavailable tide data becomes an explicit unavailable card.

Weather uses Home Assistant's `weather/subscribe_forecast` hourly subscription. It samples the hourly interval containing each 00:00, 04:00, 08:00, 12:00, 16:00 and 20:00 station-local time. These are point-in-time hourly forecasts, not four-hour averages. Missing fields, past hours omitted by the provider, and times beyond the provider's hourly horizon display dashes. Zero precipitation is shown as 0%. Unavailable entities, subscription failures, or two hours without a forecast delivery hide weather readings while leaving tide data visible. Removing the card cleans up subscriptions, timers and resize observers. Failed subscriptions retry at a bounded five-minute interval.

## Development and validation

`PYTHONPATH=. .venv/bin/python scripts/build_card_preview.py` produces an ignored local test page at `.local/card-preview/index.html`. Serve the repository locally to preview it. Its tides come from NOAA test fixtures and its **weather is explicitly simulated**. Preview icons are lightweight stand-ins; Home Assistant provides real `ha-icon` icons in production.

Run `.venv/bin/pytest -q`, `.venv/bin/ruff check .`, and `node --test tests/card.test.cjs`. Automated coverage includes the authenticated endpoint and permissions, static asset loading, seven-day sample bounds, cached expiry, DST, polar sunlight, no extrapolation, missing weather hours, valid zero values and HTML escaping. Live deployment and visual verification evidence belongs in the deployment record.

Official API references: [custom cards](https://developers.home-assistant.io/docs/frontend/custom-ui/custom-card/), [async static resources](https://developers.home-assistant.io/blog/2024/06/18/async_register_static_paths/), and [weather forecast subscription](https://github.com/home-assistant/frontend/blob/dev/src/data/weather.ts).
