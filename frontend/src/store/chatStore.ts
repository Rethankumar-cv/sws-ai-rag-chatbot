import { create } from 'zustand';
import type { Message, Conversation, ChatSettings } from '../types';
import api from '../services/api';

interface ChatState {
  conversations: Conversation[];
  activeConversation: Conversation | null;
  messages: Message[];
  isTyping: boolean;
  settings: ChatSettings;
  fetchConversations: () => Promise<void>;
  setActiveConversation: (id: string) => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  createNewChat: () => void;
  updateSettings: (settings: Partial<ChatSettings>) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  activeConversation: null,
  messages: [],
  isTyping: false,
  settings: {
    model: 'gemini-1.5-flash',
    temperature: 0.7,
    top_k: 40,
  },
  fetchConversations: async () => {
    try {
      const response = await api.get('/chat/history');
      set({ conversations: response.data });
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    }
  },
  setActiveConversation: async (id) => {
    try {
      const response = await api.get(`/chat/${id}`);
      set({ activeConversation: response.data, messages: response.data.messages || [] });
    } catch (error) {
      console.error('Failed to fetch conversation details:', error);
    }
  },
  sendMessage: async (content) => {
    const { activeConversation, messages, settings } = get();
    
    // Optimistic UI update
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };

    set({ messages: [...messages, userMessage], isTyping: true });

    try {
      const response = await api.post('/chat', {
        conversation_id: activeConversation?.id,
        message: content,
        ...settings
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString(),
      };

      set({ 
        messages: [...get().messages, assistantMessage], 
        isTyping: false,
        activeConversation: response.data.conversation_id ? { ...activeConversation!, id: response.data.conversation_id } : activeConversation
      });
      
      // Refresh history if it's a new conversation
      if (!activeConversation) {
        get().fetchConversations();
      }
    } catch (error) {
      set({ isTyping: false });
      console.error('Failed to send message:', error);
    }
  },
  createNewChat: () => {
    set({ activeConversation: null, messages: [] });
  },
  updateSettings: (newSettings) => {
    set({ settings: { ...get().settings, ...newSettings } });
  },
}));
