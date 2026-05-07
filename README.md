# IdeaGen Pro (AI Business Idea SaaS)

IdeaGen Pro is a subscription-gated SaaS app that generates AI business ideas in real time.

It uses:
- a Next.js frontend (`pages` router) for UI and auth-aware navigation
- Clerk for authentication and subscription enforcement
- a FastAPI backend endpoint that streams model output over SSE

https://saas-bexi3k909-adarshkumar124-8995s-projects.vercel.app/

## What This App Does

- Landing page (`/`) with sign-in and upgrade messaging
- Product page (`/product`) protected by Clerk billing plan checks
- Live streaming idea generation rendered as Markdown
- Clerk user session and JWT used to authorize backend calls

## Tech Stack

### Frontend
- Next.js `16.x` (Pages Router)
- React `19.x`
- TypeScript
- Tailwind CSS `4.x`
- `@clerk/nextjs` for auth, user UI, and plan protection
- `@microsoft/fetch-event-source` for SSE stream consumption
- `react-markdown` + `remark-gfm` + `remark-breaks` for formatted model output

### Backend
- FastAPI (Python)
- `fastapi-clerk-auth` for validating Clerk JWTs
- OpenAI SDK (configured with GitHub Models Azure endpoint)
- Streaming response via `text/event-stream`

## Repository Structure

```text
.
├── api/
│   └── index.py            # FastAPI app with authenticated SSE endpoint at /api
├── pages/
│   ├── _app.tsx            # Wraps app with ClerkProvider
│   ├── _document.tsx       # HTML shell metadata
│   ├── index.tsx           # Marketing/landing page
│   └── product.tsx         # Protected product experience + stream rendering
├── styles/
│   └── globals.css         # Tailwind + Markdown output styles
├── requirements.txt        # Python dependencies
└── package.json            # Node dependencies and scripts
```

## Prerequisites

- Node.js `>=20`
- npm `>=10`
- Python `>=3.10`
- Clerk account (for auth + billing plans)
- GitHub token with model inference access (used by backend OpenAI client config)

## Environment Variables

This project currently uses both frontend (`.env.local`) and backend (`.env`) environment files.

### Frontend (`.env.local`)

Required for Next.js + Clerk:

```bash
CLERK_PUBLISHABLE_KEY=...
CLERK_SECRET_KEY=...
```

### Backend (`.env`)

Required for FastAPI auth + model access:

```bash
CLERK_JWKS_URL=...
GITHUB_TOKEN=...
```

Notes:
- `CLERK_JWKS_URL` should point to your Clerk JWKS endpoint.
- `GITHUB_TOKEN` is used by the backend model client (`OpenAI(...)`) with `base_url="https://models.inference.ai.azure.com"`.
- Do not commit real keys/tokens.
- If secrets were ever committed locally, rotate them immediately.

## Local Development Setup

## 1) Install frontend dependencies

```bash
npm install
```

## 2) Install backend dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3) Configure environment variables

- Create/update `.env.local` for Next.js + Clerk keys.
- Create/update `.env` for backend variables.

## 4) Run the frontend

```bash
npm run dev
```

Frontend runs at [http://localhost:3000](http://localhost:3000).

## 5) Run the backend

In a second terminal:

```bash
source .venv/bin/activate
uvicorn api.index:app --reload --port 8000
```

Backend runs at [http://localhost:8000](http://localhost:8000) by default.

Important:
- The UI currently calls `fetchEventSource('/api', ...)` from the browser.
- In local dev, ensure your runtime/proxy setup routes `/api` requests to FastAPI, or update the frontend call to point to your backend origin directly.

## Clerk Configuration Checklist

To make auth + subscription protection work end to end:

- Create Clerk application and copy publishable/secret keys
- Enable sign-in methods used by your app
- Create billing plan matching the `Protect` plan identifier used in `pages/product.tsx`
- Confirm JWT template/issuer is compatible with your FastAPI Clerk guard
- Set `CLERK_JWKS_URL` in backend environment

If the plan ID in your Clerk dashboard differs from the hardcoded value in `pages/product.tsx`, update the code or plan slug so they match.

## How Request Flow Works

1. User signs in via Clerk on the frontend.
2. User navigates to `/product`.
3. `Protect` checks active subscription plan.
4. If allowed, `IdeaGenerator` fetches a Clerk JWT via `getToken()`.
5. Frontend calls `/api` with `Authorization: Bearer <jwt>`.
6. FastAPI validates JWT (`fastapi-clerk-auth`).
7. Backend starts model stream and emits SSE chunks.
8. Frontend appends streamed chunks and renders Markdown output live.

## Available Scripts

From `package.json`:

- `npm run dev` - start Next.js dev server
- `npm run build` - create production build
- `npm run start` - run production Next.js server
- `npm run lint` - run ESLint

## API Notes

### `GET /api` (FastAPI)

- Requires Bearer token issued by Clerk
- Streams content as `text/event-stream`
- Current prompt: asks model for a business idea formatted with headings/subheadings/bullets

Potential production improvements:
- add explicit rate limits per user
- persist generations per user
- improve stream framing for multiline markdown fidelity
- structured error events for client UX

## Deployment Notes

This repo combines a Next.js app and a FastAPI service.

You can deploy in two common ways:
- **Single platform with routing**: deploy both services and route `/api` to FastAPI
- **Split services**: deploy frontend and backend separately, then call backend via full URL and CORS config

Before production:
- rotate and secure all secrets
- enable monitoring/logging
- set up proper CORS and trusted origins
- verify Clerk production keys, domains, and billing config

## Troubleshooting

- **`Authentication required` in UI**
  - User is not signed in or token fetch failed.
  - Verify Clerk keys and session state.

- **`401/403` from backend**
  - JWT verification failed.
  - Check `CLERK_JWKS_URL` and token issuer/audience assumptions.

- **No stream appears on `/product`**
  - `/api` may not be routed to FastAPI in local setup.
  - Confirm backend is running and frontend is calling correct origin.

- **Plan-gated content always blocked**
  - `Protect` plan string does not match Clerk billing plan identifier.

- **Model call errors**
  - Verify `GITHUB_TOKEN` availability and model access (`gpt-4o-mini`).

## Security Reminder

- Never commit `.env` or `.env.local` with real credentials.
- Use distinct keys for dev/staging/prod.
- Rotate any leaked or previously exposed secrets immediately.
