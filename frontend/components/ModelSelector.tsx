'use client';

import React, { useState, useEffect } from 'react';
import { Cpu, CheckCircle2, XCircle, RefreshCw } from 'lucide-react';

export default function ModelSelector() {
  const [provider, setProvider] = useState('ollama');
  const [modelName, setModelName] = useState('qwen2.5-coder:7b');
  const [apiBase, setApiBase] = useState('http://localhost:11434');
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchStatus = async () => {
    try {
      const res = await fetch('http://localhost:8080/api/models');
      if (res.ok) {
        const data = await res.json();
        setProvider(data.provider_type);
        setModelName(data.model_name);
        setApiBase(data.api_base);
        setIsConnected(data.is_connected);
      } else {
        setIsConnected(false);
      }
    } catch {
      setIsConnected(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleSwitch = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8080/api/models/switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider_type: provider,
          model_name: modelName,
          api_base: apiBase,
          api_key: ''
        })
      });
      if (res.ok) {
        const data = await res.json();
        setIsConnected(data.is_connected);
      } else {
        setIsConnected(false);
      }
    } catch {
      setIsConnected(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel p-4 rounded-xl border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4 text-xs">
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
          <Cpu className="w-5 h-5" />
        </div>
        <div>
          <div className="font-semibold text-slate-200 text-sm flex items-center gap-2">
            Local Provider Interface
            {isConnected === true && (
              <span className="flex items-center gap-1 text-emerald-400 font-mono text-xs bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                <CheckCircle2 className="w-3 h-3" /> Connected
              </span>
            )}
            {isConnected === false && (
              <span className="flex items-center gap-1 text-rose-400 font-mono text-xs bg-rose-500/10 px-2 py-0.5 rounded-full border border-rose-500/20">
                <XCircle className="w-3 h-3" /> Offline
              </span>
            )}
          </div>
          <p className="text-slate-400">Switch between local Ollama, LM Studio, vLLM, or OpenAI endpoints</p>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
        <select
          value={provider}
          onChange={(e) => setProvider(e.target.value)}
          className="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500"
        >
          <option value="ollama">Ollama</option>
          <option value="openai_compatible">OpenAI Compatible / LM Studio</option>
          <option value="vllm">vLLM Server</option>
        </select>

        <input
          type="text"
          value={modelName}
          onChange={(e) => setModelName(e.target.value)}
          placeholder="Model identifier"
          className="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500 w-36"
        />

        <input
          type="text"
          value={apiBase}
          onChange={(e) => setApiBase(e.target.value)}
          placeholder="API Base URL"
          className="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500 w-44"
        />

        <button
          onClick={handleSwitch}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-500 text-white font-medium px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Switch
        </button>
      </div>
    </div>
  );
}
