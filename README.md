# PowderMonitor

Small practice projects, published with GitHub Pages.

- **Hello World** (`index.html`): 7-day weather forecast for Salzburg.
- **Powder Monitor** (`powder-monitor/`): "should I go?" verdicts for **snowboarding, surfing and kitesurfing**.
  - **Sport switch** at the top: Snowboard / Surf / Kite.
  - **Level switch** (Beginner / Intermediate / Advanced, saved per sport) changes what counts as a good day: e.g. waist-high waves are perfect for a beginner and boring for an advanced surfer; an off-piste day needs fresh snow *and* enough base.
  - **Plain-language verdict** ("Send it", "Fun waves", "Marginal", "Skip it") with ✅ / ⚠️ / ❌ reasons, plus a details panel for experienced riders (base depth, freezing level, storm flow; wave period, swell angle vs. beach, onshore/offshore/chop; wind, gusts, side-on/offshore, kite size, wetsuit).
  - **Location**: auto-detected on first visit, "Locate me", place search, or tap the map → *Start from here*. Tap the map → *Check conditions here* to get a verdict for any point (set the shore direction for wind advice).
  - Week strip, top spots, interactive map, ranking bars and a full table, all for the selected day.
  - Ski resorts: `powder-monitor/resorts.json`. Surf and kite spots: `powder-monitor/spots.json`. Edit those to add spots.
  - Data: [Open-Meteo](https://open-meteo.com/) weather + marine APIs (no key needed). Map: Leaflet + OpenStreetMap/CARTO tiles.

Planned: Telegram bot you can ask ("how's the weekend for snowboarding?").
