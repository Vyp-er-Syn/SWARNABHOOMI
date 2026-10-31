import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default Leaflet marker icons in React
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

export default function FieldMap() {
  // Default center: Sri Lanka (Anuradhapura region)
  const center: [number, number] = [8.3114, 80.4037];

  return (
    <div className="w-full h-[500px] border-2 border-green-500 rounded-lg overflow-hidden shadow-lg mt-6">
      <MapContainer center={center} zoom={13} scrollWheelZoom={true} className="w-full h-full">
        {/* Free OpenStreetMap tiles */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker position={center}>
          <Popup>
            Your Farm Location <br /> Select bounds here.
          </Popup>
        </Marker>
      </MapContainer>
    </div>
  );
}