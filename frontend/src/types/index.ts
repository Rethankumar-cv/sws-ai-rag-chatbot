export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface Conversation {
  id: string;
  title: string;
  updated_at: string;
  messages?: Message[];
}

export interface Document {
  id: string;
  filename: string;
  upload_date: string;
  status: 'processing' | 'ready' | 'error';
  size?: number;
}

export interface ChatSettings {
  model: string;
  temperature: number;
  top_k: number;
}
