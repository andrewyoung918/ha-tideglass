# Styled Coast dashboard

The styled example matches the dark Tideglass graph palette: deep navy `#101f2b`, seafoam `#73dbc7`, warm gold `#efd19a`, and soft white `#edf5f2`. It was verified on Home Assistant 2026.9.3 at 1280-pixel desktop and 390-pixel phone widths.

## Setup

1. Set up Tideglass and a Home Assistant weather integration. The example uses Provincetown’s existing NWS entity, `weather.kpvc`.
2. Install [button-card](https://github.com/custom-cards/button-card) and [clock-weather-card](https://github.com/pkissling/clock-weather-card) through HACS. Confirm both dashboard resources are loaded.
3. Export the current dashboard raw configuration before replacing it. Paste [`weather-dashboard-aesthetic.yaml`](../examples/weather-dashboard-aesthetic.yaml) through the dashboard’s supported raw configuration editor, then save.
4. Check desktop and phone layouts, both maps, the forecast, and tide times. Restore the exported configuration through that same editor if validation fails.

The example contains a complete dashboard configuration, including `button_card_templates`. When merging it into an existing dashboard, merge that top-level template block as well as the view. It applies its own colors and background within the view without requiring a server-side theme or changing the house theme.

## Data and interactions

- Current conditions, temperature, humidity and wind come from `weather.kpvc`. The six hourly forecast rows use clock-weather-card’s supported forecast subscription. NWS Provincetown supports hourly and twice-daily forecasts; this design uses hourly rows to avoid duplicated day/night labels.
- The high/low cards show explicit local times, dates, and numeric heights. Tap a card for its entity details.
- The status card keeps tide direction, the most recent tide, predicted current height, and fresh/cached/unavailable status visible. Predicted height is unavailable for subordinate stations that lack a continuous NOAA prediction curve.
- The weekly table reads the typed `tides` attribute directly from the week sensor. All 28 events were checked against the underlying sensor on the installed station. Tap the table, then use **Menu → Details** to inspect its full attributes. The calendar entity remains available for automation and other dashboards.
- Both official Windy embeds retain their map controls, legend and play button. Their weather imagery has Windy’s own colors, inside matching Tideglass card frames.
- Missing values are shown as unavailable or a dash; they are not converted to zero. Tide heights are NOAA predictions relative to MLLW, not observed water levels.

## Customize

For another station, replace the `provincetown_tideglass` entity prefix with the actual entities created by Home Assistant, update the station title and map coordinates, and replace `America/New_York` with the station’s time zone. Replace `weather.kpvc` with an entity that supports hourly forecasts. Height units are read from the relevant entities; temperature and wind units come from the weather entity.

The template block controls card colors, corners and text. The weekly table has a phone layout below 600 pixels. The large daily and weekly graphs stay native Tideglass image entities; no client-side curve approximation or additional NOAA polling is introduced.

The [native-card alternative](../examples/weather-dashboard.yaml) is still available for installations that prefer no frontend custom-card dependencies. The styled example changes presentation only; timestamp sensors, height sensors, week attributes, and the tide calendar remain available for triggers.
