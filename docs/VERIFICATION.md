# Initial release verification

September 27, 2026.

- Home Assistant target version: 2026.9.3, read from the instance’s `.HA_VERSION` file.
- 29 local tests passed against Home Assistant 2026.9.3, using real public NOAA fixture data.
- All 20 entities load through Home Assistant’s actual platform setup. Timestamp and height types, PNG serving, duplicate station handling, cache restoration, offline expiry, unit-cache isolation, time rollover and DST boundaries tested.
- Live NOAA metadata, high/low and six-minute endpoints successfully queried for station 8446121. No API key required.
- NWS `weather.kpvc` verified in the live registry as “Provincetown Weather.” Installed NWS platform supports hourly and twice-daily forecasts.
- Light/dark daily and weekly graphs rendered and visually inspected. Design preview checked at desktop and phone widths; it is a layout reference, not a screenshot of the installed HA dashboard.
- Both official Windy embeds loaded in Chrome with Provincetown map labels. Radar displayed its current observation timestamp; the wind map displayed its forecast time.
- Examples parsed successfully as YAML.

## Live installation

- Installed version 0.1.0 through HACS’s supported UI using Codex’s in-app browser. All 16 installed source files match release commit `82ede8e7a132a51f4df31295d6ef93e9e9bdd154` byte for byte.
- Verified a current encrypted native backup on the system and in Home Assistant Cloud, private off-device emergency-kit storage, and the Supervisor terminal recovery route before installation.
- After installation, Tools → YAML → Check configuration returned “Configuration will not prevent Home Assistant from starting!” Core restarted successfully; the UI reconnected in about one minute and startup completed within five minutes. No host reboot or upgrade.
- Configured the default Provincetown station, feet, and America/New_York. All 20 entities loaded; prediction status was `fresh` and height sensors displayed feet.
- Observed the natural 18:29 EDT low-tide transition: most recent tide changed high → low, direction changed falling → rising, and next low advanced to September 28 at 06:46. The image’s next-event label advanced to the 00:43 high tide. No state injection or house-device actions were used.
- Created a separate UI-owned Coast dashboard with the native example YAML. Verified current NWS weather, twice-daily and hourly forecasts, live daily/weekly images, Windy radar and wind maps, and all 28 tide events for September 27–October 3. Reloading the dashboard preserved its content.
- Inspected the native layout at 1280-pixel desktop width, in a 652-pixel in-app panel, and at 390 × 844 phone size. Forecast rows scroll horizontally at narrow widths; the main sections stack into one column.
- Read the live entities through Tools → Template: 20 entities, timezone-aware UTC timestamps, 28 structured week events with numeric heights and high/low types, `ft` metadata, and the rising binary sensor `on`. Restored the previous demo template afterward.
- Filtered Home Assistant Core logs for `tideglass` after setup: no issues found. Other existing integrations reported startup/connection/authentication warnings; no claim is made that the whole household configuration is error-free.
- Existing managed house YAML and unfinished automation/script edits were preserved. The optional theme and example automations were not installed. HACS owns the component installation; the dashboard is UI-owned.
- Offline expiry, restart-cache restoration, DST, and other station types have automated coverage; these failure cases were not forced on the live household. Actual future automation actions and long-term operation remain untested.
