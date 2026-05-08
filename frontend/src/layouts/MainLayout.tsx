import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  MessageSquare, 
  Upload, 
  Settings, 
  LogOut, 
  Plus, 
  Menu,
  ChevronLeft,
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuthStore } from '../store/authStore';
import { useChatStore } from '../store/chatStore';
import { cn } from '../lib/utils';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const { user, logout } = useAuthStore();
  const { conversations, createNewChat, setActiveConversation, activeConversation } = useChatStore();
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { icon: MessageSquare, label: 'Chat', path: '/dashboard' },
    { icon: Upload, label: 'Documents', path: '/upload' },
    { icon: Settings, label: 'Settings', path: '/settings' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-background text-white overflow-hidden">
      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: isSidebarOpen ? 280 : 80 }}
        className="glass-card m-3 flex flex-col border-r border-white/5 relative z-50"
      >
        <div className="p-4 flex items-center justify-between">
          {isSidebarOpen && (
            <motion.span 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-xl font-bold text-gradient"
            >
              SWS AI
            </motion.span>
          )}
          <button 
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            {isSidebarOpen ? <ChevronLeft size={20} /> : <Menu size={20} />}
          </button>
        </div>

        <div className="px-3 mb-4">
          <button
            onClick={() => {
              createNewChat();
              navigate('/dashboard');
            }}
            className={cn(
              "w-full flex items-center justify-center gap-2 btn-primary py-3",
              !isSidebarOpen && "px-0"
            )}
          >
            <Plus size={20} />
            {isSidebarOpen && <span>New Chat</span>}
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 space-y-2">
          {isSidebarOpen && (
            <div className="text-xs font-semibold text-white/40 uppercase tracking-wider mb-2 px-2">
              Menu
            </div>
          )}
          {menuItems.map((item) => (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={cn(
                "w-full flex items-center gap-3 p-3 rounded-xl transition-all",
                location.pathname === item.path 
                  ? "bg-primary/20 text-primary-light" 
                  : "hover:bg-white/5 text-white/70 hover:text-white"
              )}
            >
              <item.icon size={20} />
              {isSidebarOpen && <span>{item.label}</span>}
            </button>
          ))}

          {isSidebarOpen && conversations.length > 0 && (
            <>
              <div className="text-xs font-semibold text-white/40 uppercase tracking-wider mt-6 mb-2 px-2">
                Recent Chats
              </div>
              <div className="space-y-1">
                {conversations.map((chat) => (
                  <button
                    key={chat.id}
                    onClick={() => {
                      setActiveConversation(chat.id);
                      navigate('/dashboard');
                    }}
                    className={cn(
                      "w-full text-left p-2 rounded-lg text-sm transition-all truncate",
                      activeConversation?.id === chat.id 
                        ? "bg-white/10 text-white" 
                        : "text-white/50 hover:text-white hover:bg-white/5"
                    )}
                  >
                    {chat.title || 'Untitled Chat'}
                  </button>
                ))}
              </div>
            </>
          )}
        </nav>

        <div className="p-4 border-t border-white/5">
          <div className="flex items-center gap-3 p-2 rounded-xl bg-white/5">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-xs font-bold">
              {user?.username?.[0]?.toUpperCase() || 'U'}
            </div>
            {isSidebarOpen && (
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{user?.username}</p>
                <p className="text-xs text-white/40 truncate">{user?.email}</p>
              </div>
            )}
          </div>
          <button
            onClick={handleLogout}
            className={cn(
              "w-full flex items-center gap-3 p-3 mt-2 rounded-xl text-red-400 hover:bg-red-400/10 transition-all",
              !isSidebarOpen && "justify-center"
            )}
          >
            <LogOut size={20} />
            {isSidebarOpen && <span>Logout</span>}
          </button>
        </div>
      </motion.aside>

      {/* Main Content */}
      <main className="flex-1 relative flex flex-col overflow-hidden">
        {/* Animated Background Elements */}
        <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-primary/10 blur-[120px] rounded-full pointer-events-none" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-secondary/10 blur-[120px] rounded-full pointer-events-none" />
        
        <div className="flex-1 overflow-y-auto p-6 relative z-10">
          {children}
        </div>
      </main>
    </div>
  );
};

export default MainLayout;
