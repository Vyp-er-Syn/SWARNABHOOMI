import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, useMap } from 'react-leaflet';
import axios from 'axios';
import * as turf from '@turf/turf';
import 'leaflet/dist/leaflet.css';
import '@geoman-io/leaflet-geoman-free';
import '@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css';

// Sub-component to attach Geoman controls to the Leaflet map instance
function GeomanControls({ onPolygonComplete }: { onPolygonComplete: (coords: number[][]) => void }) {
  const map = useMap();

  useEffect(() => {
    // Enable the Geoman drawing toolbar
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
    
    // Set custom styling for the polygon being drawn
    map.pm.setPathOptions({
      color: '#10b981', // Tailwind green-500
      weight: 3,
    });

    // Listen for when a farmer finishes drawing the polygon
    map.on('pm:create', (e: any) => {
      if (e.shape === 'Polygon') {
        const layer = e.layer;
        const latLngs = layer.getLatLngs()[0];
        const coordinates = latLngs.map((coord: any) => [coord.lng, coord.lat]);
        coordinates.push(coordinates[0]); // Close the polygon for GeoJSON
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
  const center: [number, number] = [8.3114, 80.4037]; // Anuradhapura
  const [fieldCoordinates, setFieldCoordinates] = useState<number[][][]>([]);
  const [calculatedArea, setCalculatedArea] = useState({ acres: 0, perches: 0 });
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Form State
  const [fieldName, setFieldName] = useState("My Paddy Plot");
  const [plantingDate, setPlantingDate] = useState("");

  const handlePolygonComplete = (coordinates: number[][]) => {
    const polygon = turf.polygon([coordinates]);
    const areaSqMeters = turf.area(polygon);
    
    setCalculatedArea({
      acres: parseFloat((areaSqMeters / 4046.86).toFixed(2)),
      perches: parseFloat((areaSqMeters / 25.2929).toFixed(1))
    });
    setFieldCoordinates([coordinates]);
  };

  const registerCultivation = async () => {
    if (fieldCoordinates.length === 0 || !plantingDate) {
      alert("Please draw a boundary and select a planting date.");
      return;
    }

    setIsSubmitting(true);
    try {
      // 1. Save the Field Boundary
      const fieldPayload = {
        name: fieldName,
        area: calculatedArea.acres, 
        water_regime_id: "Irrigated",
        soil_profile_id: "Reddish Brown Earth",
        farm_id: 1, 
        geometry_coordinates: fieldCoordinates
      };
      const fieldRes = await axios.post('http://localhost:8000/api/fields', fieldPayload);
      
      // 2. Register the Cultivation to trigger the Intelligence Engine
      const cultivationPayload = {
        field_id: fieldRes.data.id,
        season_id: 1, 
        variety_id: 1, 
        planting_date: plantingDate,
        area: calculatedArea.acres
      };
      await axios.post('http://localhost:8000/api/cultivations', cultivationPayload);
      
      alert(`Success! Field mapped and cultivation scheduled.`);
      // Clear form
      setFieldCoordinates([]);
      setCalculatedArea({ acres: 0, perches: 0 });
    } catch (error) {
      console.error("Error:", error);
      alert("Failed to save. Ensure your FastAPI backend is running.");
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
        </MapContainer>
      </div>
      
      {fieldCoordinates.length > 0 && (
        <div className="bg-gray-900 text-gray-100 p-6 rounded-lg shadow-md border border-gray-700">
          <h3 className="text-xl font-semibold mb-4 border-b border-gray-700 pb-2">Cultivation Details</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
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
    </div>
  );
}