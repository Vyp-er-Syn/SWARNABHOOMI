import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import FieldMap from './components/FieldMap';
import BuyerDemandForm from './components/BuyerDemandForm';
import GovernmentDashboard from './components/GovernmentDashboard';

const Home = () => (
  <div className="p-8">
    <h1 className="text-4xl font-bold text-green-700 mb-4">SWARNABHOOMI</h1>
    <p className="text-xl text-gray-300 mb-8">Rice Production Intelligence & Demand Coordination Platform</p>
    <div className="flex gap-4">
      <Link to="/farmer" className="bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700">Farmer Portal</Link>
      <Link to="/buyer" className="bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700">Buyer Portal</Link>
      <Link to="/government" className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700">Government Portal</Link>
    </div>
  </div>
);

const FarmerPortal = () => (
  <div className="p-8 max-w-6xl mx-auto">
    <Link to="/" className="text-green-500 hover:underline mb-4 inline-block font-semibold">&larr; Back to Home</Link>
    <h1 className="text-3xl font-bold text-green-700 mb-2">Farmer Portal</h1>
    <p className="text-gray-400 mb-6">Draw your field boundaries on the satellite map below to register your cultivation area.</p>
    <FieldMap />
  </div>
);

const BuyerPortal = () => (
  <div className="p-8 max-w-6xl mx-auto">
    <Link to="/" className="text-purple-600 hover:underline mb-4 inline-block font-semibold">&larr; Back to Home</Link>
    <h1 className="text-4xl font-bold text-purple-800 mb-2">Buyer Portal</h1>
    <p className="text-gray-600 mb-6 text-lg">Register your upcoming requirements for rice to help the government coordinate supply.</p>
    <BuyerDemandForm />
  </div>
);

const GovernmentPortal = () => (
  <div className="p-8 max-w-6xl mx-auto">
    <Link to="/" className="text-blue-600 hover:underline mb-4 inline-block font-semibold">&larr; Back to Home</Link>
    <h1 className="text-4xl font-bold text-blue-800 mb-2">Government Intelligence Portal</h1>
    <p className="text-gray-600 mb-6 text-lg">Real-time monitoring of agricultural supply chains and food security.</p>
    <GovernmentDashboard />
  </div>
);

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/farmer" element={<FarmerPortal />} />
          <Route path="/buyer" element={<BuyerPortal />} />
          <Route path="/government" element={<GovernmentPortal />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;