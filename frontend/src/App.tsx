import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import FieldMap from './components/FieldMap';
import BuyerDemandForm from './components/BuyerDemandForm';
import GovernmentDashboard from './components/GovernmentDashboard';
import AgrarianDashboard from './components/AgrarianDashboard';
import Login from './components/Login';

// --- Protected Route Wrapper ---
const ProtectedRoute = ({ user, allowedRoles, children }: { user: any, allowedRoles: string[], children: JSX.Element }) => {
  if (!user) return <Navigate to="/" replace />;
  if (!allowedRoles.includes(user.role)) return <Navigate to="/unauthorized" replace />;
  return children;
};

// --- Top Navigation Bar ---
const NavBar = ({ user, onLogout }: { user: any, onLogout: () => void }) => {
  const navigate = useNavigate();
  if (!user) return null;

  const handleLogout = () => {
    onLogout();
    navigate('/');
  };

  return (
    <nav className="bg-gray-900 text-white px-6 py-4 flex justify-between items-center shadow-md">
      <div className="font-bold text-xl tracking-wider text-green-400">SWARNABHOOMI</div>
      <div className="flex items-center gap-4">
        <span className="text-sm text-gray-300">
          Logged in as <span className="font-semibold text-white">{user.username}</span> ({user.role})
        </span>
        <button 
          onClick={handleLogout}
          className="bg-red-600 hover:bg-red-700 px-4 py-1.5 rounded text-sm font-semibold transition-colors"
        >
          Logout
        </button>
      </div>
    </nav>
  );
};

export default function App() {
  const [user, setUser] = useState<any>(null);

  // Persist login state across browser refreshes
  useEffect(() => {
    const savedUser = localStorage.getItem('sb_user');
    if (savedUser) setUser(JSON.parse(savedUser));
  }, []);

  const handleLogin = (userData: any) => {
    setUser(userData);
    localStorage.setItem('sb_user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('sb_user');
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <NavBar user={user} onLogout={handleLogout} />
        
        <div className="p-4 md:p-8 max-w-7xl mx-auto">
          <Routes>
            <Route 
              path="/" 
              element={user ? <Navigate to={`/${user.role.toLowerCase()}`} replace /> : <Login onLogin={handleLogin} />} 
            />
            
            <Route 
              path="/farmer" 
              element={
                <ProtectedRoute user={user} allowedRoles={['Farmer']}>
                  <div>
                    <h1 className="text-3xl font-bold text-green-700 mb-2">Farmer Portal</h1>
                    <p className="text-gray-600 mb-6">Register your cultivation area and generate your fertilizer schedule.</p>
                    <FieldMap />
                  </div>
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/agrarian" 
              element={
                <ProtectedRoute user={user} allowedRoles={['Agrarian', 'Government']}>
                  <div>
                    <h1 className="text-3xl font-bold text-amber-800 mb-2">Agrarian Services Portal</h1>
                    <p className="text-gray-600 mb-6">Monitor active paddy cultivations and regional fertilizer allocation.</p>
                    <AgrarianDashboard />
                  </div>
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/buyer" 
              element={
                <ProtectedRoute user={user} allowedRoles={['Buyer']}>
                  <div>
                    <h1 className="text-4xl font-bold text-purple-800 mb-2">Buyer Portal</h1>
                    <p className="text-gray-600 mb-6 text-lg">Register your upcoming requirements for rice.</p>
                    <BuyerDemandForm />
                  </div>
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/government" 
              element={
                <ProtectedRoute user={user} allowedRoles={['Government']}>
                  <div>
                    <h1 className="text-4xl font-bold text-blue-800 mb-2">Government Intelligence Portal</h1>
                    <p className="text-gray-600 mb-6 text-lg">Real-time monitoring of agricultural supply chains.</p>
                    <GovernmentDashboard />
                  </div>
                </ProtectedRoute>
              } 
            />

            <Route path="/unauthorized" element={
              <div className="text-center mt-20">
                <h1 className="text-3xl font-bold text-red-600 mb-4">Access Denied</h1>
                <p className="text-gray-600">You do not have permission to view this portal.</p>
              </div>
            } />
          </Routes>
        </div>
      </div>
    </Router>
  );
}