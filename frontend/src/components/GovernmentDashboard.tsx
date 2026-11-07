import { useState, useEffect } from 'react';
import axios from 'axios';

export default function GovernmentDashboard() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchAnalytics = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/api/analytics/supply-demand');
      setAnalytics(response.data);
    } catch (error) {
      console.error("Failed to fetch analytics:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (isLoading) return <div className="text-blue-600 font-bold p-8">Loading National Analytics...</div>;
  if (!analytics) return <div className="text-red-500 p-8">Failed to load data. Ensure backend is running on port 8000.</div>;

  const isShortage = analytics.balance_mt < 0;

  return (
    <div className="bg-white p-8 rounded-lg shadow-md border border-gray-200 mt-6 max-w-4xl">
      <div className="flex justify-between items-center mb-6 border-b pb-2">
        <h2 className="text-2xl font-bold text-blue-800">National Rice Production Balance</h2>
        <button
          onClick={fetchAnalytics}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-1.5 rounded text-sm font-semibold"
        >
          Refresh Data
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-4">
        <div className="bg-green-50 p-6 rounded border border-green-200 shadow-sm">
          <p className="text-sm text-green-700 font-semibold uppercase">Projected Supply</p>
          <p className="text-3xl font-mono text-green-900 mt-2">
            {analytics.total_supply_mt} <span className="text-lg">MT</span>
          </p>
        </div>

        <div className="bg-purple-50 p-6 rounded border border-purple-200 shadow-sm">
          <p className="text-sm text-purple-700 font-semibold uppercase">Registered Demand</p>
          <p className="text-3xl font-mono text-purple-900 mt-2">
            {analytics.total_demand_mt} <span className="text-lg">MT</span>
          </p>
        </div>

        <div className={`p-6 rounded border shadow-sm ${isShortage ? 'bg-red-50 border-red-200' : 'bg-blue-50 border-blue-200'}`}>
          <p className={`text-sm font-semibold uppercase ${isShortage ? 'text-red-700' : 'text-blue-700'}`}>
            Net Balance ({analytics.status})
          </p>
          <p className={`text-3xl font-mono mt-2 ${isShortage ? 'text-red-900' : 'text-blue-900'}`}>
            {analytics.balance_mt} <span className="text-lg">MT</span>
          </p>
        </div>
      </div>
    </div>
  );
}