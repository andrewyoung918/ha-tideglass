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

## Current weather header, v0.2.3

Candidate `472ec2d0523fd6dda20d5c7b6095f77c31ab9e76` pairs the current tide at left with current condition icon, temperature and label at right. It uses current weather entity state and updates with HA state changes; forecast subscription failure does not hide valid current conditions.

- Preview checked at 1280, 390 and 320 pixels. The tide and temperature bounding boxes had identical vertical positions. At 390/320, document width equaled viewport width. Unavailable current weather displayed a dash and explicit label; expansion remained usable. Preview readings were simulated.
- HACS installation completed September 29 around03:15UTC; baseline and immediate post-install HA UI configuration checks passed. All18 live component files exactly match the candidate. Browser refresh activated this frontend-only update; no backend change or Core restart.
- Live Coast displayed a rising7.1ft tide and rainy62°F weather side by side. No Tideglass browser errors were captured. User's open Coast tab was refreshed. Five existing JS tests, syntax, Ruff and diff checks passed locally; release Test and HACS/hassfest CI passed.
- Stable tag `stable/20260929T031702Z` records this scoped frontend verification. Exact preceding two-file snapshot and final hashes remain outside Git in `.local/backups/0.2.2-before-current-weather-header/`. Recovery is HACS v0.2.2, configuration check, then browser refresh. Physical phone hardware and long-term operation were not tested for this small update.

## Rendering compatibility, v0.2.4

A user reported an interactive-card rendering error. All four Coast tabs, a fresh Tides load and scoped integration logs were healthy in the available Chromium browser; the affected device and exact message remain unconfirmed. Inspection and a controlled test did identify a separate concrete compatibility failure: removing `Array.prototype.at` made the original curve renderer throw `TypeError: segment.at is not a function`. The fetch catch then misclassified the render failure as unavailable tide predictions. Previous-day navigation also depended on `toReversed`.

Candidate `ecf871b257eeadf6bedd7c76777c148433d57cb7` replaces those operations with indexing and copying/reversing the small day list. A regression test disables both methods and exercises rendering and previous-day navigation. The complete NOAA fixture produces byte-identical SVG before and after the change, with those methods disabled for the new renderer. See the platform compatibility references for [Array.at](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/at) and [Array.toReversed](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/toReversed).

- Installed through HACS as v0.2.4 after baseline UI validation; immediate post-install configuration check passed around 03:52 UTC, September 29. All 18 installed files match the candidate. Only JavaScript and the manifest version changed; browser refresh activated it without a Core restart.
- Live card displayed rising 8.4 ft and rainy 62°F. Next settled on Tuesday, Previous returned Monday, Now restored current time, and expansion showed actual hourly weather. No Tideglass browser errors were captured.
- Six JavaScript tests, syntax, Ruff and diff checks passed locally. CI Test and HACS/hassfest passed. The supported-browser baseline was visually verified; the compatibility regression uses controlled feature removal, not physical legacy-device testing.
- Stable tag `stable/20260929T035352Z` identifies the tested candidate. Recovery files and final hashes: `.local/backups/0.2.3-before-rendering-compatibility/`. HACS v0.2.3 plus immediate check and browser refresh restores the preceding release.
- The specific user-reported error is **not yet confirmed resolved on the affected device**. A refresh/reopen is needed to load the patch, followed by confirmation or the exact error text if it persists.

## Coast distillation candidate, 2026-09-29

Component candidate `dbb01a20c57c2ba7284316811675fa4b9fd07dbe` (manifest 0.2.5) is published to the default source branch, **not yet released or installed through HACS**. The local reviewed source commit `df6e28d` has the identical full tree. GitHub CLI credentials failed; the GitHub connector published the exact tree, and a browser sign-in is pending for release publication. The unpublished local release tag was preserved as `candidate/0.2.5-local`; no v0.2.5 release tag currently exists.

The candidate removes the branding eyebrow and introductory sentence, defaults to the station name as its single heading, retains side-by-side tide/current weather, labels the expansion control Forecast at phone widths, hides the empty inspection readout, and moves datum/time-zone/forecast explanation into a keyboard-accessible Details disclosure. Cached/unavailable warnings remain visible when applicable.

