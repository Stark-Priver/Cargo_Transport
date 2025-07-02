import React from 'react';
import { useLocation } from 'react-router-dom';
import { Menu, Bell, Sun, Moon, Search } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import { useAuthStore } from '../../store/authStore';

interface HeaderProps {
  toggleSidebar: () => void;
}

const Header: React.FC<HeaderProps> = ({ toggleSidebar }) => {
  const { theme, toggleTheme } = useTheme();
  const { user } = useAuthStore();
  const location = useLocation();
  
  // Generate page title based on current route
  const getPageTitle = () => {
    const path = location.pathname;
    if (path === '/dashboard') return 'Dashboard';
    if (path === '/orders') return 'Transport Orders';
    if (path.startsWith('/orders/')) return 'Order Details';
    if (path === '/transporters') return 'Transporters';
    if (path === '/transporters/create') return 'Register New Transporter';
    if (path.startsWith('/transporters/')) return 'Transporter Details';
    if (path === '/reports') return 'Reports & Analytics';
    if (path === '/users') return 'User Management';
    if (path === '/settings') return 'Settings';
    if (path === '/profile') return 'Profile';
    return 'Safiri Mazao Admin';
  };
  
  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 dark:bg-gray-800 dark:border-gray-700">
      <div className="flex items-center gap-4">
        <button 
          onClick={toggleSidebar} 
          className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          <Menu size={20} className="text-gray-600 dark:text-gray-300" />
        </button>
        
        <h1 className="text-xl font-semibold text-gray-800 dark:text-white">
          {getPageTitle()}
        </h1>
      </div>
      
      <div className="hidden md:flex items-center gap-4 bg-gray-100 rounded-md px-3 py-1.5 dark:bg-gray-700">
        <Search size={18} className="text-gray-500 dark:text-gray-400" />
        <input 
          type="text"
          placeholder="Search..."
          className="bg-transparent border-none outline-none text-sm w-64 dark:text-white"
        />
      </div>
      
      <div className="flex items-center gap-4">
        <button 
          onClick={toggleTheme} 
          className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          {theme === 'light' ? (
            <Moon size={20} className="text-gray-600 dark:text-gray-300" />
          ) : (
            <Sun size={20} className="text-gray-600 dark:text-gray-300" />
          )}
        </button>
        
        <button className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 relative">
          <Bell size={20} className="text-gray-600 dark:text-gray-300" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-accent rounded-full"></span>
        </button>
        
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-white overflow-hidden">
            {user?.avatar ? (
              <img src={user.avatar} alt={user.name} className="h-full w-full object-cover" />
            ) : (
              <span>{user?.name?.charAt(0) || 'A'}</span>
            )}
          </div>
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300 hidden md:block">
            {user?.name || 'Admin User'}
          </span>
        </div>
      </div>
    </header>
  );
};

export default Header;