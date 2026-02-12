# Prompt Reverse Engineer Frontend

React + Vite + TypeScript + Tailwind UI for the Prompt Reverse Engineer API.

## Setup

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Default app URL: `http://localhost:5173`.

## Environment

- `VITE_API_BASE_URL` (default: `http://localhost:8000`)
- `VITE_API_TIMEOUT_MS` (default: `20000`)

## Scripts

- `npm run dev` - run dev server
- `npm run build` - build for production
- `npm run preview` - preview production build
- `npm run lint` - lint frontend project

## Features

- Large paste-first input area and keyboard-friendly form submit
- Analyze button with loading spinner
- Error state and retry action
- Results panel with:
  - inferred prompt + copy button
  - prompt style badge
  - task type
  - confidence score meter
  - explainability section
  - constraints list
  - expandable reasoning trace
  - cache indicator
  - request ID
- Raw JSON view toggle
- Mobile responsive layout
- Dark mode support
