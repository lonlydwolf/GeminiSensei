import React, { useState, useEffect } from 'react';
import { Home, Map, MessageSquare, Settings, BookOpen, PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { AppRoute } from '../types';

export default function Sidebar() {
  const { currentRoute, setRoute } = useApp();
  
  // Initialize state from localStorage
  const [isCollapsed, setIsCollapsed] = useState(() => {
    const saved = localStorage.getItem('edu_sidebar_collapsed');
    return saved === 'true';
  });

  useEffect(() => {
    localStorage.setItem('edu_sidebar_collapsed', String(isCollapsed));
  }, [isCollapsed]);

  const navItems = [
    { label: 'Home', route: AppRoute.HOME, icon: Home },
    { label: 'Roadmap', route: AppRoute.ROADMAP, icon: Map },
    { label: 'Chat', route: AppRoute.CHAT, icon: MessageSquare },
    { label: 'Settings', route: AppRoute.SETTINGS, icon: Settings },
  ];

  return (
    <div 
      className={`${
        isCollapsed ? 'w-20' : 'w-64'
      } bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 h-screen flex flex-col transition-all duration-300 ease-in-out relative z-50`}
    >
      {/* Header */}
      <div className="p-6 flex items-center justify-between border-b border-gray-100 dark:border-gray-700 h-20 overflow-hidden">
        <div className={`flex items-center gap-3 transition-all duration-300 ${isCollapsed ? 'w-full justify-center' : ''}`}>
          <div className="bg-primary text-white p-2 rounded-2xl shrink-0 shadow-lg shadow-blue-500/20">
            <BookOpen size={24} />
          </div>
          <h1 
            className={`text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-purple-600 whitespace-nowrap transition-all duration-200 origin-left ${
              isCollapsed ? 'opacity-0 w-0 hidden scale-90' : 'opacity-100 scale-100'
            }`}
          >
            EduMind
          </h1>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-2 overflow-y-auto overflow-x-hidden">
        {navItems.map((item) => {
          const isActive = currentRoute === item.route;
          return (
            <button
              key={item.route}
              onClick={() => setRoute(item.route)}
              title={isCollapsed ? item.label : ''}
              className={`w-full flex items-center ${
                isCollapsed ? 'justify-center px-0' : 'justify-start px-4 gap-3'
              } py-3 rounded-2xl transition-all duration-200 group relative ${
                isActive
                  ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 font-medium'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700/50 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              <item.icon 
                size={24} 
                className={`${isActive ? 'stroke-2' : 'stroke-1.5'} shrink-0 transition-transform duration-200 ${isCollapsed ? 'group-hover:scale-110' : ''}`} 
              />
              
              <span 
                className={`whitespace-nowrap transition-all duration-200 ${
                  isCollapsed ? 'opacity-0 w-0 hidden' : 'opacity-100'
                }`}
              >
                {item.label}
              </span>
            </button>
          );
        })}
      </nav>

      {/* Footer Toggle */}
      <div className="p-4 border-t border-gray-100 dark:border-gray-700">
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className={`w-full flex items-center ${
            isCollapsed ? 'justify-center' : 'justify-start gap-3 px-4'
          } py-2 rounded-xl text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700/50 hover:text-gray-900 dark:hover:text-gray-200 transition-all`}
          title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
        >
          {isCollapsed ? <PanelLeftOpen size={20} /> : <PanelLeftClose size={20} />}
          <span 
            className={`whitespace-nowrap transition-all duration-200 ${
              isCollapsed ? 'opacity-0 w-0 hidden' : 'opacity-100'
            }`}
          >
            Collapse
          </span>
        </button>

        {!isCollapsed && (
          <div className="mt-4 text-xs text-gray-400 dark:text-gray-500 text-center transition-opacity duration-200 delay-100 overflow-hidden whitespace-nowrap">
            v1.0.0 • React 19
          </div>
        )}
      </div>
    </div>
  );
}