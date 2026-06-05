import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, AlertCircle, Sparkles, Scale, Info, Database, Zap, ShieldAlert, Award, Users } from 'lucide-react';
import MessageBubble from './MessageBubble';

export default function ChatWindow({ 
  messages = [], 
  onSendMessage, 
  isLoading, 
  error 
}) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  // Auto-scroll to the bottom of the container whenever messages or loading state changes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-screen bg-[#070a13] relative overflow-hidden">
      {/* Background Aurora Glow Effects */}
      <div className="absolute top-[-20%] right-[-10%] w-[500px] h-[500px] rounded-full bg-blue-600/10 blur-[120px] pointer-events-none z-0" />
      <div className="absolute bottom-[-10%] left-[-10%] w-[450px] h-[450px] rounded-full bg-indigo-600/5 blur-[120px] pointer-events-none z-0" />

      {/* Top Navigation Header */}
      <header className="h-16 border-b border-slate-800/60 bg-[#070a13]/60 backdrop-blur-md flex items-center justify-between px-8 z-10">
        <div className="flex items-center space-x-3">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
          <div>
            <h2 className="text-xs font-bold text-slate-100 flex items-center tracking-wide uppercase">
              Compliance & HR Knowledge Hub
              <Sparkles className="w-3.5 h-3.5 ml-1.5 text-blue-400" />
            </h2>
            <p className="text-[10px] text-slate-500 font-medium">Multi-Knowledge-Base AI Assistant Suite</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className="font-mono bg-slate-900 border border-slate-800 px-2 py-0.5 rounded text-[9px] font-bold text-blue-400">Gemini 2.5 Flash Active</span>
        </div>
      </header>

      {/* Messages Feed Area */}
      <div className="flex-1 overflow-y-auto px-8 py-6 space-y-4 z-10 relative">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-3xl mx-auto py-8">
            
            {/* Branding Shield */}
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-500 flex items-center justify-center shadow-lg shadow-blue-500/20 mb-5 relative group">
              <Scale className="w-7 h-7 text-white transition-transform duration-300 group-hover:rotate-12" />
              <div className="absolute inset-0 rounded-2xl bg-blue-500/20 blur-md -z-10 animate-pulse" />
            </div>
            
            <h3 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-blue-400 tracking-tight mb-2">
              Compliance & HR Knowledge Hub
            </h3>
            <p className="text-xs text-slate-450 leading-relaxed max-w-xl mb-8">
              Query our integrated global Employer of Record compliance playbook and HR lifecycle database to verify legal codes, employee benefits, onboarding, recruitment, and termination policies.
            </p>

            {/* Quick Metrics Dashboard */}
            <div className="grid grid-cols-3 gap-4 w-full max-w-2xl mb-8">
              {[
                { icon: <Database className="w-4 h-4 text-blue-400" />, label: 'INDEXED KNOWLEDGE BASES', val: '2 Active Databases' },
                { icon: <Zap className="w-4 h-4 text-amber-400" />, label: 'LATENCY SPEED', val: '1.2s Average' },
                { icon: <Award className="w-4 h-4 text-purple-400" />, label: 'RAG MATCH RATE', val: '99.2% Relevance' }
              ].map((metric, i) => (
                <div key={i} className="p-3.5 rounded-xl border border-slate-800/80 bg-slate-950/40 backdrop-blur-md flex flex-col items-center text-center">
                  <div className="p-1.5 rounded-lg bg-slate-900 mb-2 border border-slate-800">{metric.icon}</div>
                  <span className="text-[8px] font-extrabold text-slate-500 tracking-wider mb-0.5">{metric.label}</span>
                  <span className="text-xs font-semibold text-slate-200">{metric.val}</span>
                </div>
              ))}
            </div>

            {/* Suggested Consultations Section */}
            <div className="w-full max-w-3xl mt-4">
              <h4 className="text-[10px] uppercase font-bold tracking-widest text-slate-500 mb-4 text-left border-b border-slate-850 pb-2">
                Quick Start Suggestions
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
                {/* Compliance Column */}
                <div className="space-y-3">
                  <div className="flex items-center space-x-2 text-xs font-bold text-blue-400 px-1">
                    <Scale className="w-4 h-4" />
                    <span>Global Compliance</span>
                  </div>
                  <div className="space-y-2">
                    {[
                      { topic: 'Brazil labor laws', query: 'What are the main labor law requirements in Brazil?' },
                      { topic: 'Mexico payroll compliance', query: 'Explain the payroll compliance regulations in Mexico.' },
                      { topic: 'Argentina employment regulations', query: 'What is the mandatory employee severance policy in Argentina?' }
                    ].map((item, idx) => (
                      <button
                        key={idx}
                        onClick={() => onSendMessage(item.query)}
                        className="w-full p-3.5 text-left rounded-xl border border-slate-850 bg-slate-900/10 hover:bg-slate-900/40 hover:border-slate-700/80 hover:-translate-y-0.5 text-xs transition-all duration-300 cursor-pointer shadow-sm hover:shadow-blue-500/5 block group"
                      >
                        <div className="flex justify-between items-center mb-1">
                          <span className="font-bold text-slate-200 group-hover:text-white transition">{item.topic}</span>
                          <span className="text-[9px] text-slate-550 group-hover:text-blue-450 font-mono">Run query →</span>
                        </div>
                        <span className="text-[10px] text-slate-500 block truncate">{item.query}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* HR Column */}
                <div className="space-y-3">
                  <div className="flex items-center space-x-2 text-xs font-bold text-emerald-400 px-1">
                    <Users className="w-4 h-4" />
                    <span>HR & Employee Operations</span>
                  </div>
                  <div className="space-y-2">
                    {[
                      { topic: 'Employee onboarding', query: 'What is the employee onboarding checklist and timeline?' },
                      { topic: 'Leave policy', query: 'What are the maternity leave policies across different countries?' },
                      { topic: 'Employee lifecycle', query: 'What are the categories, projects, and priorities in the Employee Lifecycle playbook?' },
                      { topic: 'Recruitment process', query: 'What is the recruitment and selection process in the HR playbook?' }
                    ].map((item, idx) => (
                      <button
                        key={idx}
                        onClick={() => onSendMessage(item.query)}
                        className="w-full p-3.5 text-left rounded-xl border border-slate-850 bg-slate-900/10 hover:bg-slate-900/40 hover:border-slate-700/80 hover:-translate-y-0.5 text-xs transition-all duration-300 cursor-pointer shadow-sm hover:shadow-emerald-500/5 block group"
                      >
                        <div className="flex justify-between items-center mb-1">
                          <span className="font-bold text-slate-200 group-hover:text-white transition">{item.topic}</span>
                          <span className="text-[9px] text-slate-550 group-hover:text-emerald-450 font-mono">Run query →</span>
                        </div>
                        <span className="text-[10px] text-slate-500 block truncate">{item.query}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            
          </div>
        ) : (
          <>
            {messages.map((msg, index) => (
              <MessageBubble key={index} message={msg} />
            ))}
            
            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex w-full justify-start mb-6">
                <div className="flex items-start max-w-[85%] space-x-3.5">
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-655 to-purple-600 text-white flex items-center justify-center shadow-md animate-pulse">
                    <Loader2 className="w-4 h-4 animate-spin" />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[9px] font-bold text-slate-500 tracking-wider mb-1">KNOWLEDGE HUB ADVISOR</span>
                    <div className="rounded-2xl px-5 py-4 border border-slate-800/80 bg-slate-900/30 backdrop-blur-md flex items-center space-x-3 text-slate-400 rounded-tl-none shadow-lg">
                      <div className="flex space-x-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '0ms' }} />
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '150ms' }} />
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                      <span className="text-xs ml-2 text-slate-400">Searching knowledge bases & generating compliance/HR analysis...</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Error Banner */}
            {error && (
              <div className="flex items-center space-x-3 p-4 rounded-xl border border-red-900/30 bg-red-950/15 text-red-400 max-w-2xl mx-auto my-4 shadow-lg shadow-red-950/20 backdrop-blur-md">
                <AlertCircle className="w-5 h-5 shrink-0 text-red-500" />
                <div>
                  <p className="text-xs font-bold text-red-300">Analysis Error</p>
                  <p className="text-[10px] text-red-400 mt-0.5">{error}</p>
                </div>
              </div>
            )}

            {/* Auto-scroll target */}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Form Area */}
      <div className="p-6 border-t border-slate-800/60 bg-[#070a13]/60 backdrop-blur-md z-10 relative">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative flex items-center bg-slate-900/40 border border-slate-850 rounded-2xl p-1.5 focus-within:border-blue-500/40 focus-within:ring-4 focus-within:ring-blue-500/5 transition shadow-lg">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a compliance or labor law question..."
            rows="1"
            className="flex-1 bg-transparent border-0 outline-none text-slate-100 placeholder-slate-655 text-xs px-4 py-3.5 resize-none max-h-32 min-h-[46px]"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="w-10 h-10 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-650 hover:from-blue-500 hover:to-indigo-550 disabled:from-slate-850 disabled:to-slate-850 disabled:text-slate-600 text-white flex items-center justify-center transition-all duration-300 shadow-md cursor-pointer shrink-0"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        <div className="max-w-4xl mx-auto flex items-center space-x-1.5 mt-2 px-2 text-[9px] text-slate-650 justify-center">
          <Info className="w-3.5 h-3.5 text-slate-700" />
          <span>Responses represent legislative guidance gathered via vector indexing and should be cross-checked with official gazettes.</span>
        </div>
      </div>
    </div>
  );
}
