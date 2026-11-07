import FieldMap from './components/FieldMap';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import BuyerDemandForm from './components/BuyerDemandForm';

// Placeholder components for the role-based portals
const Home = () => (
  <div className="flex flex-col items-center justify-center min-h-screen bg-green-50">
    <h1 className="text-5xl font-bold text-green-800 mb-4">SWARNABHOOMI</h1>
    <p className="text-xl text-gray-700 mb-8">Rice Production Intelligence Platform</p>
    <div className="flex gap-4">
      <Link to="/farmer" className="px-6 py-2 bg-green-600 text-white rounded shadow hover:bg-green-700 transition">Farmer Portal</Link>
      <Link to="/government" className="px-6 py-2 bg-blue-600 text-white rounded shadow hover:bg-blue-700 transition">Government Portal</Link>
      <Link to="/buyer" className="px-6 py-2 bg-purple-600 text-white rounded shadow hover:bg-purple-700 transition">Buyer Portal</Link>
    </div>
  </div>
);


  const FarmerPortal = () => (
  <div className="p-8 max-w-6xl mx-auto">
    <Link to="/" className="text-green-600 hover:underline mb-4 inline-block font-semibold">&larr; Back to Home</Link>
    <h1 className="text-4xl font-bold text-green-800 mb-2">Farmer Portal</h1>
    <p className="text-gray-600 mb-6 text-lg">Locate your field on the map below to register your cultivation boundaries.</p>
    
    <FieldMap />
  </div>
);


const GovernmentPortal = () => (
  <div className="p-8">
    <Link to="/" className="text-blue-600 hover:underline mb-4 inline-block">&larr; Back to Home</Link>
    <h1 className="text-3xl font-bold text-blue-800">Government Portal</h1>
    <p className="text-gray-600 mt-2">Supply and demand analytics dashboards will be built here.</p>
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

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/farmer" element={<FarmerPortal />} />
        <Route path="/government" element={<GovernmentPortal />} />
        <Route path="/buyer" element={<BuyerPortal />} />
      </Routes>
    </Router>
  );
}

export default App;

