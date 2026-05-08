import React from 'react';
import { Cpu, Thermometer, Database, User, LogOut } from 'lucide-react';
import { useChatStore } from '../store/chatStore';
import { useAuthStore } from '../store/authStore';
import { cn } from '../lib/utils';

const Settings: React.FC = () => {
  const { settings, updateSettings } = useChatStore();
  const { user, logout } = useAuthStore();

  const models = [
    { id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash', desc: 'Fast and efficient for most tasks.' },
    { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro', desc: 'Powerful reasoning for complex queries.' },
    { id: 'gpt-4o', name: 'GPT-4o', desc: 'Omni model for high performance.' },
  ];

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-10">
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-white/50">Manage your AI model preferences and account details.</p>
      </div>

      <div className="space-y-8">
        {/* Model Settings */}
        <section className="glass-card p-8 bg-white/5 border-white/10">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center text-primary-light">
              <Cpu size={22} />
            </div>
            <div>
              <h2 className="text-xl font-bold">AI Configuration</h2>
              <p className="text-xs text-white/40">Adjust the behavior of the AI assistant.</p>
            </div>
          </div>

          <div className="space-y-8">
            <div className="space-y-4">
              <label className="text-sm font-semibold text-white/70">Model Selection</label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {models.map(model => (
                  <button
                    key={model.id}
                    onClick={() => updateSettings({ model: model.id })}
                    className={cn(
                      "p-4 rounded-2xl border text-left transition-all",
                      settings.model === model.id 
                        ? "bg-primary/20 border-primary text-white shadow-lg shadow-primary/10" 
                        : "bg-white/5 border-white/5 text-white/50 hover:bg-white/10"
                    )}
                  >
                    <p className="font-bold text-sm mb-1">{model.name}</p>
                    <p className="text-[10px] leading-tight">{model.desc}</p>
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-semibold text-white/70 flex items-center gap-2">
                    <Thermometer size={16} /> Temperature
                  </label>
                  <span className="text-primary-light font-mono text-sm">{settings.temperature}</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={settings.temperature}
                  onChange={(e) => updateSettings({ temperature: parseFloat(e.target.value) })}
                  className="w-full accent-primary bg-white/10 h-1.5 rounded-lg appearance-none cursor-pointer"
                />
                <p className="text-[10px] text-white/30">Higher values make output more creative, lower more deterministic.</p>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-semibold text-white/70 flex items-center gap-2">
                    <Database size={16} /> Retrieval Top-K
                  </label>
                  <span className="text-primary-light font-mono text-sm">{settings.top_k}</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="20"
                  step="1"
                  value={settings.top_k}
                  onChange={(e) => updateSettings({ top_k: parseInt(e.target.value) })}
                  className="w-full accent-primary bg-white/10 h-1.5 rounded-lg appearance-none cursor-pointer"
                />
                <p className="text-[10px] text-white/30">Number of document chunks to retrieve for context.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Profile Settings */}
        <section className="glass-card p-8 bg-white/5 border-white/10">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl bg-secondary/20 flex items-center justify-center text-secondary-light">
              <User size={22} />
            </div>
            <div>
              <h2 className="text-xl font-bold">Profile Settings</h2>
              <p className="text-xs text-white/40">Manage your personal information.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-white/60">Username</label>
              <input 
                type="text" 
                defaultValue={user?.username} 
                disabled
                className="w-full glass-input bg-white/5 border-white/5 opacity-50 cursor-not-allowed"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-white/60">Email Address</label>
              <input 
                type="email" 
                defaultValue={user?.email} 
                disabled
                className="w-full glass-input bg-white/5 border-white/5 opacity-50 cursor-not-allowed"
              />
            </div>
          </div>
        </section>

        {/* Danger Zone */}
        <section className="p-8 border border-red-500/20 rounded-[2rem] bg-red-500/5">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-red-400">Sign Out</h2>
              <p className="text-sm text-red-400/50">Disconnect your session from this device.</p>
            </div>
            <button 
              onClick={logout}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-all font-medium"
            >
              <LogOut size={18} /> Logout
            </button>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Settings;
