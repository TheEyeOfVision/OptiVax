import React, { useEffect } from 'react';
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMap,
  Tooltip,
} from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Vaccination center star icons
import redStarIcon from './red-star.png';
import blueStarIcon from './blue-star.png';
import greenStarIcon from './green-star.png';
import orangeStarIcon from './orange-star.png';
import purpleStarIcon from './purple-star.png';
import yellowStarIcon from './yellow-star.png';
import cyanStarIcon from './cyan-star.png';
import brownStarIcon from './brown-star.png';

// Barangay colored marker icons
import redMarkerIcon from './red-marker.png';
import blueMarkerIcon from './blue-marker.png';
import greenMarkerIcon from './green-marker.png';
import orangeMarkerIcon from './orange-marker.png';
import purpleMarkerIcon from './purple-marker.png';
import yellowMarkerIcon from './yellow-marker.png';
import cyanMarkerIcon from './cyan-marker.png';
import brownMarkerIcon from './brown-marker.png';

const vaccinationCenterIconMap = {
  red: L.icon({ iconUrl: redStarIcon, iconSize: [24, 24], iconAnchor: [16, 32] }),
  blue: L.icon({ iconUrl: blueStarIcon, iconSize: [24, 24], iconAnchor: [16, 32] }),
  green: L.icon({ iconUrl: greenStarIcon, iconSize: [24, 24], iconAnchor: [16, 32] }),
  orange: L.icon({ iconUrl: orangeStarIcon, iconSize: [24, 24], iconAnchor: [16, 32] }),
  purple: L.icon({ iconUrl: purpleStarIcon, iconSize: [24, 24], iconAnchor: [16, 32] }),
  yellow: L.icon({ iconUrl: yellowStarIcon, iconSize: [24, 24], iconAnchor: [16, 32] }),
  cyan: L.icon({ iconUrl: cyanStarIcon, iconSize: [24, 24], iconAnchor: [16, 32] }),
  brown: L.icon({ iconUrl: brownStarIcon, iconSize: [24, 24], iconAnchor: [16, 32] }),
};

const barangayIconMap = {
  red: L.icon({ iconUrl: redMarkerIcon, iconSize: [23, 35], iconAnchor: [12, 41] }),
  blue: L.icon({ iconUrl: blueMarkerIcon, iconSize: [23, 35], iconAnchor: [12, 41] }),
  green: L.icon({ iconUrl: greenMarkerIcon, iconSize: [23, 35], iconAnchor: [12, 41] }),
  orange: L.icon({ iconUrl: orangeMarkerIcon, iconSize: [23, 35], iconAnchor: [12, 41] }),
  purple: L.icon({ iconUrl: purpleMarkerIcon, iconSize: [23, 35], iconAnchor: [12, 41] }),
  yellow: L.icon({ iconUrl: yellowMarkerIcon, iconSize: [23, 35], iconAnchor: [12, 41] }),
  cyan: L.icon({ iconUrl: cyanMarkerIcon, iconSize: [23, 35], iconAnchor: [12, 41] }),
  brown: L.icon({ iconUrl: brownMarkerIcon, iconSize: [23, 35], iconAnchor: [12, 41] }),
};

const defaultBarangayIcon = L.icon({
  iconUrl: redMarkerIcon, // fallback icon
  iconSize: [23, 35],
  iconAnchor: [12, 41],
});

const MapComponent = ({ selectedSites = [], barangays = {}, assignments = [], showTooltips = true }) => {
  const defaultCenter = [14.5825, 120.9784];

  const MapBounds = () => {
    const map = useMap();
    useEffect(() => {
      const allLocations = [
        ...((Array.isArray(selectedSites) && selectedSites.map((site) => [site.coordinates[0], site.coordinates[1]])) || []),
        ...((Array.isArray(barangays.locations) && barangays.locations) || []),
      ];
      if (allLocations.length > 0) {
        const bounds = L.latLngBounds(allLocations);
        map.fitBounds(bounds, { padding: [50, 50] });
      }
    }, [selectedSites, barangays, map]);
    return null;
  };

  return (
    <div className="map-container">
      <MapContainer center={defaultCenter} zoom={10} scrollWheelZoom={true} style={{ width: '860px', height: '384px' }}>
        <TileLayer attribution='&copy; OpenStreetMap contributors' url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png' />
        
        {/* Vaccination center markers */}
        {Array.isArray(selectedSites) && selectedSites.map((site) => {
          const icon = vaccinationCenterIconMap[site.color] || vaccinationCenterIconMap.red;
          return (
            <Marker key={`site-${site.index}`} position={[site.coordinates[0], site.coordinates[1]]} icon={icon}>
              {showTooltips && (
                <Tooltip direction="top" offset={[0, -20]} opacity={1} permanent>
                  <span style={{ fontSize: '14px' }}>{site.name}</span>
                </Tooltip>
              )}
              <Popup>{site.name}</Popup>
            </Marker>
          );
        })}

        {/* Barangay markers */}
        {Array.isArray(barangays.locations) && barangays.locations.map((location, index) => {
          const assignment = assignments.find(a => a.barangay_index === index);
          const barangayColor = assignment && assignment.closest_center && assignment.closest_center.color;
          const icon = barangayIconMap[barangayColor] || defaultBarangayIcon;
          return (
            <Marker key={`barangay-${index}`} position={location} icon={icon} title={barangays.names[index]}>
              {showTooltips && (
                <Tooltip direction="top" offset={[0, -20]} opacity={1} permanent>
                  <span style={{ fontSize: '11px' }}>{barangays.names[index]}</span>
                </Tooltip>
              )}
              <Popup>
                <div>
                  <strong>{barangays.names[index]}</strong>
                  <p>Infected: {barangays.infected[index]}</p>
                  <p>Population: {barangays.populations[index]}</p>
                  <p>
                    Percentage: {((barangays.infected[index] / barangays.populations[index]) * 100).toFixed(2)}%
                  </p>
                  {assignment && assignment.closest_center && (
                    <p>
                      Closest Vaccination Center: {assignment.closest_center.name} <br />
                      (Distance: {assignment.distance.toFixed(2)} m)
                    </p>
                  )}
                </div>
              </Popup>
            </Marker>
          );
        })}
        <MapBounds />
      </MapContainer>
    </div>
  );
};

export default MapComponent;
