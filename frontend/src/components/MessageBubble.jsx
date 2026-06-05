import React, { useState } from 'react';
import { User, Shield, Clipboard, Check, BookOpen, AlertTriangle, ChevronDown, ChevronRight, Scale, Users, Database, HelpCircle, FileText } from 'lucide-react';

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);
  const [sourcesOpen, setSourcesOpen] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getCleanDocName = (docName) => {
    if (!docName) return '';
    const mappings = {
      'KOMP_EOR_Playbook_Ver1.0.xlsx': 'KOMP EOR Playbook',
      'HR Playbook_Employee Lifecycle_Ver1.0.xlsx': 'HR Playbook Employee Lifecycle',
      'latam_laws_flat.json': 'LATAM Laws Database',
      'latam_compliance.json': 'LATAM Compliance Guidelines',
      'latam_keywords.json': 'LATAM Keyword Indices'
    };
    if (mappings[docName]) return mappings[docName];
    
    // Fallback: strip extension and replace underscores/dashes with spaces
    return docName
      .replace(/\.[^/.]+$/, "") // strip extension
      .replace(/[_-]/g, " ")    // replace underscores and dashes with spaces
      .replace(/\s+/g, " ")     // replace multiple spaces
      .trim();
  };

  // Progressive enhancement: parse text into styled HTML elements
  const formatText = (text) => {
    if (!text) return '';
    
    return text.split('\n').map((line, idx) => {
      // Horizontal rules
      if (line.trim() === '====================================================' || line.trim() === '---') {
        return <hr key={idx} className="my-4 border-slate-800/85" />;
      }
      
      // Unordered lists
      if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
        const content = line.trim().replace(/^[-*]\s+/, '');
        return (
          <li key={idx} className="ml-4 list-disc text-slate-350 text-xs leading-relaxed mb-1.5">
            {parseInlineMarkdown(content)}
          </li>
        );
      }

      // Ordered lists
      if (/^\d+\.\s+/.test(line.trim())) {
        const content = line.trim().replace(/^\d+\.\s+/, '');
        return (
          <li key={idx} className="ml-4 list-decimal text-slate-350 text-xs leading-relaxed mb-1.5" style={{ listStyleType: 'decimal' }}>
            {parseInlineMarkdown(content)}
          </li>
        );
      }
      
      // Section headers (e.g. "Applicable laws:")
      if (line.trim().endsWith(':') && line.trim().length < 50) {
        return (
          <h4 key={idx} className="text-[10px] uppercase tracking-widest font-extrabold text-blue-400 mt-4 mb-2 first:mt-1 flex items-center">
            <BookOpen className="w-3.5 h-3.5 mr-1.5 text-blue-500" />
            {line.trim()}
          </h4>
        );
      }

      // Blank paragraphs
      if (line.trim() === '') {
        return <div key={idx} className="h-2.5" />;
      }

      // Standard paragraphs
      return (
        <p key={idx} className="text-slate-350 text-xs leading-relaxed mb-2">
          {parseInlineMarkdown(line)}
        </p>
      );
    });
  };

  // Helper to render bold text and automatically convert citations (Articles/Laws) to styled pills
  const parseInlineMarkdown = (line) => {
    const parts = line.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        const content = part.slice(2, -2);
        return (
          <strong key={index} className="font-semibold text-slate-100">
            {content}
          </strong>
        );
      }
      
      // Auto-detect citations like "Article 245" or "Law No. 729" and style them as custom pills
      const citationRegex = /(Article\s+\d+|Law\s+No\.\s+\d+|Articles\s+\d+[\s\d,and]*\d*|Ley\s+[\w\s\d\.]+)/gi;
      if (citationRegex.test(part)) {
        const subParts = part.split(citationRegex);
        const matches = part.match(citationRegex);
        let matchIdx = 0;
        
        return subParts.map((subPart, subIdx) => {
          if (citationRegex.test(subPart)) {
            const currentMatch = matches[matchIdx++];
            return (
              <span 
                key={subIdx} 
                className="inline-flex items-center px-2 py-0.5 rounded-md bg-blue-950/60 text-blue-400 border border-blue-900/50 text-[10px] font-bold mx-1 shadow-sm select-all cursor-help"
                title="Compliance Database Citation Reference"
              >
                <BookOpen className="w-2.5 h-2.5 mr-1" />
                {currentMatch}
              </span>
            );
          }
          return subPart;
        });
      }
      
      return part;
    });
  };

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-6 group`}>
      <div className={`flex items-start max-w-[85%] space-x-3.5 ${
        isUser ? 'flex-row-reverse space-x-reverse' : 'flex-row'
      }`}>
        
        {/* Avatar with Custom Ring Glow */}
        <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 shadow-md ${
          isUser 
            ? 'bg-slate-800 border border-slate-700 text-slate-300' 
            : 'bg-gradient-to-tr from-blue-600 via-indigo-500 to-purple-600 text-white ring-2 ring-blue-500/20'
        }`}>
          {isUser ? <User className="w-4 h-4" /> : <Shield className="w-4 h-4" />}
        </div>

        {/* Bubble Details */}
        <div className="flex flex-col relative">
          {/* Header Row: Sender + Action Buttons */}
          <div className="flex items-center justify-between mb-1.5">
            <span className={`text-[9px] font-extrabold text-slate-500 tracking-wider ${
              isUser ? 'text-right w-full' : 'text-left'
            }`}>
              {isUser ? 'YOU' : 'KNOWLEDGE HUB ASSISTANT'}
            </span>
            
            {/* Copy Button (Only for assistant responses, visible on hover) */}
            {!isUser && (
              <button
                onClick={handleCopy}
                className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 ml-4 p-1 rounded hover:bg-slate-800 text-slate-500 hover:text-slate-300 cursor-pointer"
                title="Copy response to clipboard"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Clipboard className="w-3.5 h-3.5" />}
              </button>
            )}
          </div>
          
          {/* Text Bubble with Glassmorphic gradient */}
          <div className={`rounded-2xl shadow-xl border transition-all duration-300 overflow-hidden ${
            isUser 
              ? 'bg-gradient-to-r from-blue-600 to-indigo-600 border-blue-500/20 text-white rounded-tr-none hover:shadow-blue-500/5 px-5 py-4' 
              : 'bg-slate-900/40 backdrop-blur-lg border-slate-800/80 text-slate-200 rounded-tl-none hover:border-slate-700/80 hover:shadow-slate-950/20 flex flex-col'
          }`}>
            {isUser ? (
              <p className="text-xs leading-relaxed text-slate-100 whitespace-pre-wrap">{message.content}</p>
            ) : (
              <>
                {/* 1. Header Badges Row inside Response Card */}
                {message.intent && (
                  <div className="flex flex-wrap items-center gap-2 px-5 py-3 border-b border-slate-800/60 bg-slate-950/25">
                    {/* Intent Badge */}
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[9px] font-extrabold uppercase tracking-wider border ${
                      message.intent === 'COMPLIANCE' 
                        ? 'bg-blue-950/50 text-blue-400 border-blue-900/50' 
                        : message.intent === 'HR' 
                          ? 'bg-emerald-950/50 text-emerald-400 border-emerald-900/50' 
                          : 'bg-amber-950/50 text-amber-400 border-amber-900/50'
                    }`}>
                      {message.intent === 'COMPLIANCE' ? (
                        <Scale className="w-2.5 h-2.5 mr-1" />
                      ) : message.intent === 'HR' ? (
                        <Users className="w-2.5 h-2.5 mr-1" />
                      ) : (
                        <HelpCircle className="w-2.5 h-2.5 mr-1" />
                      )}
                      Intent: {message.intent}
                    </span>

                    {/* Source Collection Badge */}
                    {message.source_collection && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full bg-slate-900/80 border border-slate-800/80 text-[9px] text-slate-400 font-extrabold uppercase tracking-wider">
                        <Database className="w-2.5 h-2.5 mr-1 text-slate-500" />
                        KB: {message.source_collection}
                      </span>
                    )}
                  </div>
                )}

                {/* 2. AI-generated Answer body */}
                <div className="px-5 py-4 space-y-0.5">
                  {formatText(message.content)}
                </div>

                {/* 3. Collapsible Source Section at bottom of card */}
                {message.documents_used && message.documents_used.length > 0 && (
                  <div className="border-t border-slate-800/60 bg-slate-950/15">
                    <button
                      onClick={() => setSourcesOpen(!sourcesOpen)}
                      className="w-full flex items-center justify-between px-5 py-3 text-[10px] font-bold text-slate-400 hover:text-slate-200 transition-colors cursor-pointer select-none"
                    >
                      <span className="flex items-center space-x-1.5">
                        <BookOpen className="w-3.5 h-3.5 text-slate-500" />
                        <span>Sources Used ({message.documents_used.length})</span>
                      </span>
                      {sourcesOpen ? (
                        <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
                      ) : (
                        <ChevronRight className="w-3.5 h-3.5 text-slate-500" />
                      )}
                    </button>
                    
                    {sourcesOpen && (
                      <div className="px-5 pb-4 pt-1 space-y-1.5 border-t border-slate-900/40">
                        {message.documents_used.map((doc, dIdx) => (
                          <div key={dIdx} className="flex items-center space-x-2 text-[10px] text-slate-450 bg-slate-900/20 px-2.5 py-1.5 rounded-md border border-slate-850">
                            <FileText className="w-3 h-3 text-blue-500/70" />
                            <span className="font-semibold text-slate-350">{getCleanDocName(doc)}</span>
                            <span className="text-[8px] text-slate-600 font-mono">({doc})</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
