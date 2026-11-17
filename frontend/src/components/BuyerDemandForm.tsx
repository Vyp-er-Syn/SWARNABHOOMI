import { useState, useEffect } from 'react';
import axios from 'axios';

export default function BuyerDemandForm() {
  const [region, setRegion] = useState('Anuradhapura');
  const [varietyClass, setVarietyClass] = useState('Short-Grain (Nadu)');
  const [quantity, setQuantity] = useState<number>(100);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [demands, setDemands] = useState<any[]>([]);

  const fetchDemands = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/api/demand');
      setDemands(res.data || []);
    } catch (err) {
      console.error("Failed to fetch demands:", err);
    }
  };

  useEffect(() => {
    fetchDemands();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const payload = {
        season_id: 1,
        buyer_id: 1,
        region,
        variety_class: varietyClass,
        quantity: Number(quantity)
      };

      await axios.post('http://127.0.0.1:8000/api/demand', payload);
      alert(`Successfully registered demand for ${quantity} MT of ${varietyClass} in ${region}!`);
      setQuantity(100);
      fetchDemands();
    } catch (error) {
      console.error("Error submitting demand:", error);
      alert("Failed to submit demand. Is your backend running?");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-8 mt-6">
      <div className="bg-white p-8 rounded-lg shadow-md border border-gray-200 max-w-2xl">
        <h2 className="text-2xl font-bold text-purple-800 mb-6 border-b pb-2">Register Rice Demand</h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Target Region</label>
              <select
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-4 py-2 text-gray-900 focus:ring-purple-500 focus:border-purple-500"
              >
                <option value="Anuradhapura">Anuradhapura</option>
                <option value="Polonnaruwa">Polonnaruwa</option>
                <option value="Kurunegala">Kurunegala</option>
                <option value="Ampara">Ampara</option>
                <option value="Hambantota">Hambantota</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Rice Variety Class</label>
              <select
                value={varietyClass}
                onChange={(e) => setVarietyClass(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-4 py-2 text-gray-900 focus:ring-purple-500 focus:border-purple-500"
              >
                <option value="Short-Grain (Nadu)">Short-Grain (Nadu)</option>
                <option value="Long-Grain (Red/White)">Long-Grain (Red/White)</option>
                <option value="Samba">Samba</option>
                <option value="Traditional (Heenati, Suwandel)">Traditional (Heenati, Suwandel)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Required Quantity (Metric Tons)</label>
            <input
              type="number"
              min="1"
              step="0.5"
              value={quantity}
              onChange={(e) => setQuantity(parseFloat(e.target.value))}
              className="w-full border border-gray-300 rounded-md px-4 py-2 text-gray-900 focus:ring-purple-500 focus:border-purple-500 font-mono text-lg"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-md transition-colors shadow-sm"
          >
            {isSubmitting ? 'Registering...' : 'Submit Demand Requirements'}
          </button>
        </form>
      </div>

      {/* Live Registered Demands Table */}
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <h3 className="text-xl font-bold text-gray-800 mb-4 border-b pb-2">Published Buyer Demands</h3>
        {demands.length === 0 ? (
          <p className="text-gray-500 text-sm">No demand commitments published yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b bg-gray-50 text-gray-600 uppercase text-xs">
                  <th className="py-2.5 px-3">Order ID</th>
                  <th className="py-2.5 px-3">Region</th>
                  <th className="py-2.5 px-3">Variety Class</th>
                  <th className="py-2.5 px-3">Quantity (MT)</th>
                  <th className="py-2.5 px-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {demands.map((d) => (
                  <tr key={d.id} className="border-b hover:bg-gray-50">
                    <td className="py-2.5 px-3 font-mono text-gray-500">#{d.id}</td>
                    <td className="py-2.5 px-3 font-semibold text-gray-900">{d.region}</td>
                    <td className="py-2.5 px-3 text-purple-700 font-medium">{d.variety_class}</td>
                    <td className="py-2.5 px-3 font-mono font-bold">{d.quantity} MT</td>
                    <td className="py-2.5 px-3">
                      <span className="bg-purple-100 text-purple-800 px-2.5 py-0.5 rounded-full text-xs font-semibold">
                        {d.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}