import React from 'react';
import Sidebar from './Sidebar';

// Changed children to optional to fix strict type checking
export default function Layout({ children }: { children?: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 overflow-hidden font-sans">
      <Sidebar />
      <main className="flex-1 h-full overflow-hidden flex flex-col relative">
        {children}
      </main>
    </div>
  );
}