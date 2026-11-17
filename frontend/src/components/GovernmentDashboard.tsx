import { useState, useEffect } from 'react';
import axios from 'axios';

export default function GovernmentDashboard() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchAnalytics = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/analytics/supply-demand');
      setAnalytics(response.data);
    } catch (error) {
      console.error("Failed to fetch analytics:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const exportToCSV = () => {
    if (!analytics?.regional_breakdown) return;
    const headers = ["District,Projected Supply (MT),Buyer Demand (MT),Net Balance (MT),Status"];
    const rows = analytics.regional_breakdown.map((r: any) =>
      `${r.region},${r.supply_mt},${r.demand_mt},${r.balance_mt},${r.status}`
    );
    const csvContent = "data:text/csv;charset=utf-8," + [headers, ...rows].join("\n");
    const link = document.createElement("a");
    link.setAttribute("href", encodeURI(csvContent));
    link.setAttribute("download", "swarnabhoomi_national_balance.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (isLoading) return <div className="text-blue-600 font-bold p-8">Loading National Analytics...</div>;
  if (!analytics) return <div className="text-red-500 p-8">Failed to load data. Ensure backend is running on port 8000.</div>;

  const isShortage = analytics.balance_mt < 0;
  const totalVolume = (analytics.total_supply_mt || 0) + (analytics.total_demand_mt || 0);
  const supplyRatio = totalVolume > 0 ? Math.round((analytics.total_supply_mt / totalVolume) * 100) : 50;

  return (
    <div className="space-y-6 mt-4">
      {/* Top KPI Cards */}
      <div className="bg-white p-8 rounded-lg shadow-md border border-gray-200">
        <div className="flex justify-between items-center mb-6 border-b pb-3">
          <div>
            <h2 className="text-2xl font-bold text-blue-900">National Rice Production & Security Balance</h2>
            <p className="text-sm text-gray-500">Live aggregation of farmer harvest forecasts vs. registered buyer demand</p>
          </div>
          <button
            onClick={fetchAnalytics}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm font-semibold transition-colors"
          >
            Refresh Telemetry
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-green-50 p-5 rounded border border-green-200 shadow-sm">
            <p className="text-xs text-green-700 font-semibold uppercase">Projected Supply</p>
            <p className="text-2xl font-mono font-bold text-green-900 mt-2">
              {analytics.total_supply_mt} <span className="text-sm font-normal">MT</span>
            </p>
          </div>

          <div className="bg-purple-50 p-5 rounded border border-purple-200 shadow-sm">
            <p className="text-xs text-purple-700 font-semibold uppercase">Registered Demand</p>
            <p className="text-2xl font-mono font-bold text-purple-900 mt-2">
              {analytics.total_demand_mt} <span className="text-sm font-normal">MT</span>
            </p>
          </div>

          <div className={`p-5 rounded border shadow-sm ${isShortage ? 'bg-red-50 border-red-200' : 'bg-blue-50 border-blue-200'}`}>
            <p className={`text-xs font-semibold uppercase ${isShortage ? 'text-red-700' : 'text-blue-700'}`}>
              Net Balance ({analytics.status})
            </p>
            <p className={`text-2xl font-mono font-bold mt-2 ${isShortage ? 'text-red-900' : 'text-blue-900'}`}>
              {analytics.balance_mt > 0 ? `+${analytics.balance_mt}` : analytics.balance_mt} <span className="text-sm font-normal">MT</span>
            </p>
          </div>

          <div className="bg-gray-50 p-5 rounded border border-gray-200 shadow-sm">
            <p className="text-xs text-gray-600 font-semibold uppercase">Active Cultivations</p>
            <p className="text-2xl font-mono font-bold text-gray-900 mt-2">
              {analytics.total_cultivations ?? 0} <span className="text-sm font-normal">Plots</span>
            </p>
          </div>

          <div className="bg-amber-50 p-5 rounded border border-amber-200 shadow-sm">
            <p className="text-xs text-amber-800 font-semibold uppercase">Mapped Paddy Area</p>
            <p className="text-2xl font-mono font-bold text-amber-900 mt-2">
              {analytics.total_fields_acres ?? 0} <span className="text-sm font-normal">Acres</span>
            </p>
          </div>
        </div>

        {/* Visual Supply vs Demand Ratio Bar */}
        <div className="mt-4">
          <div className="flex justify-between text-xs font-semibold uppercase text-gray-600 mb-1">
            <span>Supply Share ({supplyRatio}%)</span>
            <span>Demand Share ({100 - supplyRatio}%)</span>
          </div>
          <div className="w-full h-4 bg-purple-200 rounded-full overflow-hidden flex">
            <div
              className="bg-green-600 h-full transition-all duration-500"
              style={{ width: `${supplyRatio}%` }}
            />
          </div>
        </div>
      </div>

      {/* Regional Breakdown Table */}
      <div className="bg-white p-8 rounded-lg shadow-md border border-gray-200">
        <h3 className="text-xl font-bold text-gray-800 mb-4 border-b pb-2">District-Level Supply & Demand Breakdown</h3>
        {(!analytics.regional_breakdown || analytics.regional_breakdown.length === 0) ? (
          <p className="text-gray-500 text-sm">No regional supply or demand records registered yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b bg-gray-50 text-gray-600 uppercase text-xs">
                  <th className="py-3 px-4">District / Region</th>
                  <th className="py-3 px-4">Projected Supply (MT)</th>
                  <th className="py-3 px-4">Buyer Demand (MT)</th>
                  <th className="py-3 px-4">Net Balance (MT)</th>
                  <th className="py-3 px-4">Security Status</th>
                </tr>
              </thead>
              <tbody>
                {analytics.regional_breakdown.map((row: any) => {
                  const neg = row.balance_mt < 0;
                  return (
                    <tr key={row.region} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4 font-semibold text-gray-900">{row.region}</td>
                      <td className="py-3 px-4 font-mono text-green-700">{row.supply_mt} MT</td>
                      <td className="py-3 px-4 font-mono text-purple-700">{row.demand_mt} MT</td>
                      <td className={`py-3 px-4 font-mono font-bold ${neg ? 'text-red-600' : 'text-blue-700'}`}>
                        {row.balance_mt > 0 ? `+${row.balance_mt}` : row.balance_mt} MT
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                          neg ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                        }`}>
                          {row.status}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
      <div className="flex gap-3">
            <button
              onClick={exportToCSV}
              className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded text-sm font-semibold transition-colors"
            >
              Export CSV Report
            </button>
          
          </div>
    </div>
  );
}