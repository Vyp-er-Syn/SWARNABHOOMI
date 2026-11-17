import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Polygon as LeafletPolygon, Tooltip, useMap } from 'react-leaflet';
import axios from 'axios';
import * as turf from '@turf/turf';
import 'leaflet/dist/leaflet.css';
import '@geoman-io/leaflet-geoman-free';
import '@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css';
import SmartSchedule from './SmartSchedule';

function GeomanControls({ onPolygonComplete }: { onPolygonComplete: (coords: number[][]) => void }) {
  const map = useMap();

  useEffect(() => {
    map.pm.addControls({
      position: 'topright',
      drawCircle: false,
      drawCircleMarker: false,
      drawMarker: false,
      drawPolyline: false,
      drawRectangle: false,
      drawText: false,
      editMode: true,
      dragMode: false,
      removalMode: true,
    });

    map.pm.setPathOptions({
      color: '#10b981',
      weight: 3,
    });

    map.on('pm:create', (e: any) => {
      if (e.shape === 'Polygon') {
        const layer = e.layer;
        const latLngs = layer.getLatLngs()[0];
        const coordinates = latLngs.map((coord: any) => [coord.lng, coord.lat]);
        coordinates.push(coordinates[0]);
        onPolygonComplete(coordinates);
      }
    });

    return () => {
      map.pm.removeControls();
      map.off('pm:create');
    };
  }, [map, onPolygonComplete]);

  return null;
}

