import { X } from 'lucide-react';
import type { ReactNode } from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
}

export const Modal = ({ isOpen, onClose, title, children }: ModalProps) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm transition-opacity">
      <div 
        className="bg-[#F7F5F0] rounded-xl shadow-2xl w-full max-w-2xl overflow-hidden border border-stone-200 animate-in fade-in zoom-in-95 duration-200"
        role="dialog"
        aria-modal="true"
      >
        <div className="px-6 py-4 border-b border-stone-200 flex justify-between items-center bg-[#EBE7DF]">
          <h2 className="text-xl font-serif text-stone-900">{title}</h2>
          <button 
            onClick={onClose}
            className="text-stone-500 hover:text-stone-900 hover:bg-stone-200 p-1 rounded-full transition-colors"
          >
            <X size={20} />
          </button>
        </div>
        
        <div className="p-6 max-h-[80vh] overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  );
};
