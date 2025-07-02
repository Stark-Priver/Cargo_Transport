import React from 'react';
import { Truck } from 'lucide-react';

const LoadingScreen: React.FC = () => {
  return (
    <div className="h-screen w-full flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="flex items-center gap-3 mb-8">
        <Truck className="text-primary animate-bounce" size={40} />
        <h1 className="text-3xl font-bold text-primary">Safiri Mazao</h1>
      </div>
      
      <div className="w-40 h-1.5 bg-gray-200 rounded-full overflow-hidden dark:bg-gray-700">
        <div className="h-full bg-primary animate-[loadingBar_2s_ease-in-out_infinite]"></div>
      </div>
      
      <p className="mt-4 text-gray-600 dark:text-gray-300">Loading resources...</p>
      
      <style jsx>{`
        @keyframes loadingBar {
          0% { width: 0%; }
          50% { width: 100%; }
          100% { width: 0%; }
        }
      `}</style>
    </div>
  );
};

export default LoadingScreen;