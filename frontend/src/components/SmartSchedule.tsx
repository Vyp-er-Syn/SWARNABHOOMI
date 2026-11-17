interface ResourcePlanItem {
  id: number;
  task_type: string;
  recommended_input: string;
  due_date: string;
  quantity: number;
  unit: string;
  status: string;
}

interface ScheduleProps {
  schedule: {
    variety_name?: string;
    maturity_days?: number;
    planting_date: string;
    harvest_start: string;
    harvest_end: string;
    expected_yield_mt: number;
    resource_plans?: ResourcePlanItem[];
  };
}

export default function SmartSchedule({ schedule }: ScheduleProps) {
  return (
    <div className="bg-gray-900 text-gray-100 p-6 rounded-lg shadow-md border border-green-600 mt-4">
      <div className="flex justify-between items-center border-b border-gray-700 pb-3 mb-4">
        <h3 className="text-xl font-bold text-green-400">
          Generated Smart Schedule {schedule.variety_name ? `— ${schedule.variety_name}` : ''}
        </h3>
        {schedule.maturity_days && (
          <span className="bg-green-900 text-green-300 text-xs font-semibold px-3 py-1 rounded-full">
            {schedule.maturity_days}-Day Crop Cycle
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-800 p-4 rounded border border-gray-700">
          <p className="text-xs text-gray-400 uppercase">Planting Date</p>
          <p className="text-lg font-mono text-white mt-1">{schedule.planting_date}</p>
        </div>

        <div className="bg-gray-800 p-4 rounded border border-gray-700">
          <p className="text-xs text-gray-400 uppercase">Estimated Harvest Window</p>
          <p className="text-lg font-mono text-yellow-400 mt-1">
            {schedule.harvest_start} &rarr; {schedule.harvest_end}
          </p>
        </div>

        <div className="bg-gray-800 p-4 rounded border border-gray-700">
          <p className="text-xs text-gray-400 uppercase">Projected Yield</p>
          <p className="text-2xl font-mono text-green-400 mt-1">
            {schedule.expected_yield_mt} <span className="text-sm">Metric Tons</span>
          </p>
        </div>
      </div>

      {schedule.resource_plans && schedule.resource_plans.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold uppercase tracking-wider text-gray-400 mb-3">
            Recommended Fertilizer & Input Schedule
          </h4>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-gray-700 text-gray-400">
                  <th className="py-2 px-3">Stage / Task</th>
                  <th className="py-2 px-3">Input Type</th>
                  <th className="py-2 px-3">Recommended Qty</th>
                  <th className="py-2 px-3">Target Date</th>
                  <th className="py-2 px-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {schedule.resource_plans.map((plan) => (
                  <tr key={plan.id} className="border-b border-gray-800 hover:bg-gray-800/60">
                    <td className="py-2.5 px-3 font-medium text-white">{plan.task_type}</td>
                    <td className="py-2.5 px-3 text-green-400">{plan.recommended_input}</td>
                    <td className="py-2.5 px-3 font-mono">
                      {plan.quantity} {plan.unit}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-yellow-300">{plan.due_date}</td>
                    <td className="py-2.5 px-3">
                      <span className="bg-blue-900/60 text-blue-300 px-2 py-0.5 rounded text-xs">
                        {plan.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}