import React from 'react';
import { PlusCircle, Shield, Globe, RefreshCw, MessageSquare, CheckCircle, Lock, BookOpen, Users, Landmark, Scale, HelpCircle } from 'lucide-react';

export default function Sidebar({
  sessions = [],
  currentSessionId,
  onSelectSession,
  onNewChat,
  onClearHistory
}) {
  return (
    <aside className="w-80 bg-slate-950 border-r border-slate-900 flex flex-col h-screen select-none shrink-0 z-10">
      {/* Header Branding */}
      <div className="p-6 border-b border-slate-900 flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/25 relative">
          <Shield className="w-5 h-5 text-white" />
          <div className="absolute inset-0 rounded-xl bg-blue-500/10 blur-sm -z-10" />
        </div>
        <div>
          <h1 className="font-extrabold text-slate-100 text-sm leading-tight tracking-tight">Compliance & HR</h1>
          <p className="text-[9px] text-blue-400 font-extrabold flex items-center mt-0.5 uppercase tracking-wider">
            <Globe className="w-3 h-3 mr-1 animate-pulse" />
            Knowledge Hub
          </p>
        </div>
      </div>

      {/* Knowledge Sources Panel */}
      <div className="px-6 py-4 border-b border-slate-900/60 bg-slate-950/20 space-y-3">
        <span className="text-[9px] uppercase font-extrabold tracking-widest text-slate-500 block">KNOWLEDGE SOURCES</span>
        <div className="space-y-2">
          {/* Active Knowledge Sources */}
          <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/40 border border-slate-800/80">
            <div className="flex items-center space-x-2">
              <Scale className="w-3.5 h-3.5 text-blue-400" />
              <span className="text-xs font-semibold text-slate-200">Compliance</span>
            </div>
            <span className="flex items-center space-x-1 text-[8px] font-bold text-emerald-400 bg-emerald-950/40 border border-emerald-900/60 px-1.5 py-0.5 rounded-full uppercase tracking-wider">
              <CheckCircle className="w-2 h-2" />
              <span>Active</span>
            </span>
          </div>

          <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/40 border border-slate-800/80">
            <div className="flex items-center space-x-2">
              <Users className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-xs font-semibold text-slate-200">HR Policies</span>
            </div>
            <span className="flex items-center space-x-1 text-[8px] font-bold text-emerald-400 bg-emerald-950/40 border border-emerald-900/60 px-1.5 py-0.5 rounded-full uppercase tracking-wider">
              <CheckCircle className="w-2 h-2" />
              <span>Active</span>
            </span>
          </div>

          {/* Upcoming Sources */}
          <div className="flex items-center justify-between p-2 rounded-lg bg-slate-950 border border-slate-900/60 opacity-40 select-none">
            <div className="flex items-center space-x-2">
              <BookOpen className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-xs font-semibold text-slate-400">Legal</span>
            </div>
            <span className="flex items-center space-x-1 text-[8px] font-bold text-slate-500 bg-slate-900 border border-slate-850 px-1.5 py-0.5 rounded-full uppercase tracking-wider">
              <Lock className="w-2 h-2" />
              <span>Soon</span>
            </span>
          </div>

          <div className="flex items-center justify-between p-2 rounded-lg bg-slate-950 border border-slate-900/60 opacity-40 select-none">
            <div className="flex items-center space-x-2">
              <Landmark className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-xs font-semibold text-slate-400">Payroll</span>
            </div>
            <span className="flex items-center space-x-1 text-[8px] font-bold text-slate-500 bg-slate-900 border border-slate-850 px-1.5 py-0.5 rounded-full uppercase tracking-wider">
              <Lock className="w-2 h-2" />
              <span>Soon</span>
            </span>
          </div>

          <div className="flex items-center justify-between p-2 rounded-lg bg-slate-950 border border-slate-900/60 opacity-40 select-none">
            <div className="flex items-center space-x-2">
              <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-xs font-semibold text-slate-400">Benefits</span>
            </div>
            <span className="flex items-center space-x-1 text-[8px] font-bold text-slate-500 bg-slate-900 border border-slate-850 px-1.5 py-0.5 rounded-full uppercase tracking-wider">
              <Lock className="w-2 h-2" />
              <span>Soon</span>
            </span>
          </div>
        </div>
      </div>

      {/* Primary Action Button with Gradient Glow */}
      <div className="p-4">
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-650 to-blue-700 hover:shadow-lg hover:shadow-blue-500/20 text-white font-bold transition-all duration-300 border border-blue-500/20 cursor-pointer hover:scale-[1.01]"
        >
          <PlusCircle className="w-4 h-4" />
          <span className="text-xs tracking-wide">New Consultation</span>
        </button>
      </div>

      {/* Sessions / History */}
      <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
        <div className="px-3 mb-2 flex items-center justify-between">
          <span className="text-[9px] uppercase font-extrabold tracking-widest text-slate-505">CONSULTATION THREADS</span>
          {sessions.length > 0 && (
            <span className="text-[8px] font-mono text-slate-500 bg-slate-900 border border-slate-850 px-1.5 py-0.5 rounded">
              {sessions.length} sessions
            </span>
          )}
        </div>

        {sessions.length === 0 ? (
          <div className="p-5 text-center rounded-xl border border-dashed border-slate-800/80 bg-slate-900/10">
            <p className="text-xs text-slate-500 font-medium">No active sessions yet.</p>
          </div>
        ) : (
          sessions.map((session) => (
            <button
              key={session.id}
              onClick={() => onSelectSession(session.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-200 border cursor-pointer group ${currentSessionId === session.id
                  ? 'bg-slate-900 text-white border-slate-800 shadow-inner border-l-2 border-l-blue-500'
                  : 'text-slate-400 hover:bg-slate-900/50 hover:text-slate-200 border-transparent hover:border-slate-900'
                }`}
            >
              <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${currentSessionId === session.id ? 'text-blue-400' : 'text-slate-550 group-hover:text-slate-400'
                }`} />
              <div className="truncate flex-1">
                <span className="text-[11px] font-bold block truncate tracking-wide">
                  {session.title || 'Chile / Argentina labor compliance'}
                </span>
                <span className="text-[8px] font-mono text-slate-500 block mt-0.5">
                  ID: {session.id.substring(0, 8)}...
                </span>
              </div>
            </button>
          ))
        )}
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-900 bg-slate-950/40 space-y-3">
        {currentSessionId && (
          <button
            onClick={() => onClearHistory(currentSessionId)}
            className="w-full flex items-center justify-center space-x-1.5 py-2 px-3 rounded-lg border border-slate-800 hover:border-red-950/40 hover:bg-red-950/15 text-[10px] text-slate-450 hover:text-red-400 font-bold transition-all cursor-pointer"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Reset Consultation Thread</span>
          </button>
        )}
        {/* <div className="flex items-center justify-between text-[10px] text-slate-500">
          <span>Ollama model:</span>
          <span className="font-mono bg-slate-900 px-2 py-0.5 rounded border border-slate-800 text-blue-400">qwen2.5:1.5b</span>
        </div> */}
      </div>
    </aside>
  );
}
