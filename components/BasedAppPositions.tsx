'use client';

import React, { useState } from 'react';
import { Users, TrendingUp, Coins, BarChart3, Clock, CalendarDays } from 'lucide-react';
import { PositionSummary } from '@/types';
import clsx from 'clsx';

interface DatasetOption {
    label: string;
    date: string;
    data: PositionSummary;
}

interface BasedAppPositionsProps {
    datasets: DatasetOption[];
}

export const BasedAppPositions: React.FC<BasedAppPositionsProps> = ({ datasets }) => {
    const [selectedIndex, setSelectedIndex] = useState(0);
    
    const data = datasets[selectedIndex].data;
    const { summary, by_coin, risk_distribution, top_positions } = data;

    // Format number with commas
    const formatNumber = (num: number) => {
        return new Intl.NumberFormat('en-US').format(num);
    };

    // Format currency
    const formatCurrency = (num: number) => {
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

    // Get risk level color
    const getRiskColor = (risk: string) => {
        switch (risk) {
            case 'CRITICAL':
                return 'bg-red-50 text-red-600 border-red-200';
            case 'HIGH':
                return 'bg-orange-50 text-orange-600 border-orange-200';
            case 'MODERATE':
                return 'bg-yellow-50 text-yellow-600 border-yellow-200';
            case 'LOW':
                return 'bg-green-50 text-green-600 border-green-200';
            default:
                return 'bg-gray-50 text-gray-600 border-gray-200';
        }
    };

    // Top coins (limit to top 20)
    const topCoins = by_coin.slice(0, 20);

    return (
        <div className="animate-in fade-in duration-500 pb-20">
            {/* Header */}
            <div className="mb-8">
                <div className="flex items-center justify-between flex-wrap gap-4 mb-2">
                    <h2 className="text-2xl font-bold text-gray-900">BasedApp Positions Summary</h2>
                    
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
                        <span className="text-sm text-gray-500 font-medium">Total Users</span>
                    </div>
                    <div className="text-2xl font-bold text-gray-900">{formatNumber(summary.total_users)}</div>
                    <div className="text-xs text-gray-500 mt-1">
                        {summary.users_with_positions.toLocaleString()} with positions
                    </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                        <BarChart3 className="w-5 h-5 text-gray-500" />
                        <span className="text-sm text-gray-500 font-medium">Total Positions</span>
                    </div>
                    <div className="text-2xl font-bold text-gray-900">{formatNumber(summary.total_positions)}</div>
                    <div className="text-xs text-gray-500 mt-1">
                        Avg {summary.avg_positions_per_user} per user
                    </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="w-5 h-5 text-gray-500" />
                        <span className="text-sm text-gray-500 font-medium">Total Value</span>
                    </div>
                    <div className="text-2xl font-bold text-gray-900">{formatCurrency(summary.total_position_value)}</div>
                    <div className="text-xs text-gray-500 mt-1">
                        Across {by_coin.length} coins
                    </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                        <Coins className="w-5 h-5 text-gray-500" />
                        <span className="text-sm text-gray-500 font-medium">Active Coins</span>
                    </div>
                    <div className="text-2xl font-bold text-gray-900">{by_coin.length}</div>
                    <div className="text-xs text-gray-500 mt-1">
                        With open positions
                    </div>
                </div>
            </div>

            {/* Risk Distribution */}
            <div className="mb-8">
                <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4 border-b border-gray-200 pb-2">
                    Risk Distribution
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                    {Object.entries(risk_distribution).map(([risk, count]) => (
                        <div
                            key={risk}
                            className={clsx(
                                'p-3 rounded-lg border text-center',
                                getRiskColor(risk)
                            )}
                        >
                            <div className="text-xs font-medium mb-1">{risk}</div>
                            <div className="text-lg font-bold">{formatNumber(count)}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Top Coins Table */}
            <div className="mb-8">
                <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4 border-b border-gray-200 pb-2">
                    Top Coins by Position Value
                </h3>
                <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-xs">
                            <thead className="bg-gray-50 border-b border-gray-200">
                                <tr>
                                    <th className="px-2 py-2 text-left text-[10px] font-medium text-gray-500 uppercase tracking-wider">
                                        Coin
                                    </th>
                                    <th className="px-2 py-2 text-right text-[10px] font-medium text-gray-500 uppercase tracking-wider">
                                        Pos
                                    </th>
                                    <th className="px-2 py-2 text-right text-[10px] font-medium text-gray-500 uppercase tracking-wider">
                                        Value
                                    </th>
                                    <th className="px-2 py-2 text-right text-[10px] font-medium text-gray-500 uppercase tracking-wider">
                                        Longs
                                    </th>
                                    <th className="px-2 py-2 text-right text-[10px] font-medium text-gray-500 uppercase tracking-wider">
                                        Shorts
                                    </th>
                                    <th className="px-2 py-2 text-right text-[10px] font-medium text-gray-500 uppercase tracking-wider">
                                        L/S
                                    </th>
                                    <th className="px-2 py-2 text-right text-[10px] font-medium text-gray-500 uppercase tracking-wider">
                                        Long Sz
                                    </th>
                                    <th className="px-2 py-2 text-right text-[10px] font-medium text-gray-500 uppercase tracking-wider">
                                        Short Sz
                                    </th>
                                    <th className="px-2 py-2 text-right text-[10px] font-medium text-gray-500 uppercase tracking-wider">
                                        Sz Ratio
                                    </th>
                                    <th className="px-2 py-2 text-right text-[10px] font-medium text-gray-500 uppercase tracking-wider">
                                        L PnL
                                    </th>
                                    <th className="px-2 py-2 text-right text-[10px] font-medium text-gray-500 uppercase tracking-wider">
                                        S PnL
                                    </th>
                                    <th className="px-2 py-2 text-right text-[10px] font-medium text-gray-500 uppercase tracking-wider">
                                        Net
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {topCoins.map((coin) => (
                                    <tr key={coin.coin} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-2 py-2">
                                            <div className="font-medium text-gray-900 text-xs">{coin.coin}</div>
                                        </td>
                                        <td className="px-2 py-2 text-right text-xs text-gray-700">
                                            {formatNumber(coin.count)}
                                        </td>
                                        <td className="px-2 py-2 text-right text-xs font-medium text-gray-900 whitespace-nowrap">
                                            {formatCurrency(coin.total_value)}
                                        </td>
                                        <td className="px-2 py-2 text-right text-xs text-green-600">
                                            {formatNumber(coin.longs)}
                                        </td>
                                        <td className="px-2 py-2 text-right text-xs text-red-600">
                                            {formatNumber(coin.shorts)}
                                        </td>
                                        <td className="px-2 py-2 text-right text-xs text-gray-700">
                                            {coin.long_short_ratio.toFixed(2)}x
                                        </td>
                                        <td className="px-2 py-2 text-right text-xs font-medium text-green-600 whitespace-nowrap">
                                            {formatNumber(coin.longs_total_size)}
                                        </td>
                                        <td className="px-2 py-2 text-right text-xs font-medium text-red-600 whitespace-nowrap">
                                            {formatNumber(coin.shorts_total_size)}
                                        </td>
                                        <td className="px-2 py-2 text-right text-xs text-gray-700">
                                            {coin.long_short_size_ratio.toFixed(2)}x
                                        </td>
                                        <td className={clsx(
                                            'px-2 py-2 text-right text-xs font-medium whitespace-nowrap',
                                            coin.longs_unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                                        )}>
                                            {coin.longs_unrealized_pnl >= 0 ? '+' : ''}
                                            {formatCurrency(coin.longs_unrealized_pnl)}
                                        </td>
                                        <td className={clsx(
                                            'px-2 py-2 text-right text-xs font-medium whitespace-nowrap',
                                            coin.shorts_unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                                        )}>
                                            {coin.shorts_unrealized_pnl >= 0 ? '+' : ''}
                                            {formatCurrency(coin.shorts_unrealized_pnl)}
                                        </td>
                                        <td className={clsx(
                                            'px-2 py-2 text-right text-xs font-medium whitespace-nowrap',
                                            coin.total_unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                                        )}>
                                            {coin.total_unrealized_pnl >= 0 ? '+' : ''}
                                            {formatCurrency(coin.total_unrealized_pnl)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Top Positions */}
            <div>
                <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4 border-b border-gray-200 pb-2">
                    Top Positions by Value
                </h3>
                <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-gray-50 border-b border-gray-200">
                                <tr>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Address
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Coin
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Direction
                                    </th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Size
                                    </th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Position Value
                                    </th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Unrealized PnL
                                    </th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Risk Level
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {top_positions.slice(0, 25).map((pos, idx) => (
                                    <tr key={idx} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-4 py-3">
                                            <a 
                                                href={`https://hyperscreener.asxn.xyz/profile/${pos.user_address}`}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-xs font-mono text-blue-600 hover:text-blue-800 hover:underline transition-colors"
                                            >
                                                {pos.user_address.slice(0, 6)}...{pos.user_address.slice(-4)}
                                            </a>
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="font-medium text-gray-900">{pos.coin}</div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className={clsx(
                                                'px-2 py-1 rounded text-xs font-medium',
                                                pos.direction === 'LONG' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                                            )}>
                                                {pos.direction}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-right text-sm text-gray-700">
                                            {formatNumber(pos.size)}
                                        </td>
                                        <td className="px-4 py-3 text-right text-sm font-medium text-gray-900">
                                            {formatCurrency(pos.position_value)}
                                        </td>
                                        <td className={clsx(
                                            'px-4 py-3 text-right text-sm font-medium',
                                            pos.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                                        )}>
                                            {pos.unrealized_pnl >= 0 ? '+' : ''}
                                            {formatCurrency(pos.unrealized_pnl)}
                                        </td>
                                        <td className="px-4 py-3 text-right">
                                            <span className={clsx(
                                                'px-2 py-1 rounded text-xs font-medium border',
                                                getRiskColor(pos.risk_level)
                                            )}>
                                                {pos.risk_level}
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

