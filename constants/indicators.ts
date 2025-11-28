import { IndicatorData } from '@/types';

export const INDICATORS_DATA: IndicatorData[] = [
    {
        id: 'ro-1',
        phase: 'RISK-ON (Entry)',
        category: 'Technical Indicators',
        name: 'Daily RSI Divergence',
        logic: 'Price makes a lower low, but momentum (RSI) makes a higher low.',
        trigger: 'Daily RSI < 30 then creates Higher Low while price is making a lower low',
        weight: 10,
        reliability: 'B-Tier'
    },
    {
        id: 'ro-2',
        phase: 'RISK-ON (Entry)',
        category: 'Correlation',
        name: 'Outperform S&P500',
        logic: 'Daily Bitcoin price when outperform against the S&P 500 price, it shows liquidity is moving into crypto',
        trigger: 'Daily Bitcoin price > S&P 500 price consecutively in the last 3 days',
        weight: 15,
        reliability: 'B-Tier'
    },
    {
        id: 'ro-3',
        phase: 'RISK-ON (Entry)',
        category: 'Sentiment',
        name: 'Crypto F&G Index',
        logic: 'Fear and Greed Index when show at extreme levels <20 or >75 implies crypto market is oversold or overbought',
        trigger: 'When Fear and Greed Index <20 for more than 1 month, it\'s a signal that Bitcoin is over sold',
        weight: 5,
        reliability: 'B-Tier'
    },
    {
        id: 'ro-4',
        phase: 'RISK-ON (Entry)',
        category: 'Correlation',
        name: 'MSTR Outperform S&P500',
        logic: 'Daily MSTR price when outperform against the S&P 500 price, it shows liquidity is moving into crypto',
        trigger: 'Daily MSTR price > S&P 500 price consecutively in the last 3 days',
        weight: 20,
        reliability: 'S-Tier'
    },
    {
        id: 'roff-1',
        phase: 'RISK-OFF (Exit)',
        category: 'Technical Indicators',
        name: 'Weekly RSI Divergence',
        logic: 'Weekly RSI Divergence',
        trigger: 'Weekly RSI > 70 then creates lower high while price is making a higher high',
        weight: 20,
        reliability: 'S-Tier'
    }
];
