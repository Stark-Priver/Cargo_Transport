import React, { useState } from 'react';
import { Truck, Lock, User } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import Button from '../../components/common/Button';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const { login } = useAuthStore();
  
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    try {
      // Simulate API call for authentication
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Simple validation (in a real app, this would be handled by the server)
      if (email === 'admin@example.com' && password === 'password') {
        login('fake-jwt-token', {
          id: 'admin-1',
          name: 'Admin User',
          email: 'admin@example.com',
          role: 'admin',
        });
      } else {
        setError('Invalid email or password');
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4 dark:bg-gray-900">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-lg shadow-md overflow-hidden dark:bg-gray-800">
          <div className="bg-primary p-6 flex flex-col items-center">
            <Truck className="text-white mb-2" size={40} />
            <h1 className="text-2xl font-bold text-white">Safiri Mazao</h1>
            <p className="text-primary-light text-sm">Transport Management System</p>
          </div>
          
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">Admin Login</h2>
            
            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-200 text-red-600 rounded-md text-sm dark:bg-red-900/30 dark:border-red-800 dark:text-red-400">
                {error}
              </div>
            )}
            
            <form onSubmit={handleLogin}>
              <div className="space-y-4">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                    Email
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <User size={16} className="text-gray-400" />
                    </div>
                    <input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="admin@example.com"
                      className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      required
                    />
                  </div>
                </div>
                
                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                    Password
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Lock size={16} className="text-gray-400" />
                    </div>
                    <input
                      id="password"
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter your password"
                      className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      required
                    />
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <input
                      id="remember-me"
                      name="remember-me"
                      type="checkbox"
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded dark:border-gray-600"
                    />
                    <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                      Remember me
                    </label>
                  </div>
                  
                  <div className="text-sm">
                    <a href="#" className="text-primary hover:text-primary-dark">
                      Forgot password?
                    </a>
                  </div>
                </div>
                
                <Button
                  type="submit"
                  variant="primary"
                  loading={isLoading}
                  fullWidth
                >
                  {isLoading ? 'Logging in...' : 'Login to Dashboard'}
                </Button>
              </div>
            </form>
            
            <div className="mt-4 text-center text-sm text-gray-500 dark:text-gray-400">
              <p>For demo, use: admin@example.com / password</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;