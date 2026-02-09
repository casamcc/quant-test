'use client';

import React, { useState } from 'react';
import { Users, TrendingUp, Target, Award, Clock, CalendarDays } from 'lucide-react';
import { MirrorldySummary, MirrorlyTrader } from '@/types';
import clsx from 'clsx';

interface DatasetOption {
    label: string;
    date: string;
    data: MirrorldySummary;
}

interface MirrorlyPositionsProps {
    datasets: DatasetOption[];
}

export const MirrorlyPositions: React.FC<MirrorlyPositionsProps> = ({ datasets }) => {
    const [selectedIndex, setSelectedIndex] = useState(0);
    const [selectedTier, setSelectedTier] = useState<'all' | 'strong' | 'watch' | 'avoid'>('all');
    
    const data = datasets[selectedIndex].data;
    const { summary, traders, by_performance_tier } = data;

    // Get traders based on selected tier
    const displayTraders = selectedTier === 'all' 
        ? traders 
        : by_performance_tier[selectedTier];

    // Format number with commas
    const formatNumber = (num: number | null) => {
        if (num === null) return 'N/A';
        return new Intl.NumberFormat('en-US').format(num);
    };

    // Format currency
    const formatCurrency = (num: number | null) => {
        if (num === null) return 'N/A';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(num);
    };

    // Format date
    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    // Get category badge color
    const getCategoryColor = (category: string) => {
        const lowerCategory = category.toLowerCase();
        if (lowerCategory.includes('god tier')) return 'bg-purple-50 text-purple-700 border-purple-200';
        if (lowerCategory.includes('whale')) return 'bg-blue-50 text-blue-700 border-blue-200';
        if (lowerCategory.includes('veteran')) return 'bg-gray-50 text-gray-700 border-gray-200';
        if (lowerCategory.includes('consistent winner')) return 'bg-green-50 text-green-700 border-green-200';
        if (lowerCategory.includes('winning streak')) return 'bg-emerald-50 text-emerald-700 border-emerald-200';
        if (lowerCategory.includes('heavy drawdown')) return 'bg-orange-50 text-orange-700 border-orange-200';
        if (lowerCategory.includes('negative pnl')) return 'bg-red-50 text-red-700 border-red-200';
        if (lowerCategory.includes('bad kol')) return 'bg-red-50 text-red-700 border-red-200';
        if (lowerCategory.includes('twitter kol') || lowerCategory.includes('kol')) return 'bg-sky-50 text-sky-700 border-sky-200';
        if (lowerCategory.includes('new')) return 'bg-slate-50 text-slate-700 border-slate-200';
        return 'bg-gray-50 text-gray-600 border-gray-200';
    };

    // Get performance tier color
    const getTierColor = (tier: string) => {
        switch (tier) {
            case 'strong':
                return 'bg-green-50 text-green-700 border-green-200';
            case 'watch':
                return 'bg-yellow-50 text-yellow-700 border-yellow-200';
            case 'avoid':
                return 'bg-red-50 text-red-700 border-red-200';
            default:
                return 'bg-gray-50 text-gray-600 border-gray-200';
        }
    };

    // Top categories (limit to top 8)
    const topCategories = Object.entries(summary.category_counts).slice(0, 8);

    return (
        <div className="animate-in fade-in duration-500 pb-20">
            {/* Header */}
            <div className="mb-8">
                <div className="flex items-center justify-between flex-wrap gap-4 mb-2">
                    <h2 className="text-2xl font-bold text-gray-900">Mirrorly Trader Profiles</h2>
                    
                    {/* Date Toggle */}
                    {datasets.length > 1 && (
                        <div className="flex items-center gap-2 bg-gray-100 rounded-lg p-1">
                            <CalendarDays className="w-4 h-4 text-gray-500 ml-2" />
                            {datasets.map((dataset, index) => (
                                <button
                                    key={dataset.date}
                                    onClick={() => setSelectedIndex(index)}
                                    className={clsx(
                                        'px-3 py-1.5 text-sm font-medium rounded-md transition-all',
                                        selectedIndex === index
                                            ? 'bg-white text-gray-900 shadow-sm'
                                            : 'text-gray-500 hover:text-gray-700'
                                    )}
                                >
                                    {dataset.label}
                                </button>
                            ))}
                        </div>
                    )}
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-500">
                    <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4" />
                        <span>Last updated: {formatDate(data.generated_at)}</span>
                    </div>
                    <span>•</span>
                    <span>Fetch date: {data.fetch_date}</span>
                </div>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                        <Users className="w-5 h-5 text-gray-500" />
                        <span className="text-sm text-gray-500 font-medium">Total Traders</span>
                    </div>
                    <div className="text-2xl font-bold text-gray-900">{formatNumber(summary.total_traders)}</div>
                    <div className="text-xs text-gray-500 mt-1">
                        Curated by Mirrorly
                    </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                        <Target className="w-5 h-5 text-gray-500" />
                        <span className="text-sm text-gray-500 font-medium">Active Traders</span>
                    </div>
                    <div className="text-2xl font-bold text-gray-900">{formatNumber(summary.traders_with_positions)}</div>
                    <div className="text-xs text-gray-500 mt-1">
                        {((summary.traders_with_positions / summary.total_traders) * 100).toFixed(1)}% with positions
                    </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="w-5 h-5 text-gray-500" />
                        <span className="text-sm text-gray-500 font-medium">Total Positions</span>
                    </div>
                    <div className="text-2xl font-bold text-gray-900">{formatNumber(summary.total_positions)}</div>
                    <div className="text-xs text-gray-500 mt-1">
                        Avg {(summary.total_positions / summary.traders_with_positions).toFixed(1)} per active trader
                    </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                        <Award className="w-5 h-5 text-gray-500" />
                        <span className="text-sm text-gray-500 font-medium">Performance Tiers</span>
                    </div>
                    <div className="flex gap-1 mt-2">
                        <div className="flex-1 text-center">
                            <div className="text-lg font-bold text-green-600">{by_performance_tier.strong.length}</div>
                            <div className="text-[10px] text-gray-500">Strong</div>
                        </div>
                        <div className="flex-1 text-center">
                            <div className="text-lg font-bold text-yellow-600">{by_performance_tier.watch.length}</div>
                            <div className="text-[10px] text-gray-500">Watch</div>
                        </div>
                        <div className="flex-1 text-center">
                            <div className="text-lg font-bold text-red-600">{by_performance_tier.avoid.length}</div>
                            <div className="text-[10px] text-gray-500">Avoid</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Category Distribution */}
            <div className="mb-8">
                <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4 border-b border-gray-200 pb-2">
                    Top Categories
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {topCategories.map(([category, count]) => (
                        <div
                            key={category}
                            className={clsx(
                                'p-3 rounded-lg border text-center',
                                getCategoryColor(category)
                            )}
                        >
                            <div className="text-xs font-medium mb-1">{category}</div>
                            <div className="text-lg font-bold">{formatNumber(count)}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Performance Tier Filter */}
            <div className="mb-6">
                <div className="flex items-center gap-2 bg-gray-100 rounded-lg p-1">
                    <button
                        onClick={() => setSelectedTier('all')}
                        className={clsx(
                            'px-4 py-2 text-sm font-medium rounded-md transition-all',
                            selectedTier === 'all'
                                ? 'bg-white text-gray-900 shadow-sm'
                                : 'text-gray-500 hover:text-gray-700'
                        )}
                    >
                        All Traders ({traders.length})
                    </button>
                    <button
                        onClick={() => setSelectedTier('strong')}
                        className={clsx(
                            'px-4 py-2 text-sm font-medium rounded-md transition-all',
                            selectedTier === 'strong'
                                ? 'bg-white text-green-700 shadow-sm'
                                : 'text-gray-500 hover:text-gray-700'
                        )}
                    >
                        Strong ({by_performance_tier.strong.length})
                    </button>
                    <button
                        onClick={() => setSelectedTier('watch')}
                        className={clsx(
                            'px-4 py-2 text-sm font-medium rounded-md transition-all',
                            selectedTier === 'watch'
                                ? 'bg-white text-yellow-700 shadow-sm'
                                : 'text-gray-500 hover:text-gray-700'
                        )}
                    >
                        Watch ({by_performance_tier.watch.length})
                    </button>
                    <button
                        onClick={() => setSelectedTier('avoid')}
                        className={clsx(
                            'px-4 py-2 text-sm font-medium rounded-md transition-all',
                            selectedTier === 'avoid'
                                ? 'bg-white text-red-700 shadow-sm'
                                : 'text-gray-500 hover:text-gray-700'
                        )}
                    >
                        Avoid ({by_performance_tier.avoid.length})
                    </button>
                </div>
            </div>

            {/* Trader Table */}
            <div>
                <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4 border-b border-gray-200 pb-2">
                    Trader Leaderboard
                </h3>
                <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-gray-50 border-b border-gray-200">
                                <tr>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Trader
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Categories
                                    </th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Win Rate
                                    </th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        W/L
                                    </th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Total Profit
                                    </th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Positions
                                    </th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Account Value
                                    </th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Unrealized PnL
                                    </th>
                                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Tier
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {displayTraders.map((trader) => (
                                    <tr key={trader.address} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-4 py-3">
                                            <div className="font-medium text-gray-900">{trader.name}</div>
                                            <a 
                                                href={`https://hyperscreener.asxn.xyz/profile/${trader.address}`}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-xs font-mono text-blue-600 hover:text-blue-800 hover:underline transition-colors"
                                            >
                                                {trader.address.slice(0, 6)}...{trader.address.slice(-4)}
                                            </a>
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="flex flex-wrap gap-1">
                                                {trader.categories.slice(0, 3).map((category) => (
                                                    <span
                                                        key={category}
                                                        className={clsx(
                                                            'px-2 py-0.5 rounded text-[10px] font-medium border',
                                                            getCategoryColor(category)
                                                        )}
                                                    >
                                                        {category}
                                                    </span>
                                                ))}
                                                {trader.categories.length > 3 && (
                                                    <span className="px-2 py-0.5 rounded text-[10px] font-medium border bg-gray-50 text-gray-600 border-gray-200">
                                                        +{trader.categories.length - 3}
                                                    </span>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3 text-right text-sm text-gray-700">
                                            {trader.win_rate !== null ? `${trader.win_rate.toFixed(1)}%` : 'N/A'}
                                        </td>
                                        <td className="px-4 py-3 text-right text-sm text-gray-700">
                                            {trader.wins !== null && trader.losses !== null 
                                                ? `${formatNumber(trader.wins)}/${formatNumber(trader.losses)}`
                                                : 'N/A'}
                                        </td>
                                        <td className={clsx(
                                            'px-4 py-3 text-right text-sm font-medium',
                                            trader.total_profit !== null && trader.total_profit >= 0 ? 'text-green-600' : 'text-red-600'
                                        )}>
                                            {formatCurrency(trader.total_profit)}
                                        </td>
                                        <td className="px-4 py-3 text-right text-sm text-gray-700">
                                            {trader.num_positions > 0 ? (
                                                <div>
                                                    <div className="font-medium">{trader.num_positions}</div>
                                                    {trader.top_coins.length > 0 && (
                                                        <div className="text-xs text-gray-500">
                                                            {trader.top_coins.join(', ')}
                                                        </div>
                                                    )}
                                                </div>
                                            ) : (
                                                <span className="text-gray-400">-</span>
                                            )}
                                        </td>
                                        <td className="px-4 py-3 text-right text-sm font-medium text-gray-900">
                                            {trader.account_value > 0 ? formatCurrency(trader.account_value) : '-'}
                                        </td>
                                        <td className={clsx(
                                            'px-4 py-3 text-right text-sm font-medium',
                                            trader.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                                        )}>
                                            {trader.has_positions ? (
                                                <>
                                                    {trader.unrealized_pnl >= 0 ? '+' : ''}
                                                    {formatCurrency(trader.unrealized_pnl)}
                                                </>
                                            ) : (
                                                <span className="text-gray-400">-</span>
                                            )}
                                        </td>
                                        <td className="px-4 py-3 text-center">
                                            <span className={clsx(
                                                'px-2 py-1 rounded text-xs font-medium border capitalize',
                                                getTierColor(trader.performance_tier)
                                            )}>
                                                {trader.performance_tier}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};
