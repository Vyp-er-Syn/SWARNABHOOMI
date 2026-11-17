import { useState, useEffect } from 'react';
import axios from 'axios';

export default function AgrarianDashboard() {
  const [data, setData] = useState<any>(null);
  const [plans, setPlans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchOverview = async () => {
    setLoading(true);
    try {
      const [overviewRes, plansRes] = await Promise.all([
        axios.get('http://127.0.0.1:8000/api/agrarian/overview'),
        axios.get('http://127.0.0.1:8000/api/agrarian/resource-plans')
      ]);
      setData(overviewRes.data);
      setPlans(plansRes.data || []);
    } catch (err) {
      console.error("Failed to fetch agrarian overview:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
  }, []);

  const updatePlanStatus = async (planId: number, newStatus: string) => {
    try {
      await axios.patch(`http://127.0.0.1:8000/api/resources/plans/${planId}/status`, { status: newStatus });
      fetchOverview();
    } catch (err) {
      console.error("Failed to update status:", err);
    }
  };

  if (loading) return <div className="p-8 text-amber-700 font-bold">Loading Agrarian Service Data...</div>;
  if (!data) return <div className="p-8 text-red-500">Failed to load Agrarian Officer data.</div>;

  return (
    <div className="space-y-8 mt-4">
      {/* Fertilizer Allocation Summary */}
      <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
        <div className="flex justify-between items-center mb-4 border-b pb-2">
          <h2 className="text-xl font-bold text-amber-800">Regional Fertilizer & Input Requirements</h2>
          <button
            onClick={fetchOverview}
            className="bg-amber-600 hover:bg-amber-700 text-white px-4 py-1.5 rounded text-sm font-semibold"
          >
            Refresh
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {data.fertilizer_summary.length === 0 ? (
            <p className="text-gray-500 text-sm">No active resource plans generated yet.</p>
          ) : (
            data.fertilizer_summary.map((item: any) => (
              <div key={item.input_name} className="bg-amber-50 p-4 rounded border border-amber-200">
                <p className="text-xs font-semibold uppercase text-amber-800">{item.input_name}</p>
                <p className="text-2xl font-mono text-amber-900 mt-1">{item.total_kg} kg</p>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Active Cultivations Table */}
      <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
        <h2 className="text-xl font-bold text-gray-800 mb-4 border-b pb-2">Registered Farmer Cultivations</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b bg-gray-50 text-gray-600">
                <th className="py-2.5 px-3">ID</th>
                <th className="py-2.5 px-3">Field Name</th>
                <th className="py-2.5 px-3">Area (Acres)</th>
                <th className="py-2.5 px-3">Rice Variety</th>
                <th className="py-2.5 px-3">Planting Date</th>
                <th className="py-2.5 px-3">Expected Harvest</th>
                <th className="py-2.5 px-3">Projected Yield (MT)</th>
              </tr>
            </thead>
            <tbody>
              {data.cultivations.map((c: any) => (
                <tr key={c.cultivation_id} className="border-b hover:bg-gray-50">
                  <td className="py-2.5 px-3 font-mono text-gray-600">#{c.cultivation_id}</td>
                  <td className="py-2.5 px-3 font-semibold text-gray-900">{c.field_name}</td>
                  <td className="py-2.5 px-3 font-mono">{c.area_acres}</td>
                  <td className="py-2.5 px-3 text-green-700 font-medium">{c.variety_name}</td>
                  <td className="py-2.5 px-3 font-mono">{c.planting_date}</td>
                  <td className="py-2.5 px-3 font-mono text-amber-700">{c.expected_harvest}</td>
                  <td className="py-2.5 px-3 font-mono font-bold text-blue-800">{c.expected_yield_mt} MT</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Fertilizer Dispatch Queue */}
      <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
        <h2 className="text-xl font-bold text-gray-800 mb-4 border-b pb-2">Fertilizer & Input Dispatch Schedule</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b bg-gray-50 text-gray-600">
                <th className="py-2.5 px-3">Field</th>
                <th className="py-2.5 px-3">Stage</th>
                <th className="py-2.5 px-3">Input</th>
                <th className="py-2.5 px-3">Quantity</th>
                <th className="py-2.5 px-3">Due Date</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3">Action</th>
              </tr>
            </thead>
            <tbody>
              {plans.map((p) => (
                <tr key={p.id} className="border-b hover:bg-gray-50">
                  <td className="py-2.5 px-3 font-semibold text-gray-900">{p.field_name}</td>
                  <td className="py-2.5 px-3 text-gray-700">{p.task_type}</td>
                  <td className="py-2.5 px-3 font-medium text-amber-800">{p.recommended_input}</td>
                  <td className="py-2.5 px-3 font-mono">{p.quantity} {p.unit}</td>
                  <td className="py-2.5 px-3 font-mono">{p.due_date}</td>
                  <td className="py-2.5 px-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                      p.status === 'Dispatched' ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'
                    }`}>
                      {p.status}
                    </span>
                  </td>
                  <td className="py-2.5 px-3">
                    {p.status !== 'Dispatched' ? (
                      <button
                        onClick={() => updatePlanStatus(p.id, 'Dispatched')}
                        className="bg-green-600 hover:bg-green-700 text-white text-xs px-3 py-1 rounded font-semibold"
                      >
                        Mark Dispatched
                      </button>
                    ) : (
                      <span className="text-xs text-gray-400">Completed</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}