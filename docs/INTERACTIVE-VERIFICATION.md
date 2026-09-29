# Interactive Tideglass card verification

Verified September 28, 2026 local / September 29 UTC, on Home Assistant 2026.9.3.

## Installed result

- Release **v0.2.2**, candidate `6093d657b04792c890d436739169bde40ab637cf`, installed through HACS. All 18 installed component files match that commit byte for byte.
- The authenticated cached timeline endpoint and automatically registered card first shipped in v0.2.0. Immediately after installation, HA Tools → YAML → Check configuration passed; the coordinated Core restart completed within five minutes, with fresh Tideglass entities and the live card available by approximately 02:46 UTC.
- The v0.2.1 and v0.2.2 maintenance releases change only the card JavaScript and manifest version. Their Python backend is identical to restart-tested v0.2.0. Each HACS installation received an immediate successful UI configuration check. The final check passed around 03:03 UTC; browser reload activated the v0.2.2 card. The backend also survived the other household task's coordinated restart ending around 03:00 UTC.
- Stable tag `stable/20260929T030600Z` identifies the exact proven component candidate, with the backend restart and final frontend refresh distinguished in its evidence. Documentation was committed afterward.

## Live behavior

- Coast's Tides view renders real Provincetown NOAA predictions, high/low labels, sunrise/sunset lines, subtle nighttime shading, the current height and a moving Now marker. All original 20 sensor/calendar/image entities remain present; prediction status was fresh.
- From Monday's initial current-time view, Next settles on Tuesday, Previous returns to Monday, and Now returns to the current tide with context. This catches the native scroll-snap timing issue fixed in v0.2.2.
- Tapping the curve displays a timestamp and interpolated height; dragging moves the tide curve and forecast columns together. Native proximity snapping remains available during manual scrolling. A stationary tap does not unexpectedly change the scroll position.
- Expanded weather uses live `weather.coast_weather` hourly forecasts: Tuesday midnight showed rain, 61°F, 10 mph and 63%; 04:00 showed wind, 58°F, 18 mph and 19%; 08:00 showed clouds, 59°F, 14 mph and 0%. Past hours omitted by the provider display dashes. Real Home Assistant icons render in production.
- Desktop visuals were checked in live HA. The local preview was inspected at 320- and 390-pixel widths, with no page overflow. The coordinated Coast layout task separately verified the installed card at 390×844 with document width remaining 390 pixels and expansion working. Its detailed record lives in the house configuration repository. Local preview weather is explicitly simulated and was not used as evidence of live forecast data.
- Filtered Core logs for `custom_components.tideglass` showed no issues after the final update. Existing unrelated integration warnings/errors remain outside this scope.

## Automated checks and limits

38 Python tests and 5 JavaScript tests passed, plus Ruff and diff checks. Tests cover real HA setup, authenticated WebSocket permissions, static asset serving, bounded samples, expiry, DST and polar solar conditions, interpolation gaps, forecast horizons, valid zero values, escaping, stationary taps and day navigation. Final release CI passed both [tests](https://github.com/andrewyoung918/ha-tideglass/actions/runs/36514890533) and [HACS/hassfest validation](https://github.com/andrewyoung918/ha-tideglass/actions/runs/36514890538).

Keyboard navigation and responsive layout were exercised in the browser preview. Physical phone touch gestures, forced live provider outages, long-term operation, other stations and live DST rollover were not tested on the household. Their relevant data behavior has automated coverage. No household devices were actuated as test probes.

The installation preserved the existing managed house YAML and unrelated work. Coast layout changes were handled by its coordinated task through the supported dashboard editor. Recovery snapshots and exact hashes are retained privately outside Git; the preceding release can be restored through HACS.
