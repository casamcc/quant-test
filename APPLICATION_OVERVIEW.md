# Application Overview: Crypto Cycle Signal Tracker

## 🎯 Purpose
This is a **Manual Bitcoin Market Cycle Checklist & Scoring System** - a sophisticated dashboard application that helps traders make informed decisions about when to enter or exit the Bitcoin market through systematic manual analysis.

## 🔧 Core Functionality

**Features:**
1. **Indicator Library** - A database of market indicators with their logic, trigger conditions, and weights
2. **Manual Checklist System** - Traders manually check off indicators as triggered/not triggered
3. **Weighted Scoring Calculator** - Automatically calculates scores for each phase based on which indicators are checked
4. **Phase-based Organization** - Indicators organized into 4 market phases (Entry, Hold, Exit, Wait)
5. **Customization** - Add/edit/delete indicators, adjust weights based on personal preference
6. **Visual Dashboard** - Clean UI to view and manage indicators by phase
7. **Local Storage** - Saves your preferences and indicator states

## 🔄 User Workflow
1. Open the dashboard
2. Research current market conditions yourself (using TradingView, Glassnode, etc.)
3. Manually check each indicator - mark as triggered or not triggered
4. App calculates weighted scores for each phase
5. Review scores to understand which phase has strongest signal
6. Make trading decision based on scores following the logic rules:
   - Risk-Off > 75 → Consider selling
   - Risk-On > 65 → Consider buying
   - Stay Risk-On > 50 → Consider holding
   - Stay Risk-Off > 50 → Consider waiting

## 💡 What This Application Is
**A structured checklist app for tracking Bitcoin market signals with automatic score calculation.**

Think of it as:
- Notion database + weighted scoring calculator
- Digital version of a trader's manual checklist
- Portfolio management tool for systematic decision-making
- Personal trading journal with built-in scoring logic

## ✨ Advantages

- ✅ No API costs
- ✅ Complete control over assessments
- ✅ No external dependencies
- ✅ Privacy - all data stays local
- ✅ Instant updates (no API calls)
- ✅ Customizable indicator library

## 📋 Market Phases

The application tracks indicators across **4 distinct market phases**:
1. **RISK-ON (Entry)** - Signals to BUY/Enter Bitcoin positions
2. **STAY RISK-ON (Hold)** - Signals to HOLD existing positions
3. **RISK-OFF (Exit)** - Signals to SELL/Exit positions
4. **STAY RISK-OFF (Wait)** - Signals to wait in cash

## 📊 How It Works

### 1. Indicator System
Each indicator has:
- A **category** (Technical Indicators, Correlation, Sentiment)
- A **logic** (explanation of what it measures)
- A **trigger condition** (when it signals entry/exit)
- A **weight** (importance/reliability score, 0-100)
- A **reliability tier** (S-Tier, B-Tier, etc.)

### 2. Manual Assessment
- Research current market conditions using your preferred sources (TradingView, Glassnode, etc.)
- Mark indicators as "Active" or "Inactive" based on whether trigger conditions are met
- Optionally enter current values for reference

### 3. Automatic Scoring
- For each phase, the app calculates a score by summing the weights of all triggered indicators
- Higher scores = stronger signal for that phase's action
- Visual progress bars show score relative to total possible weight

### 4. Recommendation Logic
The app follows priority-based decision rules:
1. Risk-Off score > 75 → SELL/HEDGE
2. Risk-On score > 65 → BUY
3. Stay Risk-On score > 50 → HOLD
4. Stay Risk-Off score > 50 → WAIT/CASH

## 🎨 User Interface

**Notion-Inspired Design:**
- Clean, minimalist interface
- Tab-based navigation between phases
- "Board Summary" view shows overview of all phases
- Individual phase tabs show detailed indicators for that phase

**Key Features:**
- Visual score tracking with progress bars
- Toggle indicators active/inactive with one click
- Add/edit/delete custom indicators
- Persistent storage of all customizations (localStorage)
- Adjustable indicator weights

## 🛠️ Technical Stack

**Framework:** Next.js 15 (App Router)  
**Language:** TypeScript  
**Styling:** Tailwind CSS  
**Storage:** Browser LocalStorage  
**Icons:** Lucide React  

**Architecture:**
- Client-side only application (no backend/API calls)
- All data stored locally in browser
- No external dependencies or API keys required
- Fully offline capable after initial load

## 📁 Project Structure

```
├── app/
│   ├── page.tsx          # Main UI (client component)
│   ├── layout.tsx        # Root layout
│   └── globals.css       # Global styles
├── components/
│   ├── PhaseCard.tsx     # Individual phase view with indicators
│   └── SummarySection.tsx # Dashboard summary view
├── lib/
│   └── weightStorage.ts  # localStorage utilities
├── constants/
│   └── indicators.ts     # Initial indicator data
└── types/
    └── index.ts          # TypeScript interfaces
```

## 🔄 Detailed User Workflow

1. **Initial Setup:**
   - Run `npm install` and `npm run dev`
   - No API keys or configuration needed

2. **Daily Usage:**
   - Research current market conditions using your preferred tools
   - Navigate through phase tabs to review indicators
   - Toggle indicators "Active" or "Inactive" based on your analysis
   - Enter current values (optional) for future reference
   - Review calculated scores on the Summary tab
   - Follow the recommendation logic to make trading decisions

3. **Customization:**
   - Adjust indicator weights to match your personal conviction
   - Add custom indicators specific to your strategy
   - Delete irrelevant indicators
   - All changes automatically saved to browser storage

## 💡 Key Features

1. **Systematic Approach:** Structured framework prevents emotional decision-making
2. **Weighted Scoring:** Prioritize indicators based on reliability and importance
3. **Phase-based Organization:** Clear categorization of market cycle stages
4. **Full Customization:** Tailor the system to your trading style
5. **Zero Dependencies:** No API keys, subscriptions, or external services needed
6. **Privacy First:** All data stays in your browser

## 🎯 Target User
Crypto traders and investors who want a systematic, data-driven approach to timing Bitcoin market entries and exits through disciplined manual analysis and structured decision-making.

