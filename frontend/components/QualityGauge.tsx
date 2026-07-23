'use client';

import React from 'react';
import { Award, CheckCircle2, AlertTriangle } from 'lucide-react';

interface QualityScoreProps {
  score?: {
    originality: number;
    clarity: number;
    correctness: number;
    test_coverage: number;
    educational_value: number;
    total_score: number;
    pass_quality_gate: boolean;
  };
}

export default function QualityGauge({ score }: QualityScoreProps) {
  if (!score) return null;

  const passes = score.pass_quality_gate;

  return (
    <div className="glass-panel p-5 rounded-xl border border-slate-800 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Award className="w-5 h-5 text-amber-400" />
          <h3 className="font-semibold text-slate-100 text-sm">Quality Gate Evaluation</h3>
        </div>
        <span
          className={`flex items-center gap-1 text-xs px-2.5 py-1 rounded-full font-semibold ${
            passes
              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
          }`}
        >
          {passes ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertTriangle className="w-3.5 h-3.5" />}
          {passes ? 'GATE PASSED (>= 85)' : 'GATE REJECTED (< 85)'}
        </span>
      </div>

      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-extrabold text-slate-100">{score.total_score}</span>
        <span className="text-slate-400 text-sm font-mono">/ 100 points</span>
      </div>

      <div className="space-y-2 text-xs">
        <div>
          <div className="flex justify-between text-slate-400 mb-1">
            <span>Originality (30 max)</span>
            <span className="text-slate-200 font-mono">{score.originality}</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: `${(score.originality / 30) * 100}%` }}></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between text-slate-400 mb-1">
            <span>Clarity (20 max)</span>
            <span className="text-slate-200 font-mono">{score.clarity}</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-purple-500 h-1.5 rounded-full" style={{ width: `${(score.clarity / 20) * 100}%` }}></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between text-slate-400 mb-1">
            <span>Correctness (25 max)</span>
            <span className="text-slate-200 font-mono">{score.correctness}</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: `${(score.correctness / 25) * 100}%` }}></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between text-slate-400 mb-1">
            <span>Test Coverage (15 max)</span>
            <span className="text-slate-200 font-mono">{score.test_coverage}</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-amber-500 h-1.5 rounded-full" style={{ width: `${(score.test_coverage / 15) * 100}%` }}></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between text-slate-400 mb-1">
            <span>Educational Value (10 max)</span>
            <span className="text-slate-200 font-mono">{score.educational_value}</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-indigo-500 h-1.5 rounded-full" style={{ width: `${(score.educational_value / 10) * 100}%` }}></div>
          </div>
        </div>
      </div>
    </div>
  );
}