export default function FieldMap() {
  const center: [number, number] = [8.3114, 80.4037];
  const [fieldCoordinates, setFieldCoordinates] = useState<number[][][]>([]);
  const [calculatedArea, setCalculatedArea] = useState({ acres: 0, perches: 0 });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [scheduleData, setScheduleData] = useState<any>(null);

  const [savedFields, setSavedFields] = useState<any[]>([]);
  const [varieties, setVarieties] = useState<any[]>([]);

  // Form State
  const [fieldName, setFieldName] = useState("My Paddy Plot");
  const [plantingDate, setPlantingDate] = useState("");
  const [selectedVariety, setSelectedVariety] = useState<number>(1);
  const [waterRegimeId, setWaterRegimeId] = useState<number>(1);
  const [soilProfileId, setSoilProfileId] = useState<number>(1);

  const loadInitialData = async () => {
    try {
      const [fieldsRes, varRes] = await Promise.all([
        axios.get('http://127.0.0.1:8000/api/fields'),
        axios.get('http://127.0.0.1:8000/api/catalog/varieties'),
      ]);
      setSavedFields(fieldsRes.data || []);
      if (varRes.data && varRes.data.length > 0) {
        setVarieties(varRes.data);
        setSelectedVariety(varRes.data[0].id);
      }
    } catch (err) {
      console.error("Failed to load initial map data:", err);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  const handlePolygonComplete = (coordinates: number[][]) => {
    const polygon = turf.polygon([coordinates]);
    const areaSqMeters = turf.area(polygon);

    setCalculatedArea({
      acres: parseFloat((areaSqMeters / 4046.86).toFixed(2)),
      perches: parseFloat((areaSqMeters / 25.2929).toFixed(1))
    });
    setFieldCoordinates([coordinates]);
    setScheduleData(null);
  };

  const registerCultivation = async () => {
    if (fieldCoordinates.length === 0 || !plantingDate) {
      alert("Please draw a boundary and select a planting date.");
      return;
    }

    setIsSubmitting(true);
    try {
      const fieldPayload = {
        name: fieldName,
        area: calculatedArea.acres > 0 ? calculatedArea.acres : 0.1,
        water_regime_id: waterRegimeId,
        soil_profile_id: soilProfileId,
        farm_id: 1,
        geometry_coordinates: fieldCoordinates
      };
      const fieldRes = await axios.post('http://127.0.0.1:8000/api/fields', fieldPayload);

      const cultivationPayload = {
        field_id: fieldRes.data.id,
        season_id: 1,
        variety_id: selectedVariety,
        planting_date: plantingDate,
        status: "Planned"
      };
      const cultRes = await axios.post('http://127.0.0.1:8000/api/cultivations', cultivationPayload);

      const scheduleRes = await axios.get(`http://127.0.0.1:8000/api/cultivations/${cultRes.data.id}/schedule`);
      setScheduleData(scheduleRes.data);

      alert("Success! Field mapped and cultivation scheduled.");
      setFieldCoordinates([]);
      setCalculatedArea({ acres: 0, perches: 0 });
      loadInitialData();
    } catch (error: any) {
      const detail = error?.response?.data?.detail;
      console.error("Submission error:", detail || error);
      alert(`Failed to save: ${detail ? JSON.stringify(detail) : "Ensure FastAPI backend is running on port 8000."}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="w-full flex flex-col gap-6 mt-6">
      <div className="w-full h-[500px] border-2 border-gray-800 rounded-lg overflow-hidden shadow-lg z-0 relative">
        <MapContainer center={center} zoom={13} scrollWheelZoom={true} className="w-full h-full">
          <TileLayer
            attribution='&copy; Google Maps'
            url="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
            maxZoom={20}
          />
          <GeomanControls onPolygonComplete={handlePolygonComplete} />

          {/* Render existing saved fields on the map */}
          {savedFields.map((f) => {
            const coords = f.geometry?.coordinates?.[0];
            if (!coords) return null;
            const latLngs = coords.map((c: number[]) => [c[1], c[0]] as [number, number]);
            return (
              <LeafletPolygon
                key={f.id}
                positions={latLngs}
                pathOptions={{ color: '#3b82f6', weight: 2, fillOpacity: 0.35 }}
              >
                <Tooltip sticky>
                  <div className="text-xs font-semibold">
                    {f.name} ({f.area} Acres)
                  </div>
                </Tooltip>
              </LeafletPolygon>
            );
          })}
        </MapContainer>
      </div>

      {fieldCoordinates.length > 0 && (
        <div className="bg-gray-900 text-gray-100 p-6 rounded-lg shadow-md border border-gray-700">
          <h3 className="text-xl font-semibold mb-4 border-b border-gray-700 pb-2">Cultivation Details</h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Measured Area</label>
              <div className="text-lg font-mono text-green-400">
                {calculatedArea.acres} Acres <span className="text-gray-500 text-sm">({calculatedArea.perches} Perches)</span>
              </div>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Field Name</label>
              <input
                type="text"
                value={fieldName}
                onChange={(e) => setFieldName(e.target.value)}
                className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-green-500"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Estimated Planting Date</label>
              <input
                type="date"
                value={plantingDate}
                onChange={(e) => setPlantingDate(e.target.value)}
                className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-green-500"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Rice Variety</label>
              <select
                value={selectedVariety}
                onChange={(e) => setSelectedVariety(Number(e.target.value))}
                className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-green-500"
              >
                {varieties.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.name} — {v.variety_class} ({v.maturity_days}d)
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Water Regime</label>
              <select
                value={waterRegimeId}
                onChange={(e) => setWaterRegimeId(Number(e.target.value))}
                className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-green-500"
              >
                <option value={1}>Irrigated (Major/Minor Tank)</option>
                <option value={2}>Rainfed</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Soil Profile</label>
              <select
                value={soilProfileId}
                onChange={(e) => setSoilProfileId(Number(e.target.value))}
                className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-green-500"
              >
                <option value={1}>Reddish Brown Earth</option>
                <option value={2}>Low Humic Gley</option>
                <option value={3}>Alluvial Soil</option>
              </select>
            </div>
          </div>

          <button
            onClick={registerCultivation}
            disabled={isSubmitting || !plantingDate}
            className={`w-full py-3 rounded font-bold text-white transition-colors ${
              !isSubmitting && plantingDate
                ? 'bg-green-600 hover:bg-green-700'
                : 'bg-gray-700 text-gray-500 cursor-not-allowed'
            }`}
          >
            {isSubmitting ? 'Processing Engine...' : 'Register Cultivation & Generate Smart Schedule'}
          </button>
        </div>
      )}

      {scheduleData && <SmartSchedule schedule={scheduleData} />}
    </div>
  );
}