import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { User, Check, Copy } from 'lucide-react';

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    // Parse out meta tags before copying to clipboard
    const parsed = parseMetadataAndContent(message.content);
    navigator.clipboard.writeText(parsed.content);
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
    
    return docName
      .replace(/\.[^/.]+$/, "") // strip extension
      .replace(/[_-]/g, " ")    // replace underscores/dashes with spaces
      .replace(/\s+/g, " ")     // replace multiple spaces
      .trim();
  };

  // Extract <meta intent="..."> or <meta category="..."> tag from model response
  const parseMetadataAndContent = (text) => {
    if (!text) return { intent: null, content: '' };
    let intent = null;
    let cleanedContent = text;

    const metaRegex = /<meta\s+(?:intent|category)="([^"]+)"\s*\/?>/i;
    const match = text.match(metaRegex);
    if (match) {
      intent = match[1].toUpperCase();
      cleanedContent = text.replace(new RegExp(metaRegex, 'gi'), '');
    }

    return { intent, content: cleanedContent.trim() };
  };

  const parsed = parseMetadataAndContent(message.content);
  const detectedIntent = parsed.intent || message.intent;
  const messageBody = parsed.content;

  if (isUser) {
    return (
      <div className="flex w-full justify-end mb-4">
        <div className="max-w-[75%] bg-neutral-100 text-text-primary rounded-bubble px-4 py-2.5 text-xs border border-border/40 font-normal leading-relaxed">
          {message.content}
        </div>
      </div>
    );
  }

  // Determine badge colors based on intent
  let badgeClass = 'bg-[var(--badge-general-bg)] text-[var(--badge-general-text)]';
  if (detectedIntent === 'HR') {
    badgeClass = 'bg-[var(--badge-hr-bg)] text-[var(--badge-hr-text)]';
  } else if (detectedIntent === 'COMPLIANCE') {
    badgeClass = 'bg-[var(--badge-compliance-bg)] text-[var(--badge-compliance-text)]';
  }

  return (
    <div className="flex w-full justify-start mb-6 group">
      <div className="flex items-start max-w-[85%] space-x-3.5 w-full">
        {/* Avatar */}
        <div className="w-8 h-8 rounded-xl bg-card border border-border text-text-secondary flex items-center justify-center shrink-0 shadow-soft">
          <User className="w-4 h-4 text-text-secondary" />
        </div>

        {/* Message Card Container */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[9px] font-bold text-text-secondary/65 tracking-wider uppercase">
              AI ASSISTANT
            </span>
            <button
              onClick={handleCopy}
              className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-border/30 text-text-secondary hover:text-text-primary cursor-pointer"
              title="Copy to clipboard"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
            </button>
          </div>

          <div className="rounded-bubble border border-border bg-card shadow-soft overflow-hidden flex flex-col">
            {/* Intent Badge Header (if category detected) */}
            {detectedIntent && (
              <div className="px-4 py-2 border-b border-border bg-background/50 flex items-center justify-between">
                <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider ${badgeClass}`}>
                  {detectedIntent}
                </span>
              </div>
            )}

            {/* Markdown Text Body */}
            <div className="px-4 py-3.5 text-xs text-text-primary leading-relaxed">
              <div className="prose">
                <ReactMarkdown>{messageBody}</ReactMarkdown>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
