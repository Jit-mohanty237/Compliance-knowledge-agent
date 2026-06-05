import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import ChatWindow from '../components/ChatWindow';
import { sendChatMessage } from '../services/api';

export default function Home() {
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load sessions from localStorage on mount
  useEffect(() => {
    const savedSessions = localStorage.getItem('latam_compliance_sessions');
    if (savedSessions) {
      try {
        const parsed = JSON.parse(savedSessions);
        setSessions(parsed);
        if (parsed.length > 0) {
          setCurrentSessionId(parsed[0].id);
        } else {
          startNewSession();
        }
      } catch (e) {
        console.error('Error loading saved sessions:', e);
        startNewSession();
      }
    } else {
      startNewSession();
    }
  }, []);

  // Save sessions to localStorage whenever they change
  useEffect(() => {
    if (sessions.length > 0) {
      localStorage.setItem('latam_compliance_sessions', JSON.stringify(sessions));
    } else {
      localStorage.removeItem('latam_compliance_sessions');
    }
  }, [sessions]);

  // Helper: start a brand new consultation session
  const startNewSession = () => {
    // Generate a temporary frontend UUID to uniquely identify the session
    const newSessionId = crypto.randomUUID();
    const newSession = {
      id: newSessionId,
      title: 'New Consultation',
      messages: [],
    };
    
    setSessions((prev) => [newSession, ...prev]);
    setCurrentSessionId(newSessionId);
    setError(null);
  };

  // Helper: get current active session messages
  const getActiveSessionMessages = () => {
    const active = sessions.find((s) => s.id === currentSessionId);
    return active ? active.messages : [];
  };

  // Callback: Handle sending a new message
  const handleSendMessage = async (text) => {
    if (!text.trim()) return;

    // 1. Construct temporary user message
    const userMessage = { role: 'user', content: text };
    
    // 2. Append user message to active session
    setSessions((prevSessions) =>
      prevSessions.map((session) => {
        if (session.id === currentSessionId) {
          // If first message, generate a clean title from query
          const title = session.title === 'New Consultation' 
            ? text.split(' ').slice(0, 5).join(' ') + (text.split(' ').length > 5 ? '...' : '')
            : session.title;

          return {
            ...session,
            title,
            messages: [...session.messages, userMessage],
          };
        }
        return session;
      })
    );

    setIsLoading(true);
    setError(null);

    try {
      // 3. Send query to FastAPI backend
      const data = await sendChatMessage(text, currentSessionId);
      
      // 4. Construct assistant message from response
      const assistantMessage = { 
        role: 'assistant', 
        content: data.response,
        intent: data.intent,
        source_collection: data.source_collection,
        documents_used: data.documents_used
      };

      // 5. Update session with server-returned session ID and AI reply
      setSessions((prevSessions) =>
        prevSessions.map((session) => {
          if (session.id === currentSessionId) {
            return {
              ...session,
              id: data.session_id, // Sync session ID if mapped differently
              messages: [...session.messages, assistantMessage],
            };
          }
          return session;
        })
      );
      
      // If server returned a new session ID, make it active
      if (data.session_id !== currentSessionId) {
        setCurrentSessionId(data.session_id);
      }
    } catch (err) {
      setError(err.message || 'An error occurred while connecting to the compliance service.');
    } finally {
      setIsLoading(false);
    }
  };

  // Callback: Handle selecting a session from history
  const handleSelectSession = (id) => {
    setCurrentSessionId(id);
    setError(null);
  };

  // Callback: Clear/Reset a specific session's history
  const handleClearHistory = (id) => {
    setSessions((prevSessions) =>
      prevSessions.map((session) => {
        if (session.id === id) {
          return {
            ...session,
            title: 'New Consultation',
            messages: [],
          };
        }
        return session;
      })
    );
    setError(null);
  };

  return (
    <div className="flex w-screen h-screen overflow-hidden bg-[#080b11] text-slate-100">
      {/* Navigation Sidebar */}
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelectSession={handleSelectSession}
        onNewChat={startNewSession}
        onClearHistory={handleClearHistory}
      />
      
      {/* Conversation Thread */}
      <ChatWindow
        messages={getActiveSessionMessages()}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        error={error}
      />
    </div>
  );
}
