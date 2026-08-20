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

## Login + saved paths (Firebase Auth)

Students can now log in / sign up (Firebase Authentication, same pattern as
Career Vision Hub) and bookmark career paths. The backend verifies the
Firebase ID token to know which user is saving what — it never sees passwords.

### Backend setup

1. In the [Firebase console](https://console.firebase.google.com), open your
   project (or create one) → **Project settings** → **Service accounts** →
   **Generate new private key**. This downloads a JSON file.
2. Save it as `backend/firebase-service-account.json` (already gitignored —
   never commit this file, it's a secret credential).
3. In the Firebase console, go to **Authentication** → **Sign-in method** →
   enable **Email/Password**.
4. Install the new dependency: `pip install -r requirements.txt` (already
   includes `firebase-admin`).
5. Restart the server. `/api/saved-paths` endpoints now work.

### Frontend setup

1. In the Firebase console → **Project settings** → **General** → scroll to
   "Your apps" → add a Web app (or reuse the one from Career Vision Hub).
2. Copy the `firebaseConfig` object it gives you.
3. In `disha-career-guide-connected.html`, find the `firebaseConfig` block
   near the bottom of the `<script>` and paste your real values in place of
   the `YOUR_...` placeholders.
4. Reload the page — "Log in" / "Sign up" buttons appear top-right. After
   logging in, visiting any final career page shows a "Save this path"
   button, and "My saved paths" lists everything you've bookmarked.

### New endpoints (all require `Authorization: Bearer <firebase_id_token>`)

- `POST /api/saved-paths` — bookmark a path
- `GET /api/saved-paths` — list the logged-in user's bookmarks
- `DELETE /api/saved-paths/{id}` — remove a bookmark

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
