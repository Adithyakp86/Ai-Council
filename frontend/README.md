# AI Council Frontend

Next.js 14 frontend for the AI Council web application.

## Setup

1. Install dependencies:
```bash
npm install
# or
yarn install
# or
pnpm install
```

2. Copy `.env.local.example` to `.env.local` and configure:
```bash
cp .env.local.example .env.local
```

3. Start the development server:
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Project Structure

```
frontend/
├── app/              # Next.js 14 App Router pages
├── components/       # React components
├── lib/              # Utility functions
├── hooks/            # Custom React hooks
├── types/            # TypeScript type definitions
├── public/           # Static assets
└── package.json      # Dependencies
```

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (Radix UI)
- **State Management**: Zustand
- **Data Fetching**: React Query
- **WebSocket**: Native WebSocket API

## Development

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Building for Production

```bash
npm run build
npm run start
```

## Deployment

This project is optimized for deployment on Vercel. Simply connect your GitHub repository to Vercel and it will automatically deploy on every push to the main branch.
