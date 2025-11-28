'use client';

import React, { useState, useMemo } from 'react';
import { LayoutDashboard, Database, BarChart3, Clock, AlertTriangle } from 'lucide-react';
import { INDICATORS_DATA } from '@/constants/indicators';
import { IndicatorData } from '@/types';
import { PhaseCard } from '@/components/PhaseCard';
import { SummarySection } from '@/components/SummarySection';
import { loadWeights, saveWeight, loadDeletedIndicators, saveDeletedIndicator } from '@/lib/weightStorage';
import clsx from 'clsx';

export default function Home() {
    // Load indicators with saved weights on mount, filtering out deleted ones
    const [indicators, setIndicators] = useState<IndicatorData[]>(() => {
        if (typeof window === 'undefined') return INDICATORS_DATA;

        const savedWeights = loadWeights();
        const deletedIds = loadDeletedIndicators();

        return INDICATORS_DATA
            .filter(ind => !deletedIds.includes(ind.id))
            .map(ind => ({
                ...ind,
                weight: savedWeights[ind.id] ?? ind.weight
            }));
    });

    // Navigation State
    const [activeTab, setActiveTab] = useState<string>('SUMMARY');

    const handleUpdateIndicator = (id: string, updates: Partial<IndicatorData>) => {
        setIndicators(prev => prev.map(ind => {
            if (ind.id === id) {
                const updated = { ...ind, ...updates };
                // Persist weight changes to localStorage
                if (updates.weight !== undefined) {
                    saveWeight(id, updates.weight);
                }
                return updated;
            }
            return ind;
        }));
    };

    const handleDeleteIndicator = (id: string) => {
        saveDeletedIndicator(id);
        setIndicators(prev => prev.filter(ind => ind.id !== id));
    };

    const handleAddIndicator = (newIndicator: IndicatorData) => {
        setIndicators(prev => [...prev, newIndicator]);
    };

    const calculateScores = (inds: IndicatorData[]) => {
        const scores: Record<string, number> = {};

        const phases = Array.from(new Set(inds.map(i => i.phase)));

        phases.forEach(phase => {
            const phaseIndicators = inds.filter(i => i.phase === phase);

            scores[phase] = phaseIndicators.reduce((acc, curr) => {
                if (curr.isTriggered) {
                    return acc + curr.weight;
                }
                return acc;
            }, 0);
        });

        return scores;
    };

    const scores = useMemo(() => calculateScores(indicators), [indicators]);

    // Notion-like colors for badges, simplified
    const phases = [
        { id: 'RISK-ON (Entry)', shortTitle: 'Risk-On', icon: BarChart3 },
        { id: 'STAY RISK-ON (Hold)', shortTitle: 'Hold', icon: Clock },
        { id: 'RISK-OFF (Exit)', shortTitle: 'Risk-Off', icon: AlertTriangle },
        { id: 'STAY RISK-OFF (Wait)', shortTitle: 'Wait', icon: Database },
    ];

    return (
        <div className="min-h-screen text-gray-900 p-4 md:p-12 font-sans selection:bg-[#2383e2] selection:text-white">
            {/* Header - Notion Page Title Style */}
            <header className="max-w-5xl mx-auto mb-10 group">
                <div className="flex items-center gap-2 mb-6 text-sm text-gray-500 font-medium">
                    <span className="hover:text-gray-700 cursor-pointer transition-colors">Workspace</span>
                    <span>/</span>
                    <span className="text-gray-700">Market Analysis</span>
                </div>

                <div className="flex items-center gap-4">
                    <div className="w-16 h-16 bg-white border border-gray-200 rounded flex items-center justify-center text-4xl shadow-sm">
                        ⚡️
                    </div>
                    <div>
                        <h1 className="text-4xl font-bold text-gray-900 tracking-tight">
                            Crypto Cycle Tracker
                        </h1>
                        <p className="text-gray-500 text-sm mt-2">
                            Manual market cycle analysis and signal tracking
                        </p>
                    </div>
                </div>
            </header>

            <main className="max-w-5xl mx-auto">

                {/* Notion-style View Switcher (Tabs) */}
                <div className="flex items-center gap-1 mb-6 border-b border-gray-200 pb-0 overflow-x-auto no-scrollbar">
                    <button
                        onClick={() => setActiveTab('SUMMARY')}
                        className={clsx(
                            "px-3 py-2 text-sm font-medium flex items-center gap-2 transition-all border-b-2",
                            activeTab === 'SUMMARY'
                                ? "text-gray-900 border-gray-900"
                                : "text-gray-500 border-transparent hover:text-gray-700 hover:bg-gray-100 rounded-t"
                        )}
                    >
                        <LayoutDashboard className="w-4 h-4" />
                        Board Summary
                    </button>
                    <div className="w-px h-4 bg-gray-200 mx-1"></div>
                    {phases.map(phase => (
                        <button
                            key={phase.id}
                            onClick={() => setActiveTab(phase.id)}
                            className={clsx(
                                "px-3 py-2 text-sm font-medium flex items-center gap-2 transition-all border-b-2 whitespace-nowrap",
                                activeTab === phase.id
                                    ? "text-gray-900 border-gray-900"
                                    : "text-gray-500 border-transparent hover:text-gray-700 hover:bg-gray-100 rounded-t"
                            )}
                        >
                            <phase.icon className="w-4 h-4" />
                            {phase.shortTitle}
                            <span className="ml-1 text-[10px] text-gray-500">
                                {indicators.filter(i => i.phase === phase.id).length}
                            </span>
                        </button>
                    ))}
                </div>

                {/* Content Area - Minimalist Container */}
                <div className="min-h-[500px]">
                    {activeTab === 'SUMMARY' ? (
                        <SummarySection
                            scores={scores}
                            indicators={indicators}
                        />
                    ) : (
                        phases.filter(p => p.id === activeTab).map(phaseConfig => {
                            const phaseData = indicators.filter(i => i.phase === phaseConfig.id);
                            const score = scores[phaseConfig.id] || 0;

                            return (
                                <PhaseCard
                                    key={phaseConfig.id}
                                    title={phaseConfig.id}
                                    score={score}
                                    indicators={phaseData}
                                    onUpdate={handleUpdateIndicator}
                                    onAdd={handleAddIndicator}
                                    onDelete={handleDeleteIndicator}
                                />
                            );
                        })
                    )}
                </div>

            </main>
        </div>
    );
}