- Six existing JavaScript tests, syntax, Ruff and diff checks passed. All nine Coast dashboard templates compile. The Impeccable detector returned no findings.
- Local preview inspected at 1280 and 390 pixels, with a 320-pixel overflow check. Widths remained bounded; forecast expansion, unavailable weather, and Details opening worked. Preview weather is simulated. Resizing rebuilds the card and closes Details, consistent with other transient inspection state.
- GitHub [Test](https://github.com/andrewyoung918/ha-tideglass/actions/runs/36636567855) and [Integration validation](https://github.com/andrewyoung918/ha-tideglass/actions/runs/36636568129) passed for the published candidate.
- Private recovery snapshot of live v0.2.4's two affected files and hashes is in `.local/backups/0.2.4-before-coast-distill/`; the release ZIP in `.local/releases/tideglass.zip` contains all 18 tracked component files.
- Coast dashboard YAML was separately saved through the supported raw editor and read back exactly (parsed). It removes the external hero, duplicate tide-status panel and long caveat panel, and compacts the next high/low and weekly table. Other views are unchanged. House record documents its candidate and source backup.
- Fresh-tab live verification exposed an intermittent pre-existing card loading failure: an initial load showed Configuration error, a refresh rendered the current v0.2.4 card, and subsequent fresh reloads failed again. The existing user tab continued rendering. The static module returned HTTP 200 and exactly matched v0.2.4. No Tideglass-specific console error was captured; unrelated missing HACS resources and a Home Assistant back-button `_localize` error were visible. One explicit dashboard module resource at the same bundled URL was added through the UI, but **did not establish a fix**. Do not claim the earlier user-reported rendering error is resolved.

Next: complete GitHub sign-in, publish v0.2.5 from `dbb01a2` with the prepared ZIP, coordinate the HA writer, install through HACS, immediately check configuration, refresh and verify the new card. Investigate the fresh-load error before any stable tag. No new stable tag has been created.

## Concise header applied locally, September 29, 22:35 UTC

The pending card was applied through an explicitly extended and tested canonical sync workflow, without requiring GitHub release authentication. The final component candidate is `b920c860cb5d1cd97e3a7cadb835e74fbb72b870`. All 18 installed component files match this commit. Only the JavaScript and version-only manifest metadata differ from v0.2.4; no Python change or Core restart was required.

The canonical workflow extension runs only from clean committed checkouts, verifies every tracked component file against the checkpoint, allows only the card JavaScript and manifest version, rejects symlinks/drift/backend edits, backs up all affected bytes before writing and restores on partial copy failure. All 17 workflow safety tests passed, including the injected partial failure and recovery-conflict cases. Its source is in the house repository; existing managed YAML checks remain intact.

Both incremental copies received an immediate successful HA Tools → YAML → Check configuration. The dashboard resource is `/tideglass/tideglass-card.js?v=0.2.5&build=1`. The card now upgrades the compatible existing 0.2.x element's prototype when the integration's older cached URL registers first, with a monotonically increasing frontend revision that prevents downgrading newer code. The regression test covers this coexistence; all seven JavaScript tests, syntax, Ruff and diff checks passed.

Browser-wrapper reloads initially continued displaying old content. A native browser reload finally loaded the patch; verification used the actual rendered DOM and screenshots, not just copied bytes. The user tab at 390 pixels and a fresh desktop tab both showed the single Provincetown heading, current tide at left, weather at right and Forecast control. Neither slogan nor branding eyebrow remained. Forecast expansion displayed 42 aligned four-hour columns, Details opened/closed, Next settled on Wednesday, Now returned to current context, and keyboard inspection produced a dated tide height. No Tideglass-specific browser error was captured in the fresh final tab. This verifies these sessions; it does not establish long-term or physical legacy-device reliability.

Recovery journals remain in the clean canonical worktree at `.local/worktrees/tideglass-frontend-sync/.local/backups/component-1790720594373817000/` (v0.2.4 → concise UI) and `component-1790720860550352000/` (cache coexistence patch). To return all the way to v0.2.4, roll back the latter then the former using that worktree's `scripts/sync.py component-rollback`, check configuration, restore the prior resource URL and refresh.

HACS release publication remains pending. Its downloaded-release bookkeeping still says v0.2.4; installed files are the verified local 0.2.5 candidate. Do not redownload v0.2.4 unless intentionally rolling back. Publish the latest component source as the future release rather than the earlier prepared ZIP, which predates the cache coexistence change.
