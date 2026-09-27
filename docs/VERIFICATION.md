# Initial release verification

September 27, 2026.

- Home Assistant target version: 2026.9.3, read from the instance’s `.HA_VERSION` file.
- 29 local tests passed against Home Assistant 2026.9.3, using real public NOAA fixture data.
- All 20 entities load through Home Assistant’s actual platform setup. Timestamp and height types, PNG serving, duplicate station handling, cache restoration, offline expiry, unit-cache isolation, time rollover and DST boundaries tested.
- Live NOAA metadata, high/low and six-minute endpoints successfully queried for station 8446121. No API key required.
- NWS `weather.kpvc` verified in the live registry as “Provincetown Weather.” Installed NWS platform supports hourly and twice-daily forecasts.
- Light/dark daily and weekly graphs rendered and visually inspected. Design preview checked at desktop and phone widths; it is a layout reference, not a screenshot of the installed HA dashboard.
- Both official Windy embeds loaded in Chrome with Provincetown map labels. Radar displayed its current observation timestamp; the wind map displayed its forecast time.
- Examples parsed successfully as YAML. Native dashboard rendering still needs live verification after installation.
- Existing house configuration and unfinished automation/script edits were not changed. No files copied to the live share, no restart, no HA stability claim or stable tag.
- Live installation is waiting for UI login, native backup/recovery verification, configuration check, restart and dashboard checks. See `INSTALLATION.md`.
