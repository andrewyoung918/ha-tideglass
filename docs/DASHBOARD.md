# Styled Coast dashboard

The styled example matches the dark Tideglass graph palette: deep navy `#101f2b`, seafoam `#73dbc7`, warm gold `#efd19a`, and soft white `#edf5f2`. It was verified on Home Assistant 2026.9.3 at 1280-pixel desktop and 390-pixel phone widths.

## Setup

1. Set up Tideglass **0.2.1 or newer**, reload the browser after its required installation restart, and configure [Pirate Weather](https://docs.pirateweather.net/en/latest/ha/). Name the weather integration **Coast Weather**, choose your location, enable both Weather and Sensor, and select Summary, Minutely Summary, Hourly Summary, Daily Summary, Precipitation Type, Precipitation Intensity, Precipitation Probability, Apparent Temperature, UV Index and Time. Use a 900-second update interval. Enter the API key directly in Home Assistant; it never belongs in dashboard YAML. Leave the per-day/per-hour sensor lists empty: the weather entity supplies forecasts.
2. Install [button-card](https://github.com/custom-cards/button-card) 7 or newer and [clock-weather-card](https://github.com/pkissling/clock-weather-card) through HACS. Confirm both dashboard resources are loaded. Verify that your entities match `weather.coast_weather` and the `sensor.coast_weather_*` names in the example, or replace those names before saving.
3. Export the current dashboard raw configuration before replacing it. Paste [`weather-dashboard-aesthetic.yaml`](../examples/weather-dashboard-aesthetic.yaml) through the dashboard’s supported raw configuration editor, then save.
4. Check desktop and phone layouts, both maps, the forecast, and tide times. Restore the exported configuration through that same editor if validation fails.

The example contains a complete dashboard configuration, including `button_card_templates` and four views. When merging it into an existing dashboard, merge that top-level template block as well as the views. It applies its own colors and background without requiring a server-side theme or changing the house theme.

## Four focused tabs

| Tab | Purpose |
| --- | --- |
| Summary | A compact first screen: current weather, feels-like temperature, next-hour rain, wind and humidity; next high/low with dates and heights; a short outlook. Tap the weather, tide or outlook card to open details. |
| Weather | Current conditions, rain chance/rate, UV, six hourly rows, five daily rows, and live radar. |
| Tides | The interactive seven-day tide/solar timeline, high/low details, prediction status, and a readable weekly table. Expand Weather in the timeline for aligned four-hour forecasts. |
| Wind | Current wind, gusts, direction and pressure, followed by the Windy forecast map. The compass points toward the direction the wind comes from. |

The Summary keeps the original `coast` view path. Navigation links assume the dashboard URL is `/dashboard-coast`; replace that prefix throughout the YAML when installing at another dashboard URL. Weather, Tides and Wind use `weather`, `tides` and `wind` view paths. Native tabs scroll horizontally on narrow phones; use their scroll arrows to reveal every tab. Maps and long tables stay on their detail tabs.

## Data and interactions

- Current conditions, temperature, humidity and wind come from `weather.coast_weather`. Six hourly rows and five daily rows use clock-weather-card’s supported forecast subscriptions.
- The next-hour rain panel displays Pirate Weather’s minutely summary, current precipitation chance and rate, feels-like temperature, UV and forecast time. It checks freshness locally every minute without additional API requests. If the forecast timestamp is over an hour old, the panel replaces its summary and readings with an update warning. Missing measurements remain distinct from zero.
- The standard integration supplies a minutely text summary, not a complete minute-by-minute sensor series. This example does not invent a rain graph or derive trigger timestamps by parsing forecast prose. Pirate Weather recommends polling no faster than 15 minutes because its minute data is interpolated from coarser forecasts; see its [update guidance](https://docs.pirateweather.net/en/latest/ha/#what-is-the-recommended-update-frequency).
- The high/low cards show explicit local times, dates, and numeric heights. Tap a card for its entity details.
- The status card keeps tide direction, the most recent tide, predicted current height, and fresh/cached/unavailable status visible. Predicted height is unavailable for subordinate stations that lack a continuous NOAA prediction curve.
- The bundled [interactive Tideglass card](INTERACTIVE-CARD.md) uses existing NOAA prediction data and supports dragging, touch scrolling, day snapping and aligned weather. Its installation is a prerequisite for this example; the image entities remain available for other dashboards.
- The weekly table reads the typed `tides` attribute directly from the week sensor. The number of events varies with the seven-day window. Tap the table, then use **Menu → Details** to inspect its full attributes. The calendar entity remains available for automation and other dashboards.
- Both official Windy embeds retain their map controls, legend and play button. Their weather imagery has Windy’s own colors, inside matching Tideglass card frames.
- Missing values are shown as unavailable or a dash; they are not converted to zero. Tide heights are NOAA predictions relative to MLLW, not observed water levels.

## Customize

For another station, replace the `provincetown_tideglass` entity prefix with the actual entities created by Home Assistant, update the station title and map coordinates, and replace `America/New_York` with the station’s time zone. The example uses public Provincetown coordinates `42.05, -70.18`. Height units are read from the relevant entities; temperature and wind units come from the weather entity.

To use another weather provider, replace `weather.coast_weather` with an entity supporting hourly and daily forecasts, then adapt the Pirate Weather summary/rain/timestamp references. Tideglass itself remains independent of Pirate Weather and does not need an API key.

The template block controls card colors, corners and text. The summary stacks into compact cards on phones, and the weekly table has a phone layout below 600 pixels. Timestamp-based freshness checks run locally every minute, without additional API polling; stale readings remain distinct from zero.

## Weather data for automations

`sensor.coast_weather_precip_probability` is a numeric percentage (0–100); `sensor.coast_weather_precip_intensity` is a numeric rate (`in/h` for US units). `sensor.coast_weather_time` is the forecast timestamp. Use native numeric-state triggers with freshness and availability conditions. A zero reading means zero; an unavailable or stale reading should not be treated as dry weather. The descriptive precipitation type is `sensor.coast_weather_precip`.

Use `weather.get_forecasts` with `weather.coast_weather` for supported hourly/daily structured forecasts. Summary sensors are human-readable text. No household automation is created or enabled by this dashboard.

The [native-card alternative](../examples/weather-dashboard.yaml) is still available for installations that prefer no frontend custom-card dependencies. The styled example changes presentation only; timestamp sensors, height sensors, week attributes, and the tide calendar remain available for triggers.
