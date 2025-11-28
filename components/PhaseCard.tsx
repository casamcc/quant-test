import React, { useState } from 'react';
import { IndicatorData } from '@/types';
import { Plus, Info, User, HelpCircle, RotateCcw, Trash2 } from 'lucide-react';
import { isWeightCustomized, resetWeight } from '@/lib/weightStorage';
import { INDICATORS_DATA } from '@/constants/indicators';
import clsx from 'clsx';

interface PhaseCardProps {
    title: string;
    score: number;
    indicators: IndicatorData[];
    onUpdate: (id: string, updates: Partial<IndicatorData>) => void;
    onAdd: (indicator: IndicatorData) => void;
    onDelete: (id: string) => void;
}

export const PhaseCard: React.FC<PhaseCardProps> = ({ title, score, indicators, onUpdate, onAdd, onDelete }) => {
    const [isAdding, setIsAdding] = useState(false);
    const [newInd, setNewInd] = useState<Partial<IndicatorData>>({
        category: '',
        name: '',
        logic: '',
        trigger: '',
        weight: 10,
        reliability: 'B-Tier'
    });
    const [deletingId, setDeletingId] = useState<string | null>(null);

    const handleAddItem = () => {
        if (!newInd.name || !newInd.trigger) return;

        const id = `custom-${Date.now()}`;
        onAdd({
            id,
            phase: title,
            category: newInd.category || 'Custom',
            name: newInd.name,
            logic: newInd.logic || 'User defined custom indicator',
            trigger: newInd.trigger,
            weight: Number(newInd.weight) || 0,
            reliability: newInd.reliability || 'User',
            currentValue: '',
            isTriggered: false
        });
        setIsAdding(false);
        setNewInd({
            category: '',
            name: '',
            logic: '',
            trigger: '',
            weight: 10,
            reliability: 'B-Tier'
        });
    };

    // Notion-style Tier Badge
    const TierBadge = ({ tier }: { tier: string }) => {
        let bgClass = "bg-gray-100";
        let textClass = "text-gray-500";

        if (tier.includes('S-Tier')) { bgClass = "bg-red-50"; textClass = "text-red-600"; } // Red-ish
        else if (tier.includes('A-Tier')) { bgClass = "bg-blue-50"; textClass = "text-blue-600"; } // Blue-ish
        else if (tier.includes('B-Tier')) { bgClass = "bg-green-50"; textClass = "text-green-600"; } // Green-ish
        else if (tier.includes('C-Tier')) { bgClass = "bg-yellow-50"; textClass = "text-yellow-600"; } // Yellow-ish

        return (
            <span className={clsx("px-1.5 py-0.5 rounded text-[10px] font-medium whitespace-nowrap", bgClass, textClass)}>
                {tier}
            </span>
        );
    };

    // Editable Weight Badge Component
    const EditableWeightBadge = ({ indicator }: { indicator: IndicatorData }) => {
        const [isEditing, setIsEditing] = useState(false);
        const [tempValue, setTempValue] = useState(indicator.weight.toString());

        const defaultWeight = INDICATORS_DATA.find(ind => ind.id === indicator.id)?.weight || indicator.weight;
        const isCustomized = isWeightCustomized(indicator.id);

        const handleSave = () => {
            const numValue = parseInt(tempValue);
            if (!isNaN(numValue) && numValue >= 0 && numValue <= 100) {
                onUpdate(indicator.id, { weight: numValue });
                setIsEditing(false);
            } else {
                // Reset to current value if invalid
                setTempValue(indicator.weight.toString());
                setIsEditing(false);
            }
        };

        const handleReset = (e: React.MouseEvent) => {
            e.stopPropagation();
            resetWeight(indicator.id);
            onUpdate(indicator.id, { weight: defaultWeight });
        };

        if (isEditing) {
            return (
                <input
                    type="number"
                    value={tempValue}
                    onChange={(e) => setTempValue(e.target.value)}
                    onBlur={handleSave}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter') handleSave();
                        if (e.key === 'Escape') {
                            setTempValue(indicator.weight.toString());
                            setIsEditing(false);
                        }
                    }}
                    autoFocus
                    className="w-12 h-6 bg-white border border-[#2383e2] rounded text-xs font-mono text-center text-gray-900 focus:outline-none"
                    min="0"
                    max="100"
                />
            );
        }

        return (
            <div className="flex items-center gap-1 group/weight">
                <button
                    onClick={() => setIsEditing(true)}
                    className={clsx(
                        "px-1.5 py-0.5 rounded text-xs font-mono transition-all cursor-pointer",
                        isCustomized
                            ? "bg-blue-50 text-blue-600 border border-[#2383e2]/30 hover:border-[#2383e2]"
                            : "bg-gray-100 text-gray-500 hover:bg-gray-200 hover:text-gray-700"
                    )}
                    title={isCustomized ? "Custom weight (click to edit)" : "Click to edit weight"}
                >
                    {indicator.weight}%
                </button>
                {isCustomized && (
                    <button
                        onClick={handleReset}
                    >
                        <RotateCcw className="w-3 h-3 text-gray-400 hover:text-gray-600" />
                    </button>
                )}
            </div>
        );
    };

    return (
        <div className="animate-in fade-in duration-300 pb-20">
            {/* Minimalist Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 pb-4 border-b border-gray-200">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                        <span className="px-1.5 py-0.5 bg-gray-100 rounded border border-gray-200 text-xs">Database</span>
                        <span>•</span>
                        <span>{indicators.length} Items</span>
                    </div>
                </div>

                {/* Score Summary */}
                <div className="flex gap-2 mt-4 md:mt-0">
                    <div className="flex flex-col items-end">
                        <span className="text-[10px] uppercase tracking-wide text-gray-500 font-semibold mb-1">Score</span>
                        <div className="font-mono text-xl font-medium text-blue-600">{score}</div>
                    </div>
                </div>
            </div>

            {/* List Container */}
            <div className="space-y-4">
                {indicators.map((ind) => {
                    return (
                        <div key={ind.id} className="group bg-white border border-gray-200 rounded-lg hover:shadow-sm transition-all p-4 relative">

                                {/* Top Row: Name & Metadata */}
                                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                                    <div className="flex items-center gap-3">
                                        <EditableWeightBadge indicator={ind} />
                                        <div className="font-medium text-gray-900 text-base">{ind.name}</div>
                                        <TierBadge tier={ind.reliability} />
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="flex items-center gap-2 text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                                            <Info className="w-3 h-3" />
                                            {ind.trigger}
                                        </div>

                                        {/* Delete Button with Confirmation */}
                                        {deletingId === ind.id ? (
                                            <div className="flex items-center gap-2 bg-red-50 border border-red-200 px-2 py-1 rounded animate-in fade-in zoom-in duration-200">
                                                <span className="text-[10px] text-red-600 font-medium whitespace-nowrap">Delete?</span>
                                                <button
                                                    onClick={() => {
                                                        onDelete(ind.id);
                                                        setDeletingId(null);
                                                    }}
                                                    className="text-red-600 hover:text-red-700 transition-colors"
                                                >
                                                    <Trash2 className="w-3 h-3" />
                                                </button>
                                                <button
                                                    onClick={() => setDeletingId(null)}
                                                    className="text-gray-400 hover:text-gray-600 transition-colors"
                                                >
                                                    <RotateCcw className="w-3 h-3" />
                                                </button>
                                            </div>
                                        ) : (
                                            <button
                                                onClick={() => setDeletingId(ind.id)}
                                                className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-red-50 hover:text-red-600 rounded text-gray-400"
                                                title="Delete indicator"
                                            >
                                                <Trash2 className="w-3.5 h-3.5" />
                                            </button>
                                        )}
                                    </div>
                                </div>

                                {/* Manual Input */}
                                <div className="space-y-2 pt-2">
                                    <div className="text-[11px] text-gray-500 uppercase tracking-wider font-semibold flex items-center gap-1">
                                        <User className="w-3 h-3" /> Your Assessment
                                    </div>
                                    <div className="flex items-center gap-2">
                                        {/* Checkbox-like trigger button */}
                                        <button
                                            onClick={() => onUpdate(ind.id, { isTriggered: !ind.isTriggered })}
                                            className={clsx(
                                                "h-[42px] px-3 rounded border flex items-center gap-2 transition-all font-medium text-sm",
                                                ind.isTriggered
                                                    ? "bg-green-50 border-green-200 text-green-700"
                                                    : "bg-white border-gray-200 text-gray-500 hover:bg-gray-50"
                                            )}
                                        >
                                            {ind.isTriggered ? "Active" : "Inactive"}
                                        </button>

                                        {/* Text Input */}
                                        <input
                                            type="text"
                                            value={ind.currentValue || ''}
                                            onChange={(e) => onUpdate(ind.id, { currentValue: e.target.value })}
                                            placeholder="Enter current value..."
                                            className="flex-1 h-[42px] bg-white border border-gray-200 rounded px-3 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-[#2383e2] transition-colors"
                                        />
                                    </div>
                                </div>

                                {/* Logic Collapsible/Snippet - Notion Callout Style */}
                                <div className="mt-4 p-3 bg-gray-50 rounded text-sm text-gray-600 flex gap-3 border border-transparent hover:border-gray-200 transition-colors">
                                    <HelpCircle className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" />
                                    <div>{ind.logic}</div>
                                </div>
                            </div>
                        );
                    })}

                {/* Add New Button */}
                {!isAdding ? (
                    <button
                        onClick={() => setIsAdding(true)}
                        className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-300 py-2 px-1 transition-colors mt-4"
                    >
                        <Plus className="w-4 h-4" />
                        New
                    </button>
                ) : (
                    <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-lg mt-4">
                        <h3 className="text-gray-900 font-medium mb-4">Add Property</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                            <input
                                className="bg-white border border-gray-200 rounded px-3 py-2 text-sm text-gray-900 focus:outline-none focus:border-[#2383e2]"
                                placeholder="Name"
                                value={newInd.name}
                                onChange={e => setNewInd({ ...newInd, name: e.target.value })}
                            />
                            <input
                                className="bg-white border border-gray-200 rounded px-3 py-2 text-sm text-gray-900 focus:outline-none focus:border-[#2383e2]"
                                placeholder="Category"
                                value={newInd.category}
                                onChange={e => setNewInd({ ...newInd, category: e.target.value })}
                            />
                            <input
                                className="bg-white border border-gray-200 rounded px-3 py-2 text-sm text-gray-900 focus:outline-none focus:border-[#2383e2]"
                                placeholder="Trigger Condition"
                                value={newInd.trigger}
                                onChange={e => setNewInd({ ...newInd, trigger: e.target.value })}
                            />
                            <input
                                type="number"
                                className="bg-white border border-gray-200 rounded px-3 py-2 text-sm text-gray-900 focus:outline-none focus:border-[#2383e2]"
                                placeholder="Weight (%)"
                                value={newInd.weight}
                                onChange={e => setNewInd({ ...newInd, weight: Number(e.target.value) })}
                            />
                            <textarea
                                className="col-span-1 md:col-span-2 bg-white border border-gray-200 rounded px-3 py-2 text-sm text-gray-900 focus:outline-none focus:border-[#2383e2] h-20"
                                placeholder="Logic description..."
                                value={newInd.logic}
                                onChange={e => setNewInd({ ...newInd, logic: e.target.value })}
                            />
                        </div>
                        <div className="flex gap-2">
                            <button onClick={handleAddItem} className="bg-[#2383e2] hover:bg-[#1a73ca] text-white px-4 py-1.5 rounded text-sm font-medium">Add</button>
                            <button onClick={() => setIsAdding(false)} className="bg-transparent hover:bg-gray-100 text-gray-500 px-4 py-1.5 rounded text-sm">Cancel</button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};