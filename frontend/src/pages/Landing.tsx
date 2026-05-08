import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Bot, Shield, Zap, Database, ArrowRight, Globe } from 'lucide-react';

const Landing: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background text-white selection:bg-primary/30">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 py-6 backdrop-blur-md bg-background/50 border-b border-white/5">
        <div className="text-2xl font-bold text-gradient">SWS AI</div>
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-white/70">
          <a href="#features" className="hover:text-white transition-colors">Features</a>
          <a href="#architecture" className="hover:text-white transition-colors">Architecture</a>
          <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
        </div>
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/login')} className="text-sm font-medium hover:text-white transition-colors">Login</button>
          <button onClick={() => navigate('/signup')} className="btn-primary py-2 px-5 text-sm">Get Started</button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-8 overflow-hidden">
        {/* Animated Background Mesh */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[120%] h-[120%] bg-mesh-gradient opacity-40 pointer-events-none" />
        <div className="absolute top-[10%] left-[20%] w-[40%] h-[40%] bg-primary/20 blur-[150px] rounded-full animate-pulse-slow" />
        <div className="absolute bottom-[10%] right-[20%] w-[40%] h-[40%] bg-secondary/20 blur-[150px] rounded-full animate-pulse-slow" />

        <div className="max-w-6xl mx-auto text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <span className="inline-block px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-primary-light text-xs font-semibold uppercase tracking-wider mb-6">
              The Future of Enterprise Intelligence
            </span>
            <h1 className="text-6xl md:text-8xl font-bold mb-8 leading-tight">
              Enterprise AI <br />
              <span className="text-gradient">Powered by RAG</span>
            </h1>
            <p className="text-lg md:text-xl text-white/60 max-w-2xl mx-auto mb-10 leading-relaxed">
              Unlock the power of your company's data with our production-grade RAG architecture. 
              Upload documents, query policies, and get context-aware answers instantly.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <button 
                onClick={() => navigate('/signup')}
                className="btn-primary py-4 px-8 text-lg flex items-center gap-2 group shadow-[0_0_20px_rgba(59,130,246,0.3)]"
              >
                Start Building <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
              </button>
              <button className="btn-secondary py-4 px-8 text-lg flex items-center gap-2 border border-white/10">
                <Globe size={20} /> View Source
              </button>
            </div>
          </motion.div>

          {/* AI Dashboard Preview */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.2 }}
            className="mt-20 relative"
          >
            <div className="absolute -inset-1 bg-gradient-to-r from-primary to-secondary rounded-[2.5rem] blur opacity-25" />
            <div className="relative glass-card bg-black/40 border-white/10 rounded-[2rem] overflow-hidden shadow-2xl">
              <img 
                src="https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&q=80&w=2000" 
                alt="AI Dashboard Preview" 
                className="w-full opacity-60 grayscale hover:grayscale-0 transition-all duration-700"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent" />
              
              {/* Floating UI Elements */}
              <div className="absolute top-1/4 left-10 p-4 glass-card bg-white/5 border-white/10 animate-float">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center">
                    <Zap size={16} className="text-green-500" />
                  </div>
                  <div className="text-left">
                    <div className="text-[10px] text-white/40 uppercase">Latency</div>
                    <div className="text-sm font-bold">120ms</div>
                  </div>
                </div>
              </div>

              <div className="absolute bottom-1/4 right-10 p-4 glass-card bg-white/5 border-white/10 animate-float [animation-delay:2s]">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                    <Database size={16} className="text-primary-light" />
                  </div>
                  <div className="text-left">
                    <div className="text-[10px] text-white/40 uppercase">Vectors Stored</div>
                    <div className="text-sm font-bold">1.2M+</div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-32 px-8 relative">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold mb-4">Unmatched Capabilities</h2>
            <p className="text-white/50">Everything you need to build production AI applications.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { icon: Bot, title: 'RAG Pipeline', desc: 'Advanced Retrieval Augmented Generation for grounded AI responses.' },
              { icon: Shield, title: 'Secure & Private', desc: 'Enterprise-grade encryption and secure document handling.' },
              { icon: Zap, title: 'Lightning Fast', desc: 'Sub-second response times with optimized vector search.' },
            ].map((f, i) => (
              <motion.div
                key={i}
                whileHover={{ y: -10 }}
                className="p-8 glass-card bg-white/5 border-white/10 text-left group"
              >
                <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center mb-6 group-hover:bg-primary/20 transition-colors">
                  <f.icon className="text-primary-light" size={24} />
                </div>
                <h3 className="text-xl font-bold mb-3">{f.title}</h3>
                <p className="text-white/50 text-sm leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-20 px-8 border-t border-white/5 bg-black/20">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-10">
          <div>
            <div className="text-2xl font-bold text-gradient mb-4">SWS AI</div>
            <p className="text-white/40 text-sm">Next-generation AI for the modern enterprise.</p>
          </div>
          <div className="flex gap-10">
            <div className="space-y-4">
              <div className="font-bold text-sm">Product</div>
              <ul className="text-white/40 text-sm space-y-2">
                <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Security</a></li>
              </ul>
            </div>
            <div className="space-y-4">
              <div className="font-bold text-sm">Company</div>
              <ul className="text-white/40 text-sm space-y-2">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>
          </div>
        </div>
        <div className="max-w-6xl mx-auto mt-20 pt-8 border-t border-white/5 text-center text-white/20 text-xs">
          © 2026 SWS AI. All rights reserved. Built with passion for excellence.
        </div>
      </footer>
    </div>
  );
};

export default Landing;
