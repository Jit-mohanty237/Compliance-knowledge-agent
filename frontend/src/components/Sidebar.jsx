import React from 'react';
import { Plus, Trash2, MessageSquare, PanelLeft, Sparkles } from 'lucide-react';

export default function Sidebar({
  sessions = [],
  currentSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  onToggleSidebar
}) {
  
  // Group sessions by relative date groups
  const groupSessions = (sessionList) => {
    const groups = {
      today: [],
      yesterday: [],
      last7Days: [],
      older: []
    };

    const now = new Date();
    // Start of today (midnight)
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
    // Start of yesterday (midnight)
    const yesterdayStart = todayStart - 24 * 60 * 60 * 1000;
    // Start of 7 days ago
    const sevenDaysAgo = todayStart - 6 * 24 * 60 * 60 * 1000;

    sessionList.forEach((session) => {
      // Default to current time if createdAt is missing
      const date = session.createdAt ? new Date(session.createdAt) : new Date();
      const time = date.getTime();

      if (time >= todayStart) {
        groups.today.push(session);
      } else if (time >= yesterdayStart) {
        groups.yesterday.push(session);
      } else if (time >= sevenDaysAgo) {
        groups.last7Days.push(session);
      } else {
        groups.older.push(session);
      }
    });

    return groups;
  };

  const grouped = groupSessions(sessions);

  const renderSessionRow = (session) => {
    const isActive = session.id === currentSessionId;
    return (
      <div
        key={session.id}
        className={`group relative flex items-center justify-between px-3 py-2 rounded-xl text-sm transition-all duration-150 cursor-pointer ${
          isActive 
            ? 'bg-border/40 text-text-primary font-medium' 
            : 'text-text-secondary hover:bg-border/20 hover:text-text-primary'
        }`}
        onClick={() => onSelectSession(session.id)}
      >
        <div className="flex items-center space-x-2.5 min-w-0 pr-6">
          <MessageSquare className={`w-4 h-4 shrink-0 ${isActive ? 'text-brand' : 'text-text-secondary group-hover:text-text-primary'}`} />
          <span className="truncate text-xs select-none">
            {session.title || 'New Consultation'}
          </span>
        </div>
        
        {/* Hover-revealed delete button */}
        <button
          onClick={(e) => onDeleteSession(session.id, e)}
          className="absolute right-2.5 p-1 rounded-md opacity-0 group-hover:opacity-100 hover:bg-border/40 hover:text-red-505 text-text-secondary hover:text-red-500 transition-opacity duration-155"
          title="Delete chat"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>
    );
  };

  const renderSection = (title, items) => {
    if (items.length === 0) return null;
    return (
      <div className="space-y-1 mt-4 first:mt-0">
        <h3 className="px-3 text-[10px] font-bold text-text-secondary/60 tracking-wider uppercase">
          {title}
        </h3>
        <div className="space-y-0.5">
          {items.map(renderSessionRow)}
        </div>
      </div>
    );
  };

  return (
    <aside className="w-64 bg-card border-r border-border flex flex-col h-screen select-none shrink-0 z-20">
      {/* Top Header - Sidebar Brand Mark and Close Toggle */}
      <div className="h-16 px-4 border-b border-border flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 rounded-md bg-brand flex items-center justify-center">
            <Sparkles className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="font-bold text-xs text-text-primary tracking-tight">Knowledge Hub</span>
        </div>
        <button 
          onClick={onToggleSidebar}
          className="p-1.5 rounded-lg text-text-secondary hover:bg-border/30 hover:text-text-primary transition-colors cursor-pointer"
          title="Collapse sidebar"
        >
          <PanelLeft className="w-4 h-4" />
        </button>
      </div>

      {/* Action Button: New Consultation */}
      <div className="p-3">
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center space-x-2 py-2 px-4 rounded-xl border border-border bg-background hover:bg-border/20 text-text-primary font-medium transition-all duration-150 cursor-pointer shadow-soft text-xs"
        >
          <Plus className="w-4 h-4 text-text-secondary" />
          <span>New Chat</span>
        </button>
      </div>

      {/* Dynamic Session History Groups */}
      <div className="flex-1 overflow-y-auto px-2 py-2 space-y-4">
        {sessions.length === 0 ? (
          <div className="p-4 text-center">
            <p className="text-xs text-text-secondary">No chat history</p>
          </div>
        ) : (
          <>
            {renderSection('Today', grouped.today)}
            {renderSection('Yesterday', grouped.yesterday)}
            {renderSection('Previous 7 Days', grouped.last7Days)}
            {renderSection('Older', grouped.older)}
          </>
        )}
      </div>
    </aside>
  );
}
