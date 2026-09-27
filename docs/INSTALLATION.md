# Install and verify

Tideglass is distributed as a HACS custom repository. Version 0.1.0 was installed through HACS and verified on Home Assistant 2026.9.3 on September 27, 2026; see `VERIFICATION.md`.

## HACS distribution

Add `https://github.com/andrewyoung918/ha-tideglass` in HACS → Custom repositories → Integration. Download Tideglass. Follow the configuration-check and restart gates below before activation. HACS default-store listing is a separate submission; this project does not claim that listing.

Alternatively, the release ZIP contains `custom_components/tideglass`. Install that folder under Home Assistant’s `custom_components` using the established deployment workflow. Do not copy tests, documentation, or the development environment to the server.

## Andrew’s installation gate

The source lives at `/Users/andrew/Development/ha-tideglass`; house configuration remains at `/Users/andrew/Development/home-assistant-config`. Unfinished automation/script edits there must be preserved.

Before live installation, complete the repository’s safe-deployment procedure, including a recent native backup, off-device copy, encryption-key access, working UI/admin session, and Core recovery route. The current managed-file sync tool only handles existing YAML paths; do not bypass it with an ad hoc component copy. Install through HACS after publishing, or explicitly extend and test the canonical sync workflow for new integration files and their rollback before deploying manually.

Immediately after files are installed, use Tools → YAML → Check configuration. Roll back the affected integration files on a failed or inconclusive check. Only after a successful check restart Core, then verify all 20 entities, the image endpoint, calendar and logs. No stability tag is justified by local tests.

## Set up a station

Settings → Devices & services → Add integration → Tideglass. Defaults: Provincetown `8446121`, feet, `America/New_York`. Other NOAA prediction stations need their own seven-digit ID and IANA time zone. Units and time zone can be changed in the integration options. Add a new integration entry for another station.

## Dashboard

For the navy, seafoam and gold design, follow the [styled dashboard guide](DASHBOARD.md) and use `examples/weather-dashboard-aesthetic.yaml`. The instructions below describe the simpler native-card alternative.

Create a new empty dashboard from Settings → Dashboards. Open its raw configuration editor and use `examples/weather-dashboard.yaml`. The current weather entity `weather.kpvc` was verified in the live entity registry as the existing NWS “Provincetown Weather” entity. That integration supports hourly and twice-daily forecasts; the YAML uses those supported modes.

Verify the newly created Tideglass entity IDs before saving if HA adds suffixes or the device was renamed. The dashboard uses native cards only. Windy’s official embeds provide separate radar and wind maps. The map URLs are centered on public Provincetown coordinates. Radar data availability and map interactions depend on Windy.

The optional theme is in `examples/coast-theme.yaml`. Add it using the canonical managed-config workflow, reload themes, and select it for the dashboard. To use light graphs, replace the two image entity suffixes `_dark` with `_light`.

Verify desktop and phone layouts, all forecasts, map load and animation, graph timestamp refresh, a sample calendar event, and the timestamp/height entities in Tools → States. Do not enable example automations just to test the dashboard.

## Remove

Remove the Tideglass config entry through Devices & services; its integration-owned prediction cache is removed. Then uninstall through HACS and restart when prompted. Restore the previous dashboard configuration through its supported editor. Never edit `.storage` by hand.
