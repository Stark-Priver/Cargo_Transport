import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Truck, 
  Package, 
  Users, 
  Settings, 
  BarChart3,
  LogOut
} from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

interface NavItemProps {
  to: string;
  icon: React.ReactNode;
  label: string;
}

const NavItem: React.FC<NavItemProps> = ({ to, icon, label }) => (
  <NavLink 
    to={to} 
    className={({ isActive }) => `
      flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200
      ${isActive 
        ? 'bg-primary/10 text-primary font-medium' 
        : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700/30'
      }
    `}
  >
    {icon}
    <span>{label}</span>
  </NavLink>
);

const Sidebar: React.FC = () => {
  const { logout } = useAuthStore();
  
  return (
    <div className="h-full w-64 bg-white border-r border-gray-200 flex flex-col dark:bg-gray-800 dark:border-gray-700">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2">
          <Truck className="text-primary" size={24} />
          <h1 className="text-xl font-bold text-primary">Safiri Mazao</h1>
        </div>
        <p className="text-xs text-gray-500 mt-1 dark:text-gray-400">Transport Management</p>
      </div>
      
      <div className="flex-1 overflow-y-auto py-4 px-3">
        <nav className="space-y-1">
          <NavItem to="/dashboard" icon={<LayoutDashboard size={20} />} label="Dashboard" />
          <NavItem to="/orders" icon={<Package size={20} />} label="Orders" />
          <NavItem to="/transporters" icon={<Truck size={20} />} label="Transporters" />
          <NavItem to="/reports" icon={<BarChart3 size={20} />} label="Reports" />
          <NavItem to="/users" icon={<Users size={20} />} label="Users" />
          <NavItem to="/settings" icon={<Settings size={20} />} label="Settings" />
        </nav>
      </div>
      
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <button 
          onClick={() => logout()}
          className="flex w-full items-center gap-3 px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-all duration-200 dark:text-gray-300 dark:hover:bg-gray-700/30"
        >
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;