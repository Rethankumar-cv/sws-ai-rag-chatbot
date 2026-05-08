import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, File, X, CheckCircle, Loader2, Trash2, Database } from 'lucide-react';
import api from '../services/api';
import type { Document } from '../types';

const DocumentUpload: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isFetching, setIsFetching] = useState(true);

  const fetchDocuments = async () => {
    try {
      const response = await api.get('/documents');
      setDocuments(response.data);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    } finally {
      setIsFetching(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedFiles = Array.from(e.dataTransfer.files);
    setFiles(prev => [...prev, ...droppedFiles]);
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    setIsUploading(true);
    
    try {
      for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
        await api.post('/documents/upload', formData);
      }
      setFiles([]);
      fetchDocuments();
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const deleteDocument = async (id: string) => {
    try {
      await api.delete(`/documents/${id}`);
      setDocuments(prev => prev.filter(doc => doc.id !== id));
    } catch (error) {
      console.error('Delete failed:', error);
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-10">
        <h1 className="text-3xl font-bold mb-2">Knowledge Base</h1>
        <p className="text-white/50">Upload and manage documents for your RAG pipeline.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Upload Zone */}
        <div className="lg:col-span-2 space-y-6">
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={onDrop}
            className="border-2 border-dashed border-white/10 rounded-[2rem] p-12 text-center hover:border-primary/50 hover:bg-primary/5 transition-all cursor-pointer group"
          >
            <div className="w-16 h-16 rounded-3xl bg-white/5 flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
              <Upload className="text-primary-light" size={32} />
            </div>
            <h3 className="text-xl font-semibold mb-2">Click or drag files to upload</h3>
            <p className="text-white/40 text-sm mb-6">PDF, DOCX, TXT (Max 10MB per file)</p>
            <input 
              type="file" 
              multiple 
              className="hidden" 
              id="file-upload" 
              onChange={(e) => setFiles(prev => [...prev, ...Array.from(e.target.files || [])])}
            />
            <label htmlFor="file-upload" className="btn-secondary cursor-pointer">
              Select Files
            </label>
          </div>

          <AnimatePresence>
            {files.length > 0 && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="glass-card p-6 bg-white/5 border-white/10"
              >
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-semibold">{files.length} Files Selected</h4>
                  <button 
                    onClick={handleUpload}
                    disabled={isUploading}
                    className="btn-primary py-2 px-6 flex items-center gap-2"
                  >
                    {isUploading ? <Loader2 className="animate-spin" size={18} /> : <Upload size={18} />}
                    {isUploading ? 'Uploading...' : 'Upload All'}
                  </button>
                </div>
                <div className="space-y-3">
                  {files.map((file, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5">
                      <div className="flex items-center gap-3">
                        <File className="text-primary-light" size={20} />
                        <div className="text-sm">
                          <p className="font-medium truncate max-w-[200px]">{file.name}</p>
                          <p className="text-[10px] text-white/40">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                        </div>
                      </div>
                      <button onClick={() => removeFile(idx)} className="text-white/30 hover:text-red-400 p-1">
                        <X size={18} />
                      </button>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Status & Stats */}
        <div className="space-y-6">
          <div className="glass-card p-6 bg-primary/5 border-primary/10">
            <h4 className="text-sm font-semibold text-primary-light uppercase tracking-wider mb-4">Pipeline Status</h4>
            <div className="flex items-center gap-4 p-4 rounded-2xl bg-white/5 border border-white/5">
              <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center text-green-500">
                <CheckCircle size={20} />
              </div>
              <div>
                <p className="text-sm font-bold">Vector Store Sync</p>
                <p className="text-xs text-white/50">Fully synchronized</p>
              </div>
            </div>
          </div>

          <div className="glass-card p-6 bg-white/5 border-white/10">
            <h4 className="text-sm font-semibold text-white/40 uppercase tracking-wider mb-4">Library</h4>
            <div className="space-y-4">
              {isFetching ? (
                <div className="flex justify-center py-10">
                  <Loader2 className="animate-spin text-white/20" size={32} />
                </div>
              ) : documents.length === 0 ? (
                <div className="text-center py-10 opacity-30">
                  <Database size={40} className="mx-auto mb-2" />
                  <p className="text-sm">No documents found</p>
                </div>
              ) : (
                documents.map(doc => (
                  <div key={doc.id} className="flex items-center justify-between group">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center">
                        <File size={16} className="text-white/60" />
                      </div>
                      <div>
                        <p className="text-sm font-medium truncate max-w-[150px]">{doc.filename}</p>
                        <p className="text-[10px] text-white/30">{new Date(doc.upload_date).toLocaleDateString()}</p>
                      </div>
                    </div>
                    <button 
                      onClick={() => deleteDocument(doc.id)}
                      className="opacity-0 group-hover:opacity-100 p-2 hover:bg-red-400/10 text-red-400/60 hover:text-red-400 rounded-lg transition-all"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentUpload;
