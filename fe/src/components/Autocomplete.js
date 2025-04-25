// Autocomplete.jsx

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TextField, List, ListItem, ListItemText } from '@mui/material';

const Autocomplete = ({ accessToken, onSelect, value, onChange }) => {
  const [suggestions, setSuggestions] = useState([]);
  const [debouncedValue, setDebouncedValue] = useState(value);

  // Debounce the user input by 500ms
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, 500); // 500ms delay

    return () => {
      clearTimeout(handler);
    };
  }, [value]);

  // Fetch suggestions when debouncedValue changes
  useEffect(() => {
    if (!debouncedValue) {
      setSuggestions([]);
      return;
    }

    const fetchSuggestions = async () => {
      try {
        const response = await axios.get(
          `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(debouncedValue)}.json`,
          {
            params: {
              access_token: accessToken,
              autocomplete: true,
              limit: 5,
            },
          }
        );
        setSuggestions(response.data.features);
      } catch (error) {
        console.error('Error fetching suggestions:', error);
      }
    };

    fetchSuggestions();
  }, [debouncedValue, accessToken]);

  // Handle selecting a suggestion
  const handleSelect = (place) => {
    onSelect(place);
    setSuggestions([]);
  };

  return (
    <div style={{ position: 'relative' }}>
      <TextField
        fullWidth
        value={value}
        onChange={onChange} // Handle both manual input and autocomplete
        placeholder="Enter Address"
        label="Address"
        variant="outlined"
        margin="normal"
      />
      {suggestions.length > 0 && (
        <List
          component="nav"
          aria-label="suggestions"
          style={{
            position: 'absolute',
            zIndex: 1000,
            backgroundColor: 'white',
            width: '100%',
            maxHeight: '200px',
            overflowY: 'auto',
            boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
          }}
        >
          {suggestions.map((place) => (
            <ListItem button key={place.id} onClick={() => handleSelect(place)}>
              <ListItemText primary={place.place_name} />
            </ListItem>
          ))}
        </List>
      )}
    </div>
  );
};

export default Autocomplete;
