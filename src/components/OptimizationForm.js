// components/OptimizationForm.js
import React from 'react';

const OptimizationForm = () => {
  return (
    <div className="form-container">
      <div className="form-group">
        <label>Optimization Techniques:</label>
        <div>
          <input type="radio" id="simple" name="optimization" value="simple" />
          <label htmlFor="simple">Simple</label>
        </div>
        <div>
          <input type="radio" id="bi-objective" name="optimization" value="bi-objective" />
          <label htmlFor="bi-objective">Bi-objective</label>
        </div>
        <div>
          <input type="radio" id="dynamic" name="optimization" value="dynamic" />
          <label htmlFor="dynamic">Dynamic</label>
        </div>
      </div>
      <div className="form-group">
        <label htmlFor="optimization-sites">Number of Optimization Sites (L):</label>
        <input type="text" id="optimization-sites" name="optimization-sites" />
      </div>
      <div className="form-group">
        <label htmlFor="radius">Radius:</label>
        <input type="text" id="radius" name="radius" />
      </div>
      <div className="form-group">
        <label htmlFor="distance-formula">Distance Formula:</label>
        <select id="distance-formula" name="distance-formula">
          <option value="time">Time</option>
          <option value="road">Road</option>
          <option value="euclidean">Euclidean</option>
        </select>
      </div>
      <div className="form-group">
        <label htmlFor="method">Method:</label>
        <select id="method" name="method">
          <option value="genetic">Genetic</option>
          <option value="numerical">Numerical</option>
        </select>
      </div>
    </div>
  );
};

export default OptimizationForm;
