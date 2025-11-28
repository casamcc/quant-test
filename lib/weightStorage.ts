/**
 * Weight Storage Utility
 * Manages persistence of custom indicator weights in localStorage
 */

const STORAGE_KEY = 'crypto-tracker-weights';

export interface WeightMap {
    [indicatorId: string]: number;
}

/**
 * Save a single indicator weight to localStorage
 */
export function saveWeight(id: string, weight: number): void {
    try {
        const weights = loadWeights();
        weights[id] = weight;
        localStorage.setItem(STORAGE_KEY, JSON.stringify(weights));
    } catch (error) {
        console.error('Failed to save weight:', error);
    }
}

/**
 * Load all saved weights from localStorage
 */
export function loadWeights(): WeightMap {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        return stored ? JSON.parse(stored) : {};
    } catch (error) {
        console.error('Failed to load weights:', error);
        return {};
    }
}

/**
 * Reset a single indicator weight to default (remove from storage)
 */
export function resetWeight(id: string): void {
    try {
        const weights = loadWeights();
        delete weights[id];
        localStorage.setItem(STORAGE_KEY, JSON.stringify(weights));
    } catch (error) {
        console.error('Failed to reset weight:', error);
    }
}

/**
 * Clear all custom weights
 */
export function resetAllWeights(): void {
    try {
        localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
        console.error('Failed to reset all weights:', error);
    }
}

/**
 * Check if a weight has been customized
 */
export function isWeightCustomized(id: string): boolean {
    const weights = loadWeights();
    return id in weights;
}

// ============================================
// Deleted Indicators Management
// ============================================

const DELETED_KEY = 'crypto-tracker-deleted';

/**
 * Save a deleted indicator ID
 */
export function saveDeletedIndicator(id: string): void {
    try {
        const deleted = loadDeletedIndicators();
        if (!deleted.includes(id)) {
            deleted.push(id);
            localStorage.setItem(DELETED_KEY, JSON.stringify(deleted));
        }
        // Also clean up the weight for this indicator
        resetWeight(id);
    } catch (error) {
        console.error('Failed to save deleted indicator:', error);
    }
}

/**
 * Load all deleted indicator IDs
 */
export function loadDeletedIndicators(): string[] {
    try {
        const stored = localStorage.getItem(DELETED_KEY);
        return stored ? JSON.parse(stored) : [];
    } catch (error) {
        console.error('Failed to load deleted indicators:', error);
        return [];
    }
}

/**
 * Restore a single deleted indicator
 */
export function restoreIndicator(id: string): void {
    try {
        const deleted = loadDeletedIndicators();
        const filtered = deleted.filter(deletedId => deletedId !== id);
        localStorage.setItem(DELETED_KEY, JSON.stringify(filtered));
    } catch (error) {
        console.error('Failed to restore indicator:', error);
    }
}

/**
 * Restore all deleted indicators
 */
export function restoreAllIndicators(): void {
    try {
        localStorage.removeItem(DELETED_KEY);
    } catch (error) {
        console.error('Failed to restore all indicators:', error);
    }
}
