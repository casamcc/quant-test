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
