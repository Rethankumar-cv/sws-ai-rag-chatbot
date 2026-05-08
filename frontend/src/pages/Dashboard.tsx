import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Send, Paperclip, Bot, User, Copy, RefreshCw } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useChatStore } from '../store/chatStore';
import { cn } from '../lib/utils';

const Dashboard: React.FC = () => {
  const { messages, sendMessage, isTyping, fetchConversations } = useChatStore();
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;
    const content = input;
    setInput('');
    await sendMessage(content);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="h-full flex flex-col max-w-5xl mx-auto relative">
      {/* Header Info */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">AI Assistant</h1>
          <p className="text-white/50 text-sm">Powered by RAG Architecture & Gemini</p>
        </div>
        <div className="flex gap-2">
          <div className="glass-card px-3 py-1 text-xs flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            System Ready
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto space-y-6 pb-32 px-2 scroll-smooth"
      >
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-50">
            <div className="w-20 h-20 rounded-3xl bg-white/5 flex items-center justify-center">
              <Bot size={40} className="text-primary-light" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">How can I help you today?</h2>
              <p className="max-w-md mx-auto text-sm mt-2">
                Ask me anything about your uploaded documents or start a general conversation.
              </p>
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              key={msg.id || idx}
              className={cn(
                "flex gap-4",
                msg.role === 'user' ? "flex-row-reverse" : "flex-row"
              )}
            >
              <div className={cn(
                "w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0",
                msg.role === 'user' ? "bg-primary/20 text-primary-light" : "bg-white/10 text-white/70"
              )}>
                {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
              </div>
              
              <div className={cn(
                "max-w-[80%] glass-card p-4 message-bubble",
                msg.role === 'user' ? "bg-primary/10 border-primary/20" : "bg-white/5 border-white/10"
              )}>
                <div className="markdown-content">
                  <ReactMarkdown
                    components={{
                      code({ node, inline, className, children, ...props }: any) {
                        const match = /language-(\w+)/.exec(className || '');
                        return !inline && match ? (
                          <SyntaxHighlighter
                            style={atomDark}
                            language={match[1]}
                            PreTag="div"
                            {...props}
                          >
                            {String(children).replace(/\n$/, '')}
                          </SyntaxHighlighter>
                        ) : (
                          <code className={className} {...props}>
                            {children}
                          </code>
                        );
                      }
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                </div>
                
                <div className="mt-2 flex items-center justify-between opacity-0 hover:opacity-100 transition-opacity">
                  <span className="text-[10px] text-white/30">
                    {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                  <button className="p-1 hover:bg-white/5 rounded transition-colors text-white/40">
                    <Copy size={12} />
                  </button>
                </div>
              </div>
            </motion.div>
          ))
        )}

        {isTyping && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-4"
          >
            <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
              <Bot size={20} className="text-white/70" />
            </div>
            <div className="glass-card p-4 bg-white/5 flex gap-1">
              <span className="w-1.5 h-1.5 bg-white/40 rounded-full animate-bounce" />
              <span className="w-1.5 h-1.5 bg-white/40 rounded-full animate-bounce [animation-delay:0.2s]" />
              <span className="w-1.5 h-1.5 bg-white/40 rounded-full animate-bounce [animation-delay:0.4s]" />
            </div>
          </motion.div>
        )}
      </div>

      {/* Input Area */}
      <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-background via-background/80 to-transparent">
        <div className="relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-primary/50 to-secondary/50 rounded-2xl blur opacity-25 group-focus-within:opacity-50 transition-opacity duration-500" />
          <div className="relative glass-card flex items-end gap-2 p-2 bg-black/40 border-white/10">
            <button className="p-3 hover:bg-white/5 rounded-xl transition-colors text-white/50">
              <Paperclip size={20} />
            </button>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message SWS AI..."
              className="flex-1 bg-transparent border-none focus:ring-0 resize-none py-3 px-2 text-sm max-h-40 min-h-[44px]"
              rows={1}
            />
            <button 
              onClick={handleSend}
              disabled={!input.trim() || isTyping}
              className={cn(
                "p-3 rounded-xl transition-all",
                input.trim() && !isTyping 
                  ? "bg-primary text-white shadow-lg shadow-primary/20 scale-100" 
                  : "bg-white/5 text-white/20 scale-90"
              )}
            >
              {isTyping ? <RefreshCw size={20} className="animate-spin" /> : <Send size={20} />}
            </button>
          </div>
        </div>
        <p className="text-[10px] text-center text-white/30 mt-3">
          AI can make mistakes. Consider checking important information.
        </p>
      </div>
    </div>
  );
};

export default Dashboard;
