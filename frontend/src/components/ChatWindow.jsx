import React, { useState, useRef, useEffect } from 'react';
import { Send, PanelLeft, Plus, Sparkles, HelpCircle } from 'lucide-react';
import MessageBubble from './MessageBubble';

const SUGGESTIONS = [
  { label: 'Brazil Labor Laws', query: 'What are the main labor law requirements in Brazil?' },
  { label: 'Onboarding', query: 'What is the employee onboarding checklist and timeline?' },
  { label: 'Leave', query: 'What are the maternity leave policies?' },
  { label: 'Payroll', query: 'Explain the payroll compliance regulations in Mexico.' },
  { label: 'Recruitment', query: 'What is the recruitment and selection process in the HR playbook?' },
  { label: 'Lifecycle', query: 'What are the categories, projects, and priorities in the Employee Lifecycle playbook?' }
];

export default function ChatWindow({ 
  messages = [], 
  onSendMessage, 
  isLoading, 
  error,
  isSidebarOpen,
  onToggleSidebar,
  onNewChat
}) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll to the bottom of the container whenever messages or loading state changes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Auto-focus input when session changes or loading finishes
  useEffect(() => {
    if (!isLoading && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [messages.length, isLoading]);

  // Auto-grow textarea effect
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      // Restrict maximum height to 200px
      const nextHeight = Math.min(textarea.scrollHeight, 200);
      textarea.style.height = `${nextHeight}px`;
    }
  }, [input]);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
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
    <div className="flex-1 flex flex-col h-screen bg-background relative overflow-hidden text-text-primary">
      {/* Top Navigation Header */}
      <header className="sticky top-0 h-16 border-b border-border bg-background/80 backdrop-blur-md flex items-center justify-between px-6 z-10 shrink-0">
        <div className="flex items-center space-x-3">
          {!isSidebarOpen && (
            <button 
              onClick={onToggleSidebar}
              className="p-1.5 rounded-lg text-text-secondary hover:bg-border/30 hover:text-text-primary transition-colors cursor-pointer"
              title="Open sidebar"
              id="sidebar-toggle-btn"
            >
              <PanelLeft className="w-4 h-4" />
            </button>
          )}
          <div className="flex items-center space-x-2">
            <div className="w-5 h-5 rounded-md bg-brand flex items-center justify-center">
              <Sparkles className="w-3 h-3 text-white" />
            </div>
            <span className="font-bold text-xs tracking-tight">Compliance & HR Hub</span>
          </div>
        </div>

        <button
          onClick={onNewChat}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full border border-border bg-background hover:bg-border/20 text-xs text-text-primary font-medium transition-all shadow-soft cursor-pointer"
          title="Start a new chat"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Chat</span>
        </button>
      </header>

      {/* Messages Feed Area */}
      <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-6 z-0 relative">
        <div className="max-w-3xl mx-auto w-full">
          {messages.length === 0 ? (
            <div className="min-h-[60vh] flex flex-col items-center justify-center text-center py-12">
              <div className="w-12 h-12 rounded-2xl bg-brand/10 text-brand flex items-center justify-center mb-6">
                <Sparkles className="w-6 h-6" />
              </div>
              
              <h2 className="text-xl md:text-2xl font-bold tracking-tight mb-2">
                Compliance & HR Knowledge Hub
              </h2>
              <p className="text-xs text-text-secondary leading-relaxed max-w-md mb-8">
                Search employment policies, onboarding processes, leave structures, and labor regulations with our AI compliance assistant.
              </p>

              {/* Suggestion Chips */}
              <div className="w-full max-w-xl">
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {SUGGESTIONS.map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => onSendMessage(item.query)}
                      className="p-3 text-left rounded-xl border border-border bg-card hover:bg-border/20 text-xs transition-all duration-150 cursor-pointer shadow-soft block"
                    >
                      <span className="font-medium text-text-primary block truncate mb-0.5">{item.label}</span>
                      <span className="text-[10px] text-text-secondary block truncate">{item.query}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-6 pb-32">
              {messages.map((msg, index) => (
                <MessageBubble key={index} message={msg} />
              ))}
              
              {/* Thinking Indicator */}
              {isLoading && (
                <div className="flex w-full justify-start mb-6">
                  <div className="flex items-start max-w-[85%] space-x-3.5">
                    <div className="w-8 h-8 rounded-xl bg-card border border-border text-text-secondary flex items-center justify-center shadow-soft">
                      <div className="relative flex h-2.5 w-2.5">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-brand"></span>
                      </div>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[9px] font-bold text-text-secondary/60 tracking-wider mb-1">AI ASSISTANT</span>
                      <div className="rounded-2xl px-4 py-3 border border-border bg-card shadow-soft text-xs text-text-secondary">
                        Analyzing sources and drafting response...
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Error Banner */}
              {error && (
                <div className="flex items-center space-x-3 p-4 rounded-xl border border-red-250 bg-red-50 text-red-700 max-w-2xl mx-auto my-4 shadow-soft">
                  <div className="w-2 h-2 rounded-full bg-red-500" />
                  <div className="flex-1">
                    <p className="text-xs font-bold">Analysis Error</p>
                    <p className="text-[10px] text-red-650 mt-0.5">{error}</p>
                  </div>
                </div>
              )}

              {/* Auto-scroll target */}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Floating Composer Area with Gradient Mask */}
      <div className="absolute bottom-0 left-0 right-0 pt-16 pb-6 px-4 bg-gradient-to-t from-background via-background/95 to-transparent z-10 pointer-events-none">
        <div className="max-w-3xl mx-auto w-full pointer-events-auto">
          <form onSubmit={handleSubmit} className="relative flex items-end bg-card border border-border rounded-2xl p-1.5 shadow-elevated focus-within:border-brand/50 transition">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a compliance or policy question..."
              rows="1"
              className="flex-1 bg-transparent border-0 outline-none text-text-primary placeholder-text-secondary/50 text-xs px-4 py-3.5 resize-none max-h-48 min-h-[44px]"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="w-9 h-9 rounded-bubble bg-brand hover:bg-brand-hover disabled:bg-border/60 disabled:text-text-secondary/40 text-brand-text flex items-center justify-center transition shadow-soft cursor-pointer shrink-0 ml-1 mb-1"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>
          <div className="flex items-center space-x-1 mt-2 px-2 text-[9px] text-text-secondary/60 justify-center">
            <HelpCircle className="w-3 h-3 text-text-secondary/40" />
            <span>Responses are synthesized from policy databases and should be verified.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
