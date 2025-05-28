import React, { useState } from 'react';
import {
  Container,
  Paper,
  Box,
  Button,
  Typography,
  TextField,
  CircularProgress,
  Checkbox,
  FormControlLabel,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import { MdInfoOutline } from 'react-icons/md'; // Using react-icons instead of MUI icons
import MapComponent from './components/MapComponent';
import axios from 'axios';
import Autocomplete from './components/Autocomplete';
import 'leaflet/dist/leaflet.css';

function App() {
  const [fileName, setFileName] = useState('');
  const [numSites, setNumSites] = useState('');
  const [address, setAddress] = useState('');
  const [transformedData, setTransformedData] = useState(null);
  const [optimizationResult, setOptimizationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showTooltips, setShowTooltips] = useState(true); // State to toggle tooltips
  const [openInfoDialog, setOpenInfoDialog] = useState(false); // State for the info dialog

  const MAPBOX_ACCESS_TOKEN = 'YOUR_MAPBOX_ACCESS_TOKEN';
  const API_BASE_URL = 'http://10.207.9.54:8000';

  // Handle file upload
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    setError(null);
    if (file) {
      setFileName(file.name);
      setOptimizationResult(null);
      const formData = new FormData();
      formData.append('file', file);
      try {
        setLoading(true);
        const response = await axios.post(`${API_BASE_URL}/transform-xlsx/`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        setTransformedData(response.data.data);
        setLoading(false);
      } catch (err) {
        console.error('Error uploading file:', err);
        setError('Failed to upload and transform the XLSX file.');
        setLoading(false);
      }
    }
  };

  // Handle calculation
  const handleCalculateClick = async () => {
    console.log('Number of Sites (L):', numSites);
    console.log('Transformed Data:', transformedData);

    if (!numSites || !transformedData) {
      setError('Please provide all required inputs: Address, Number of Sites, and upload a file.');
      return;
    }
    const L = parseInt(numSites, 10);
    if (isNaN(L) || L <= 0) {
      setError('Number of Sites (L) must be a positive integer.');
      return;
    }

    const payload = {
      L: L,
      method: 'numerical',
      sites: transformedData.sites,
      barangays: transformedData.barangays,
      distance_formula: 'road',
    };

    const endpoint = `${API_BASE_URL}/simple-optimization/`;
    console.log('Endpoint:', endpoint);
    console.log('Payload to send:', JSON.stringify(payload, null, 2));

    try {
      setLoading(true);
      const response = await axios.post(endpoint, payload, {
        headers: { 'Content-Type': 'application/json' },
      });
      setOptimizationResult(response.data);
      console.log('Optimization Result:', response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error performing optimization:', err);
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError('Failed to perform optimization.');
      }
      setLoading(false);
    }
  };

  const handleAddressSelect = (place) => {
    setAddress(place.place_name);
    console.log('Selected Address:', place.place_name);
  };

  const handleManualAddressChange = (event) => {
    setAddress(event.target.value);
    console.log('Manual Address Input:', event.target.value);
  };

  return (
    <Container maxWidth="md" sx={{ textAlign: 'center', padding: '20px' }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Optimal selection of COVID-19 vaccination sites in the Philippines at the municipal level
      </Typography>
      <Box sx={{ marginBottom: '20px', display: 'flex', justifyContent: 'center' }}>
        <Button variant="contained" component="label" color="primary">
          Choose File
          <input type="file" accept=".xlsx" hidden onChange={handleFileUpload} />
        </Button>
      </Box>
      {fileName && (
        <Typography variant="body1" gutterBottom>
          Selected File: {fileName}
        </Typography>
      )}
      
      <TextField
        fullWidth
        label="Number of Optimization Sites (L)"
        placeholder="Number of Optimization Sites (L)"
        margin="normal"
        value={numSites}
        onChange={(e) => setNumSites(e.target.value)}
      />
      {/* Checkbox with info button */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
          marginTop: '16px',
        }}
      >
        <FormControlLabel
          control={
            <Checkbox
              checked={showTooltips}
              onChange={(e) => setShowTooltips(e.target.checked)}
              color="primary"
            />
          }
          label="Show Tooltips"
        />
        <IconButton onClick={() => setOpenInfoDialog(true)} size="small">
          <MdInfoOutline size={24} />
        </IconButton>
      </Box>
      <Box sx={{ marginTop: '20px' }}>
        <Button variant="contained" color="primary" onClick={handleCalculateClick} disabled={loading}>
          {loading ? <CircularProgress size={24} color="inherit" /> : 'Calculate'}
        </Button>
      </Box>
      {optimizationResult && (
        <>
          <Box sx={{ marginTop: '20px' }}>
            <Paper elevation={3}>
              <MapComponent 
                selectedSites={optimizationResult.selected_sites} 
                barangays={transformedData.barangays} 
                assignments={optimizationResult.barangay_assignments}
                showTooltips={showTooltips} 
              />
            </Paper>
          </Box>
          {/* Table displaying assignments */}
          <Box sx={{ marginTop: '20px' }}>
            <Typography variant="h5" gutterBottom>
              Barangay Assignments
            </Typography>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Barangay</strong></TableCell>
                    <TableCell><strong>Nearest Vaccination Center</strong></TableCell>
                    <TableCell><strong>Distance (m)</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {transformedData.barangays.names.map((name, index) => {
                    const assignment = optimizationResult.barangay_assignments.find(
                      (a) => a.barangay_index === index
                    );
                    return (
                      <TableRow key={index}>
                        <TableCell>{name}</TableCell>
                        <TableCell>
                          {assignment && assignment.closest_center
                            ? assignment.closest_center.name
                            : 'N/A'}
                        </TableCell>
                        <TableCell>
                          {assignment ? assignment.distance.toFixed(2) : 'N/A'}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        </>
      )}
      {error && (
        <Box sx={{ marginTop: '20px', textAlign: 'left' }}>
          <Typography variant="h6" color="error">Error:</Typography>
          <Typography variant="body1" color="error">{error}</Typography>
        </Box>
      )}

      {/* Info dialog explaining tooltips */}
      <Dialog open={openInfoDialog} onClose={() => setOpenInfoDialog(false)}>
        <DialogTitle>Tooltip Information</DialogTitle>
        <DialogContent>
          <DialogContentText>
            When enabled, tooltips will display quick information on the map markers.
            Even if you disable tooltips, you can still access detailed information by clicking on the markers (pins).
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenInfoDialog(false)} color="primary">
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default App;
