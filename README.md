# Crypto Cycle Signal Tracker

Manual Bitcoin market cycle analysis and signal tracking application built with Next.js 15.

## Features

- 📊 **Multi-Phase Tracking**: Monitors indicators across 4 market phases (Risk-On, Hold, Risk-Off, Wait)
- ✅ **Manual Assessment**: Mark indicators as triggered or not based on your research
- 🎯 **Weighted Scoring**: Automatic score calculation based on indicator weights
- 🎨 **Notion-Inspired UI**: Clean interface with smooth animations
- 💾 **Persistent Storage**: Your assessments and customizations are saved locally

## Getting Started

### Prerequisites

- Node.js 18+

### Installation

1. Clone the repository and install dependencies:

```bash
npm install
```

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

```bash
npm run build
npm start
```

## Project Structure

```
├── app/
│   ├── layout.tsx        # Root layout
│   ├── page.tsx          # Main application page
│   └── globals.css       # Global styles
├── components/           # React components
│   ├── PhaseCard.tsx     # Phase indicator card
│   └── SummarySection.tsx # Summary dashboard
├── lib/                  # Utilities
│   └── weightStorage.ts  # LocalStorage management
├── types/                # TypeScript type definitions
├── constants/            # Application constants
└── next.config.ts        # Next.js configuration
```

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Storage**: Browser LocalStorage

## License

MIT
