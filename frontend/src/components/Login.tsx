import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface LoginProps {
  onLogin: (user: any) => void;
}

export default function Login({ onLogin }: LoginProps) {
  const [username, setUsername] = useState('default_farmer');
  const [password, setPassword] = useState('hashed_pw_123');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const res = await axios.post('http://127.0.0.1:8000/api/auth/login', {
        username,
        password
      });

      const userData = res.data;
      onLogin(userData);

      if (userData.role === 'Farmer') navigate('/farmer');
      else if (userData.role === 'Agrarian') navigate('/agrarian');
      else if (userData.role === 'Buyer') navigate('/buyer');
      else if (userData.role === 'Government') navigate('/government');
      else navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to connect to backend server.");
    } finally {
      setIsLoading(false);
    }
  };

  const selectDemoRole = (demoUsername: string) => {
    setUsername(demoUsername);
    setPassword('hashed_pw_123');
    setError('');
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg border border-gray-200 w-full max-w-md">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-green-700">SWARNABHOOMI</h1>
          <p className="text-gray-500 mt-1 text-sm">Rice Production Intelligence & Supply Chain Platform</p>
        </div>

        {/* Quick Demo Role Selector */}
        <div className="mb-6">
          <p className="text-xs font-semibold uppercase text-gray-400 mb-2 text-center">Quick Select Demo Account</p>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => selectDemoRole('default_farmer')}
              className={`text-xs py-2 px-3 rounded border font-semibold transition ${
                username === 'default_farmer' ? 'bg-green-600 text-white border-green-600' : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
              }`}
            >
              Farmer Portal
            </button>
            <button
              type="button"
              onClick={() => selectDemoRole('default_agrarian')}
              className={`text-xs py-2 px-3 rounded border font-semibold transition ${
                username === 'default_agrarian' ? 'bg-amber-600 text-white border-amber-600' : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
              }`}
            >
              Agrarian Officer
            </button>
            <button
              type="button"
              onClick={() => selectDemoRole('default_buyer')}
              className={`text-xs py-2 px-3 rounded border font-semibold transition ${
                username === 'default_buyer' ? 'bg-purple-600 text-white border-purple-600' : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
              }`}
            >
              Buyer Portal
            </button>
            <button
              type="button"
              onClick={() => selectDemoRole('default_gov')}
              className={`text-xs py-2 px-3 rounded border font-semibold transition ${
                username === 'default_gov' ? 'bg-blue-600 text-white border-blue-600' : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
              }`}
            >
              Government Portal
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 text-red-700 p-3 rounded mb-4 text-sm border border-red-200">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-5">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full border border-gray-300 rounded px-4 py-2 text-gray-900 focus:ring-green-500 focus:border-green-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-300 rounded px-4 py-2 text-gray-900 focus:ring-green-500 focus:border-green-500"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2.5 px-4 rounded transition-colors"
          >
            {isLoading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}