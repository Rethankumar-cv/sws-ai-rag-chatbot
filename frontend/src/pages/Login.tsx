import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { motion } from 'framer-motion';
import { Mail, Lock, Loader2, Globe, AlertCircle } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import api from '../services/api';
import { cn } from '../lib/utils';

const loginSchema = z.object({
  username: z.string().min(3, 'Username must be at least 3 characters'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

type LoginForm = z.infer<typeof loginSchema>;

const Login: React.FC = () => {
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuthStore();
  const navigate = useNavigate();

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('username', data.username);
      formData.append('password', data.password);
      
      const response = await api.post('/auth/login', formData);
      login(response.data.access_token, response.data.user);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-6 relative overflow-hidden">
      {/* Background Orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 blur-[150px] rounded-full" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/20 blur-[150px] rounded-full" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md z-10"
      >
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">Welcome Back</h1>
          <p className="text-white/50">Log in to your SWS AI account</p>
        </div>

        <div className="glass-card p-8 bg-white/5 border-white/10 shadow-2xl">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {error && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-3 rounded-xl flex items-center gap-3 text-sm">
                <AlertCircle size={18} />
                {error}
              </div>
            )}

            <div className="space-y-2">
              <label className="text-sm font-medium text-white/70 ml-1">Username</label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-white/30" size={18} />
                <input
                  {...register('username')}
                  type="text"
                  placeholder="rethan_cv"
                  className={cn(
                    "w-full glass-input pl-12 bg-white/5 border-white/10 h-12",
                    errors.username && "border-red-500/50"
                  )}
                />
              </div>
              {errors.username && <p className="text-xs text-red-400 ml-1">{errors.username.message}</p>}
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between ml-1">
                <label className="text-sm font-medium text-white/70">Password</label>
                <Link to="/forgot-password" className="text-xs text-primary-light hover:underline">Forgot password?</Link>
              </div>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-white/30" size={18} />
                <input
                  {...register('password')}
                  type="password"
                  placeholder="••••••••"
                  className={cn(
                    "w-full glass-input pl-12 bg-white/5 border-white/10 h-12",
                    errors.password && "border-red-500/50"
                  )}
                />
              </div>
              {errors.password && <p className="text-xs text-red-400 ml-1">{errors.password.message}</p>}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-primary h-12 flex items-center justify-center gap-2"
            >
              {isLoading ? <Loader2 className="animate-spin" /> : 'Log In'}
            </button>
          </form>

          <div className="relative my-8 text-center">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-white/10"></div></div>
            <span className="relative px-4 bg-[#0d0d10] text-xs text-white/30 uppercase">Or continue with</span>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <button className="flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl py-2 transition-all">
              <Globe size={20} />
              <span className="text-sm font-medium">GitHub</span>
            </button>
            <button className="flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl py-2 transition-all">
              <svg className="w-5 h-5" viewBox="0 0 24 24"><path fill="currentColor" d="M12.48 10.92v3.28h7.84c-.24 1.84-.9 3.34-2.16 4.6-1.52 1.52-3.23 2.42-6.58 2.42-6.64 0-12.03-5.39-12.03-12.03S7.36 3.6 14 3.6c3.98 0 6.64 1.56 8.52 3.32l2.34-2.34C22.28 2.14 18.66 0 14 0 6.48 0 0 6.48 0 14s6.48 14 14 14c4.05 0 7.31-1.34 9.8-3.95 2.5-2.5 3.31-6.13 3.31-9.08 0-.9-.08-1.77-.21-2.58h-11.42z"/></svg>
              <span className="text-sm font-medium">Google</span>
            </button>
          </div>
        </div>

        <p className="text-center mt-8 text-sm text-white/50">
          Don't have an account?{' '}
          <Link to="/signup" className="text-primary-light font-semibold hover:underline">Sign up for free</Link>
        </p>
      </motion.div>
    </div>
  );
};

export default Login;
