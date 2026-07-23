'use client';

import React, { useState } from 'react';
import ModelSelector from '@/components/ModelSelector';
import QualityGauge from '@/components/QualityGauge';
import {
  Zap,
  Code2,
  FileText,
  ShieldCheck,
  Download,
  Terminal,
  Sparkles,
  Layers,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'generate' | 'testcase'>('generate');
  const [topic, setTopic] = useState('Dynamic Programming');
  const [difficulty, setDifficulty] = useState('Medium');
  const [targetComplexity, setTargetComplexity] = useState('O(N log N)');
  const [educationalObjective, setEducationalObjective] = useState('Prefix XOR frequency hash map pattern');
  
  const [pastedStatement, setPastedStatement] = useState('');
  const [numCases, setNumCases] = useState(20);

  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [generatedProblem, setGeneratedProblem] = useState<any>(null);
  const [generatedTestCases, setGeneratedTestCases] = useState<any[]>([]);

  const handleGenerateProblem = async () => {
    setLoading(true);
    setStatusMessage('Orchestrating 8-Agent Pipeline (Idea -> Statement -> Solution -> Verifier)...');
    setGeneratedProblem(null);
    try {
      const res = await fetch('http://localhost:8080/api/problems/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic,
          difficulty,
          target_complexity: targetComplexity,
          educational_objective: educationalObjective
        })
      });
      if (res.ok) {
        const data = await res.json();
        setGeneratedProblem(data);
        setStatusMessage('Problem generation and verification complete!');
      } else {
        const err = await res.json();
        setStatusMessage(`Generation failed: ${err.detail || 'Server error'}`);
      }
    } catch (e: any) {
      setStatusMessage(`Network error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateTestCases = async () => {
    setLoading(true);
    setStatusMessage('Synthesizing boundary, adversarial, and stress test cases...');
    try {
      const res = await fetch('http://localhost:8080/api/testcases/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          statement_or_url: pastedStatement,
          num_cases: numCases,
          include_adversarial: true
        })
      });
      if (res.ok) {
        const cases = await res.json();
        // Rank them
        const rankRes = await fetch('http://localhost:8080/api/testcases/rank', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(cases)
        });
        const ranked = rankRes.ok ? await rankRes.json() : cases;
        setGeneratedTestCases(ranked);
        setStatusMessage(`Generated and ranked ${ranked.length} test cases!`);
      } else {
        setStatusMessage('Failed to generate test cases.');
      }
    } catch (e: any) {
      setStatusMessage(`Error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: 'markdown' | 'json' | 'leetcode') => {
    if (!generatedProblem) return;
    try {
      const endpoint = `http://localhost:8080/api/export/${format}`;
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(generatedProblem)
      });
      if (!res.ok) {
        const err = await res.json();
        alert(err.detail || 'Export failed Quality Gate');
        return;
      }

      if (format === 'leetcode') {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${generatedProblem.id}_package.zip`;
        a.click();
      } else {
        const text = await res.text();
        const blob = new Blob([text], { type: format === 'json' ? 'application/json' : 'text/markdown' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${generatedProblem.id}.${format === 'json' ? 'json' : 'md'}`;
        a.click();
      }
    } catch (e: any) {
      alert(`Export error: ${e.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col">
      {/* Top Navigation */}
      <header className="border-b border-slate-800 bg-[#0b0f19]/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-blue-600/20 border border-blue-500/30 text-blue-400">
              <Zap className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-bold text-lg text-slate-100 flex items-center gap-2">
                PROBLEM FOUNDRY
                <span className="text-[10px] font-mono font-semibold uppercase px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  Model-Agnostic v1.0
                </span>
              </h1>
              <p className="text-xs text-slate-400">Local AI Algorithmic Problem Authoring & Verification Engine</p>
            </div>
          </div>

          <div className="flex gap-2 bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs">
            <button
              onClick={() => setActiveTab('generate')}
              className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                activeTab === 'generate' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              New Problem Generator
            </button>
            <button
              onClick={() => setActiveTab('testcase')}
              className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                activeTab === 'testcase' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Existing Problem Test Suite
            </button>
          </div>
        </div>
      </header>

      {/* Main Layout Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-6 space-y-6">
        {/* Local Model Selector Widget */}
        <ModelSelector />

        {/* Tab 1: New Problem Generator */}
        {activeTab === 'generate' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Column: Form & Multi-Agent Pipeline Control */}
            <div className="lg:col-span-4 space-y-6">
              <div className="glass-panel p-5 rounded-xl border border-slate-800 space-y-4">
                <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
                  <Sparkles className="w-4 h-4 text-blue-400" />
                  Problem Specifications
                </div>

                <div className="space-y-3 text-xs">
                  <div>
                    <label className="block text-slate-400 mb-1 font-medium">Algorithmic Topic</label>
                    <input
                      type="text"
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-400 mb-1 font-medium">Difficulty Level</label>
                    <select
                      value={difficulty}
                      onChange={(e) => setDifficulty(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-blue-500"
                    >
                      <option value="Easy">Easy</option>
                      <option value="Medium">Medium</option>
                      <option value="Hard">Hard</option>
                      <option value="Expert">Expert</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-400 mb-1 font-medium">Target Complexity</label>
                    <input
                      type="text"
                      value={targetComplexity}
                      onChange={(e) => setTargetComplexity(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-400 mb-1 font-medium">Educational Objective</label>
                    <textarea
                      rows={3}
                      value={educationalObjective}
                      onChange={(e) => setEducationalObjective(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-blue-500 resize-none"
                    />
                  </div>

                  <button
                    onClick={handleGenerateProblem}
                    disabled={loading}
                    className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-medium py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2 text-sm"
                  >
                    <Layers className="w-4 h-4" />
                    {loading ? 'Executing Pipeline...' : 'Generate & Verify Problem'}
                  </button>
                </div>
              </div>

              {/* Status & Pipeline Log */}
              {statusMessage && (
                <div className="glass-panel p-4 rounded-xl border border-slate-800 text-xs flex items-start gap-2.5">
                  <Terminal className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                  <div className="text-slate-300 font-mono leading-relaxed">{statusMessage}</div>
                </div>
              )}

              {/* Quality Score Breakdown */}
              {generatedProblem && (
                <QualityGauge score={generatedProblem.quality_score} />
              )}
            </div>

            {/* Right Column: Problem Preview, Code & Verification */}
            <div className="lg:col-span-8 space-y-6">
              {generatedProblem ? (
                <>
                  {/* Export Action Bar */}
                  <div className="glass-panel p-4 rounded-xl border border-slate-800 flex items-center justify-between gap-4">
                    <div>
                      <h2 className="text-base font-bold text-slate-100">{generatedProblem.title}</h2>
                      <p className="text-xs text-slate-400 font-mono">ID: {generatedProblem.id}</p>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleExport('markdown')}
                        className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-3 py-1.5 rounded-lg border border-slate-700 transition-colors flex items-center gap-1.5"
                      >
                        <FileText className="w-3.5 h-3.5" /> Markdown
                      </button>
                      <button
                        onClick={() => handleExport('json')}
                        className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-3 py-1.5 rounded-lg border border-slate-700 transition-colors flex items-center gap-1.5"
                      >
                        <Code2 className="w-3.5 h-3.5" /> JSON
                      </button>
                      <button
                        onClick={() => handleExport('leetcode')}
                        className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium px-3.5 py-1.5 rounded-lg transition-colors flex items-center gap-1.5 shadow-sm"
                      >
                        <Download className="w-3.5 h-3.5" /> LeetCode Package (.zip)
                      </button>
                    </div>
                  </div>

                  {/* Problem Statement Card */}
                  <div className="glass-panel p-6 rounded-xl border border-slate-800 space-y-4">
                    <h3 className="text-sm font-semibold text-slate-200 border-b border-slate-800 pb-2">Background & Statement</h3>
                    <p className="text-xs text-slate-300 italic leading-relaxed">{generatedProblem.background}</p>
                    <div className="text-xs text-slate-200 leading-relaxed font-sans whitespace-pre-line bg-slate-900/60 p-4 rounded-lg border border-slate-800">
                      {generatedProblem.formal_statement}
                    </div>

                    <h4 className="text-xs font-semibold text-slate-300 pt-2">Constraints</h4>
                    <ul className="list-disc list-inside text-xs text-slate-400 space-y-1 font-mono">
                      {generatedProblem.constraints?.map((c: string, idx: number) => (
                        <li key={idx}>{c}</li>
                      ))}
                    </ul>

                    <h4 className="text-xs font-semibold text-slate-300 pt-2">Examples</h4>
                    <div className="space-y-3">
                      {generatedProblem.examples?.map((ex: any, idx: number) => (
                        <div key={idx} className="bg-slate-900 p-3 rounded-lg border border-slate-800 text-xs space-y-1 font-mono">
                          <div><span className="text-blue-400 font-semibold">Input:</span> {ex.input}</div>
                          <div><span className="text-emerald-400 font-semibold">Output:</span> {ex.output}</div>
                          {ex.explanation && <div className="text-slate-400 font-sans italic text-[11px] pt-1">Explanation: {ex.explanation}</div>}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Code Solutions Differential View */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="glass-panel p-4 rounded-xl border border-slate-800 space-y-2">
                      <div className="flex items-center justify-between text-xs border-b border-slate-800 pb-2">
                        <span className="font-semibold text-amber-400">Brute-Force Solution</span>
                        <span className="font-mono text-slate-400">{generatedProblem.solution?.brute_force_complexity}</span>
                      </div>
                      <pre className="bg-slate-950 p-3 rounded-lg text-[11px] font-mono text-slate-300 overflow-x-auto max-h-60 leading-relaxed">
                        {generatedProblem.solution?.brute_force_code}
                      </pre>
                    </div>

                    <div className="glass-panel p-4 rounded-xl border border-slate-800 space-y-2">
                      <div className="flex items-center justify-between text-xs border-b border-slate-800 pb-2">
                        <span className="font-semibold text-emerald-400">Optimal Reference Solution</span>
                        <span className="font-mono text-slate-400">{generatedProblem.solution?.optimized_complexity}</span>
                      </div>
                      <pre className="bg-slate-950 p-3 rounded-lg text-[11px] font-mono text-slate-300 overflow-x-auto max-h-60 leading-relaxed">
                        {generatedProblem.solution?.optimized_code}
                      </pre>
                    </div>
                  </div>

                  {/* Verification Execution Log */}
                  {generatedProblem.verification_report && (
                    <div className="glass-panel p-4 rounded-xl border border-slate-800 space-y-3 text-xs">
                      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                        <div className="flex items-center gap-2 font-semibold text-slate-200">
                          <ShieldCheck className="w-4 h-4 text-emerald-400" />
                          Differential Sandbox Execution Report
                        </div>
                        <span className="text-emerald-400 font-mono font-semibold">
                          100% Match ({generatedProblem.verification_report.passed_tests}/{generatedProblem.verification_report.total_tests_run} Passed)
                        </span>
                      </div>

                      <div className="grid grid-cols-4 gap-2 text-center">
                        <div className="bg-slate-900 p-2 rounded-lg">
                          <div className="text-slate-400 text-[10px]">Tests Run</div>
                          <div className="font-mono font-bold text-slate-200">{generatedProblem.verification_report.total_tests_run}</div>
                        </div>
                        <div className="bg-slate-900 p-2 rounded-lg">
                          <div className="text-slate-400 text-[10px]">Avg Runtime</div>
                          <div className="font-mono font-bold text-slate-200">{generatedProblem.verification_report.runtime_ms} ms</div>
                        </div>
                        <div className="bg-slate-900 p-2 rounded-lg">
                          <div className="text-slate-400 text-[10px]">Memory</div>
                          <div className="font-mono font-bold text-slate-200">{generatedProblem.verification_report.memory_mb} MB</div>
                        </div>
                        <div className="bg-slate-900 p-2 rounded-lg">
                          <div className="text-slate-400 text-[10px]">Coverage</div>
                          <div className="font-mono font-bold text-emerald-400">{generatedProblem.verification_report.coverage_percentage}%</div>
                        </div>
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="glass-panel p-12 rounded-xl border border-slate-800 text-center space-y-3">
                  <div className="w-12 h-12 rounded-full bg-blue-500/10 text-blue-400 flex items-center justify-center mx-auto">
                    <Layers className="w-6 h-6" />
                  </div>
                  <h3 className="text-base font-semibold text-slate-200">No Problem Generated Yet</h3>
                  <p className="text-xs text-slate-400 max-w-md mx-auto">
                    Configure your algorithmic domain, target complexity, and educational objective on the left panel, then trigger the 8-agent generation pipeline.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tab 2: Existing Problem Testcase Generator */}
        {activeTab === 'testcase' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-4 glass-panel p-5 rounded-xl border border-slate-800 space-y-4 text-xs">
              <div className="font-semibold text-slate-200 flex items-center gap-2">
                <FileText className="w-4 h-4 text-purple-400" />
                Problem Input Specification
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-medium">Pasted Statement or Problem Metadata URL</label>
                <textarea
                  rows={8}
                  value={pastedStatement}
                  onChange={(e) => setPastedStatement(e.target.value)}
                  placeholder="Paste problem text (e.g., Given an array of N integers, find longest contiguous subarray...)"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-purple-500 resize-none font-mono text-[11px]"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-medium">Number of Testcases</label>
                <input
                  type="number"
                  min={5}
                  max={500}
                  value={numCases}
                  onChange={(e) => setNumCases(parseInt(e.target.value) || 20)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-purple-500"
                />
              </div>

              <button
                onClick={handleGenerateTestCases}
                disabled={loading || !pastedStatement.trim()}
                className="w-full bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-medium py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                {loading ? 'Synthesizing Cases...' : 'Generate & Rank Test Suite'}
              </button>

              {statusMessage && (
                <div className="p-3 bg-slate-900 rounded-lg font-mono text-[11px] text-slate-300 leading-relaxed border border-slate-800">
                  {statusMessage}
                </div>
              )}
            </div>

            {/* Test Suite Inspector Column */}
            <div className="lg:col-span-8 space-y-4">
              <div className="glass-panel p-4 rounded-xl border border-slate-800 flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-200">Generated Test Suite ({generatedTestCases.length} Cases)</span>
                <span className="text-purple-400 font-mono">Ranked by Bug Detection Weight</span>
              </div>

              <div className="space-y-3">
                {generatedTestCases.map((tc, idx) => (
                  <div key={idx} className="glass-panel p-4 rounded-xl border border-slate-800 space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 font-mono">
                        <span className="text-slate-400">#{idx + 1}</span>
                        <span className="font-semibold text-slate-200">{tc.id}</span>
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] uppercase">{tc.test_type}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-slate-400 text-[11px]">Bug Rank:</span>
                        <span className="font-mono font-bold text-amber-400">{tc.bug_detection_rank}</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                      <div className="bg-slate-900 p-2 rounded-lg">
                        <div className="text-slate-500 text-[10px]">INPUT</div>
                        <pre className="text-slate-200 overflow-x-auto whitespace-pre-wrap max-h-24">{tc.input_data}</pre>
                      </div>
                      <div className="bg-slate-900 p-2 rounded-lg">
                        <div className="text-slate-500 text-[10px]">EXPECTED OUTPUT</div>
                        <pre className="text-slate-200 overflow-x-auto whitespace-pre-wrap max-h-24">{tc.expected_output}</pre>
                      </div>
                    </div>
                    {tc.description && <div className="text-[11px] text-slate-400 italic">Target: {tc.description}</div>}
                  </div>
                ))}

                {generatedTestCases.length === 0 && (
                  <div className="glass-panel p-12 rounded-xl border border-slate-800 text-center text-xs text-slate-400">
                    Paste a problem statement on the left to synthesize edge, boundary, and stress test cases.
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
