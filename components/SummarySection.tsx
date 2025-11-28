'use client';

import React from 'react';
import { User, TrendingUp, AlertOctagon, Shield, Clock } from 'lucide-react';
import { IndicatorData } from '@/types';

interface SummarySectionProps {
    scores: Record<string, number>;
    indicators: IndicatorData[];
}

export const SummarySection: React.FC<SummarySectionProps> = ({ scores, indicators }) => {

    const getStats = (phase: string) => {
        const items = indicators.filter(i => i.phase === phase);
        const totalWeight = items.reduce((acc, i) => acc + i.weight, 0);
        const score = scores[phase] || 0;
        return { totalWeight, score, count: items.length };
    };

    // Helper for Notion Callout Block Style
    const CalloutBlock = ({ icon: Icon, title, children, colorClass }: any) => (
        <div className={`p-4 rounded-lg flex items-start gap-4 ${colorClass}`}>
            <Icon className="w-5 h-5 mt-0.5 opacity-80" />
            <div className="flex-1">
                <h3 className="font-bold text-base mb-1">{title}</h3>
                <div className="text-sm opacity-90 leading-relaxed">{children}</div>
            </div>
        </div>
    );

    const getRecommendation = () => {
        const ro = scores['RISK-ON (Entry)'] || 0;
        const sro = scores['STAY RISK-ON (Hold)'] || 0;
        const rf = scores['RISK-OFF (Exit)'] || 0;
        const srf = scores['STAY RISK-OFF (Wait)'] || 0;

        if (rf > 75) return { text: "SELL / HEDGE", bg: "bg-red-50 text-red-600" };
        if (ro > 65) return { text: "BUY", bg: "bg-green-50 text-green-600" };
        if (sro > 50) return { text: "HOLD", bg: "bg-blue-50 text-blue-600" };
        if (srf > 50) return { text: "WAIT / CASH", bg: "bg-yellow-50 text-yellow-600" };
        return { text: "NEUTRAL", bg: "bg-gray-100 text-gray-500" };
    };

    const recommendation = getRecommendation();

    return (
        <div className="animate-in fade-in duration-500 pb-20">
            {/* Page Cover / Title Area */}
            <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Market Summary</h2>
                <p className="text-gray-500 text-sm">Your manual assessment of current Bitcoin market cycle indicators.</p>
            </div>

            {/* Recommendation Callout */}
            <div className="mb-12">
                <CalloutBlock
                    icon={User}
                    title="Your Recommendation"
                    colorClass="bg-white text-gray-900 border border-gray-200"
                >
                    <div className={`inline-block px-2 py-1 rounded text-sm font-bold mb-3 ${recommendation.bg}`}>
                        {recommendation.text}
                    </div>
                    <div className="grid grid-cols-2 gap-y-1 gap-x-4 text-xs mt-2">
                        {Object.entries(scores).map(([k, v]) => {
                            if ((v as number) > 0) return (
                                <div key={k} className="flex justify-between border-b border-gray-200 py-1">
                                    <span className="text-gray-500 truncate pr-2">{k.split('(')[0]}</span>
                                    <span className="font-mono text-gray-700">{v}</span>
                                </div>
                            )
                            return null;
                        })}
                    </div>
                </CalloutBlock>
            </div>

            {/* Data Table / Progress View */}
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4 border-b border-gray-200 pb-2">Phase Scores</h3>
            <div className="space-y-6">
                {Object.keys(scores).length > 0 ? Object.keys(scores).map((phase) => {
                    const stats = getStats(phase);

                    // Simple Icon selection
                    let Icon = TrendingUp;
                    if (phase.includes('Wait')) Icon = Clock;
                    if (phase.includes('Exit')) Icon = AlertOctagon;
                    if (phase.includes('Hold')) Icon = Shield;

                    return (
                        <div key={phase} className="flex flex-col md:flex-row md:items-center gap-4 py-2">
                            {/* Label */}
                            <div className="w-48 flex items-center gap-2 text-sm font-medium text-gray-700 flex-shrink-0">
                                <Icon className="w-4 h-4 text-gray-500" />
                                {phase.split('(')[0]}
                            </div>

                            {/* Score Bar */}
                            <div className="flex-1">
                                <div className="flex items-center gap-3">
                                    <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-blue-500"
                                            style={{ width: `${(stats.score / (stats.totalWeight || 1)) * 100}%` }}
                                        />
                                    </div>
                                    <span className="text-sm text-gray-700 font-mono w-16 text-right">{stats.score} / {stats.totalWeight}</span>
                                </div>
                            </div>
                        </div>
                    );
                }) : (
                    <div className="text-sm text-gray-500 italic py-8 text-center border border-dashed border-gray-200 rounded">
                        No indicators tracked yet. Add indicators to each phase to begin.
                    </div>
                )}
            </div>

            {/* Decision Logic Snippet */}
            <div className="mt-12 pt-6 border-t border-gray-200">
                <div className="text-xs text-gray-500 flex items-center gap-2 mb-4">
                    <span className="uppercase tracking-wide">Logic Reference</span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs text-gray-500 font-mono">
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-red-400"></div>
                        Risk-Off {'>'} 75
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-green-400"></div>
                        Risk-On {'>'} 65
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-blue-400"></div>
                        Stay Risk-On {'>'} 50
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-yellow-400"></div>
                        Stay Risk-Off {'>'} 50
                    </div>
                </div>
            </div>
        </div>
    );
};