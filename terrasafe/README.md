# TerraSafe

TerraSafe is a frontend-only environmental and disaster-risk awareness experience. It turns local signals into a clear area outlook, explains the contributing conditions, lets people explore a rainfall scenario, and offers simple preparedness guidance.

## Run locally

Requirements: Node.js 20.19+ or 22.12+ and npm.

```sh
npm install
npm run dev
```

Create a production build with `npm run build`, or run the linter with `npm run lint`.

## Map configuration

The map uses MapLibre GL JS. Without a key, it uses OpenStreetMap raster tiles and displays an attribution-safe fallback. To enable MapTiler landscape tiles and terrain elevation, create a `.env.local` file in the project root:

```env
VITE_MAPTILER_KEY=your_maptiler_key
```

The app does not display map coordinates to users. Map tile availability depends on the user's connection and configured provider key.

## Frontend architecture

- `src/data/mockData.js` contains example areas, environmental signals, safe zones, timeline points, and risk explanation helpers.
- `src/services/appService.js` contains local persistence and the assessment service boundary for a future API.
- `src/components/TerrainMap.jsx` owns the MapLibre map and its local controls.
- `src/App.jsx` contains the responsive routed app shell and Home, Evaluation, Rescue Hub, My Places, and Settings workflows.
- `localStorage` persists the selected area, saved places, and user settings on this device.

No backend is included. All risk readings, safe-zone information, routes, and timeline values in this preview are mock data. They must not be used for emergency decisions; follow local authority guidance and official alerts.