// src/components/BuyerDemandForm.tsx
import { useState } from 'react';
import axios from 'axios';

export default function BuyerDemandForm() {
  const [region, setRegion] = useState('Anuradhapura');
  const [varietyClass, setVarietyClass] = useState('Short-Grain');
  const [quantity, setQuantity] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!quantity || isNaN(Number(quantity))) {
      alert("Please enter a valid quantity in Metric Tons.");
      return;
    }

    setIsSubmitting(true);
    try {
      await axios.post('http://127.0.0.1:8000/api/demand', {
        season_id: 1, // Defaulting to current season
        buyer_id: 1,  // Hardcoded for MVP; will link to logged-in user later
        region: region,
        variety_class: varietyClass,
        quantity: parseFloat(quantity)
      });
      alert(`Successfully registered demand for ${quantity} MT of ${varietyClass} in ${region}.`);
      setQuantity(''); // Reset the form
    } catch (error) {
      console.error("Error submitting demand:", error);
      alert("Failed to submit demand. Is your backend running?");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white p-8 rounded-lg shadow-md border border-gray-200 mt-6 max-w-2xl">
      <h2 className="text-2xl font-bold text-purple-800 mb-6 border-b pb-2">Register Rice Demand</h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Region Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target Region</label>
            <select 
              value={region} 
              onChange={(e) => setRegion(e.target.value)}
              className="w-full border border-gray-300 rounded p-2 focus:ring-purple-500 focus:border-purple-500"
            >
              <option value="Anuradhapura">Anuradhapura</option>
              <option value="Polonnaruwa">Polonnaruwa</option>
              <option value="Ampara">Ampara</option>
              <option value="Kurunegala">Kurunegala</option>
            </select>
          </div>

          {/* Variety Class Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Rice Variety Class</label>
            <select 
              value={varietyClass} 
              onChange={(e) => setVarietyClass(e.target.value)}
              className="w-full border border-gray-300 rounded p-2 focus:ring-purple-500 focus:border-purple-500"
            >
              <option value="Short-Grain">Short-Grain (Samba, Nadu)</option>
              <option value="Long-Grain">Long-Grain (Basmati)</option>
              <option value="Traditional">Traditional (Heenati, Suwandel)</option>
            </select>
          </div>
        </div>

        {/* Quantity Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Required Quantity (Metric Tons)</label>
          <input 
            type="number" 
            min="0.1" 
            step="0.1"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            placeholder="e.g. 500"
            className="w-full border border-gray-300 rounded p-2 focus:ring-purple-500 focus:border-purple-500"
            required
          />
        </div>

        {/* Submit Button */}
        <button 
          type="submit" 
          disabled={isSubmitting}
          className={`w-full py-3 rounded font-bold text-white transition-colors ${
            isSubmitting ? 'bg-purple-400 cursor-not-allowed' : 'bg-purple-600 hover:bg-purple-700'
          }`}
        >
          {isSubmitting ? 'Registering...' : 'Submit Demand Requirements'}
        </button>
      </form>
    </div>
  );
}