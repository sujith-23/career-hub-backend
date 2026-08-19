# Career Vision Hub — Backend

FastAPI backend for the Career Vision Hub (Disha career guide) frontend.
Replaces the hardcoded `DATA` JS object with a real content API, and adds
click tracking + a student feedback endpoint.

## What's here

- `GET /api/streams` — list of all 11 streams (mpc, bipc, mec, cec, hec,
  polytechnic, iti, vocational, skilldev, defence, govtjobs)
- `GET /api/streams/{id}` — full detail for one stream (paths + children),
  same shape as the old `DATA[streamId]`
- `POST /api/track` — log a click (stream/path/node) for analytics
- `GET /api/analytics/popular` — most-clicked streams
- `POST /api/feedback` — student submits a question/message
- `GET /api/feedback` — list submitted feedback (add auth before exposing publicly)

Interactive API docs at `/docs` once running.

## Run locally

```bash
cd backend
pip install -r requirements.txt
python -m app.seed        # loads data/seed_data.json into SQLite (career_hub.db)
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs to try it out.

## Data source

`data/seed_data.json` was extracted directly from the `DATA` object in
`disha-career-guide-2.html`, so all 11 streams and their paths/children are
already there. To edit content, either:
- edit `data/seed_data.json` and re-run `python -m app.seed`, or
- write directly to the database once you build an admin UI

## Connecting the frontend

In the HTML file, replace the hardcoded `const DATA = {...}` block with a
fetch call, e.g.:

```js
let DATA = {};
async function loadData() {
  const res = await fetch('https://your-api-url/api/streams'); // list
  const streams = await res.json();
  for (const s of streams) {
    const detail = await fetch(`https://your-api-url/api/streams/${s.id}`);
    DATA[s.id] = await detail.json();
  }
  renderApp(); // whatever kicks off your existing render logic
}
loadData();
```

Or simpler: just add one endpoint that returns everything at once if you'd
rather not do 11 extra requests — happy to add a `GET /api/streams/full`
that returns the whole DATA object in one call if you prefer that.

Add a track call wherever the frontend currently handles a node click:

```js
fetch('https://your-api-url/api/track', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({stream_id: streamId, path_id: pathId, node_id: nodeId})
});
```

## Deploying (Docker + Azure Container Apps)

Same pattern as your CodeTutor project:

```bash
docker build -t career-hub-api .
docker run -p 8000:8000 career-hub-api
```

For production, set `DATABASE_URL` to a Postgres connection string (Azure
Database for PostgreSQL is fine) instead of the default SQLite file, since
Container Apps' filesystem isn't persistent across restarts:

```bash
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
```

Then push the image and deploy to Azure Container Apps as usual. Update the
`allow_origins` in `app/main.py` from `"*"` to your GitHub Pages URL
(`https://sujith-23.github.io`) before going live.
