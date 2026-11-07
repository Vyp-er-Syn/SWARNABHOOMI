// src/components/SmartSchedule.tsx
import { format } from 'date-fns';

export default function SmartSchedule({ schedule }: { schedule: any }) {
  if (!schedule) return null;

  return (
    <div className="bg-gray-900 text-gray-100 p-6 rounded-lg shadow-md border border-gray-700 mt-6 animate-fade-in">
      <h3 className="text-2xl font-bold text-green-400 mb-6 border-b border-gray-700 pb-2">
        Your Smart Cultivation Schedule
      </h3>
      
      <div className="mb-6 bg-gray-800 p-4 rounded border border-gray-600">
        <p className="text-sm text-gray-400">Estimated Production (Intelligence Engine)</p>
        <p className="text-3xl font-mono text-white mt-1">
          {schedule.expected_yield_mt.toFixed(2)} <span className="text-lg text-green-400">Metric Tons</span>
        </p>
      </div>

      <div className="border-l-2 border-green-600 pl-6 ml-3 space-y-8 relative">
        {/* Planting Node */}
        <div className="relative">
          <div className="absolute w-4 h-4 bg-green-500 rounded-full -left-[1.95rem] top-1 shadow-[0_0_10px_#10b981]"></div>
          <h4 className="text-lg font-bold text-white">Planting Day</h4>
          <p className="text-gray-400">{format(new Date(schedule.planting_date), 'MMMM do, yyyy')}</p>
          <p className="text-sm text-gray-500 mt-1">Initial watering and field preparation.</p>
        </div>

        {/* Growth/Fertilizer Node (Simulated midpoint) */}
        <div className="relative">
          <div className="absolute w-4 h-4 bg-blue-500 rounded-full -left-[1.95rem] top-1 shadow-[0_0_10px_#3b82f6]"></div>
          <h4 className="text-lg font-bold text-white">Active Growth & Fertilizer</h4>
          <p className="text-gray-400">Ongoing phase</p>
          <p className="text-sm text-gray-500 mt-1">Nutrient application schedule will appear here once linked.</p>
        </div>

        {/* Harvest Node */}
        <div className="relative">
          <div className="absolute w-4 h-4 bg-yellow-500 rounded-full -left-[1.95rem] top-1 shadow-[0_0_10px_#eab308]"></div>
          <h4 className="text-lg font-bold text-white">Expected Harvest Window</h4>
          <p className="text-yellow-400 font-semibold">
            {format(new Date(schedule.harvest_start), 'MMM do')} - {format(new Date(schedule.harvest_end), 'MMM do, yyyy')}
          </p>
          <p className="text-sm text-gray-500 mt-1">Prepare labor and machinery for this period.</p>
        </div>
      </div>
    </div>
  );
}