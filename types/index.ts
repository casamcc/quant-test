export interface IndicatorData {
    id: string;
    phase: string;
    category: string;
    name: string;
    logic: string;
    trigger: string;
    weight: number; // Stored as 0-100
    reliability: string;
    // Dynamic fields
    currentValue?: string;
    isTriggered?: boolean;
}

export interface PhaseScore {
    phase: string;
    score: number;
}

// BasedApp Position Data Types
export interface PositionSummary {
    generated_at: string;
    fetch_date: string;
    fetched_at: string;
    summary: {
        total_users: number;
        users_with_positions: number;
        users_without_positions: number;
        total_positions: number;
        total_position_value: number;
        avg_positions_per_user: number;
    };
    by_coin: CoinPositionData[];
    risk_distribution: Record<string, number>;
    top_positions: TopPosition[];
}

export interface CoinPositionData {
    coin: string;
    count: number;
    total_value: number;
    longs: number;
    shorts: number;
    long_short_ratio: number;
    longs_total_size: number;
    shorts_total_size: number;
    long_short_size_ratio: number;
    longs_unrealized_pnl: number;
    shorts_unrealized_pnl: number;
    total_unrealized_pnl: number;
    total_margin_used: number;
}

export interface TopPosition {
    user_address: string;
    coin: string;
    direction: string; // 'LONG' | 'SHORT' but kept as string for JSON compatibility
    size: number;
    position_value: number;
    unrealized_pnl: number;
    entry_price: number;
    risk_level: string;
    margin_used: number;
}

// Mirrorly Trader Data Types
export interface MirrorlyTrader {
    name: string;
    address: string;
    categories: string[];
    win_rate: number | null;
    wins: number | null;
    losses: number | null;
    total_profit: number | null;
    performance_tier: 'strong' | 'watch' | 'avoid';
    has_positions: boolean;
    num_positions: number;
    account_value: number;
    unrealized_pnl: number;
    top_coins: string[];
}

export interface MirrorldySummary {
    generated_at: string;
    fetch_date: string;
    fetched_at: string;
    summary: {
        total_traders: number;
        traders_with_positions: number;
        total_positions: number;
        category_counts: Record<string, number>;
    };
    traders: MirrorlyTrader[];
    by_performance_tier: {
        strong: MirrorlyTrader[];
        watch: MirrorlyTrader[];
        avoid: MirrorlyTrader[];
    };
}
