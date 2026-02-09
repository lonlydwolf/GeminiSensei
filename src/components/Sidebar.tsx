import { useState, useEffect } from 'react';
import {
  Home,
  Map,
  MessageSquare,
  Settings,
  BookOpen,
  PanelLeftClose,
  PanelLeftOpen,
} from 'lucide-react';
import { useApp } from '../hooks/useApp';
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
      } relative z-50 flex h-screen flex-col border-r border-gray-200 bg-white transition-all duration-300 ease-in-out dark:border-gray-700 dark:bg-gray-800`}
    >
      {/* Header */}
      <div className='flex h-20 items-center justify-between overflow-hidden border-b border-gray-100 p-6 dark:border-gray-700'>
        <div
          className={`flex items-center gap-3 transition-all duration-300 ${isCollapsed ? 'w-full justify-center' : ''}`}
        >
          <div className='bg-primary shrink-0 rounded-2xl p-2 text-white shadow-lg shadow-blue-500/20'>
            <BookOpen size={24} />
          </div>
          <h1
            className={`origin-left bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-xl font-bold whitespace-nowrap text-transparent transition-all duration-200 ${
              isCollapsed ? 'hidden w-0 scale-90 opacity-0' : 'scale-100 opacity-100'
            }`}
          >
            GeminiSensei
          </h1>
        </div>
      </div>

      {/* Navigation */}
      <nav className='flex-1 space-y-2 overflow-x-hidden overflow-y-auto p-3'>
        {navItems.map((item) => {
          const isActive = currentRoute === item.route;
          return (
            <button
              key={item.route}
              onClick={() => setRoute(item.route)}
              title={isCollapsed ? item.label : ''}
              className={`flex w-full items-center ${
                isCollapsed ? 'justify-center px-0' : 'justify-start gap-3 px-4'
              } group relative rounded-2xl py-3 transition-all duration-200 ${
                isActive
                  ? 'bg-blue-50 font-medium text-blue-600 dark:bg-blue-900/20 dark:text-blue-400'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-700/50 dark:hover:text-gray-200'
              }`}
            >
              <item.icon
                size={24}
                className={`${isActive ? 'stroke-2' : 'stroke-1.5'} shrink-0 transition-transform duration-200 ${isCollapsed ? 'group-hover:scale-110' : ''}`}
              />

              <span
                className={`whitespace-nowrap transition-all duration-200 ${
                  isCollapsed ? 'hidden w-0 opacity-0' : 'opacity-100'
                }`}
              >
                {item.label}
              </span>
            </button>
          );
        })}
      </nav>

      {/* Footer Toggle */}
      <div className='border-t border-gray-100 p-4 dark:border-gray-700'>
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className={`flex w-full items-center ${
            isCollapsed ? 'justify-center' : 'justify-start gap-3 px-4'
          } rounded-xl py-2 text-gray-500 transition-all hover:bg-gray-100 hover:text-gray-900 dark:hover:bg-gray-700/50 dark:hover:text-gray-200`}
          title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {isCollapsed ? <PanelLeftOpen size={20} /> : <PanelLeftClose size={20} />}
          <span
            className={`whitespace-nowrap transition-all duration-200 ${
              isCollapsed ? 'hidden w-0 opacity-0' : 'opacity-100'
            }`}
          >
            Collapse
          </span>
        </button>

        {!isCollapsed && (
          <div className='mt-4 overflow-hidden text-center text-xs whitespace-nowrap text-gray-400 transition-opacity delay-100 duration-200 dark:text-gray-500'>
            v1.0.0 • React 19
          </div>
        )}
      </div>
    </div>
  );
}
