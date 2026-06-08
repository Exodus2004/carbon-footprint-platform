import React, { useState } from 'react';

function CarbonForm({ onSubmit, isLoading }) {
  const [metrics, setMetrics] = useState({
    transportation_miles: '',
    energy_kwh: '',
    diet_meat_meals: ''
  });

  const [errors, setErrors] = useState({});

  const validate = () => {
    const newErrors = {};
    if (metrics.transportation_miles === '' || Number(metrics.transportation_miles) < 0) {
      newErrors.transportation_miles = 'Please enter a non-negative number for miles driven.';
    }
    if (metrics.energy_kwh === '' || Number(metrics.energy_kwh) < 0) {
      newErrors.energy_kwh = 'Please enter a non-negative number for energy usage.';
    }
    if (metrics.diet_meat_meals === '' || Number(metrics.diet_meat_meals) < 0) {
      newErrors.diet_meat_meals = 'Please enter a non-negative number for meat meals.';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setMetrics(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear field error on change
    if (errors[name]) {
      setErrors(prev => {
        const copy = { ...prev };
        delete copy[name];
        return copy;
      });
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validate()) return;
    onSubmit({
      transportation_miles: parseFloat(metrics.transportation_miles) || 0,
      energy_kwh: parseFloat(metrics.energy_kwh) || 0,
      diet_meat_meals: parseInt(metrics.diet_meat_meals, 10) || 0
    });
  };

  const inputStyle = {
    width: '100%',
    padding: '0.75rem',
    border: '1px solid #ccc',
    borderRadius: '4px',
    boxSizing: 'border-box',
    color: '#1a1a1a',
    backgroundColor: '#ffffff',
    fontSize: '1rem',
  };

  const errorInputStyle = {
    ...inputStyle,
    borderColor: '#d32f2f',
    boxShadow: '0 0 0 2px rgba(211,47,47,0.25)',
  };

  const errorTextStyle = {
    color: '#d32f2f',
    fontSize: '0.85rem',
    marginTop: '0.35rem',
  };

  return (
    <section className="card" aria-labelledby="form-heading">
      <h2 id="form-heading">Weekly Carbon Metrics</h2>
      <form onSubmit={handleSubmit} noValidate aria-label="Carbon footprint data entry form">

        <fieldset style={{ border: 'none', padding: 0, margin: 0 }}>
          <legend className="sr-only" style={{ position: 'absolute', width: '1px', height: '1px', overflow: 'hidden', clip: 'rect(0,0,0,0)' }}>
            Enter your weekly carbon metrics
          </legend>

          <div className="form-group">
            <label htmlFor="transportation_miles" style={{ color: '#1a1a1a', fontWeight: 'bold' }}>
              Transportation (Miles Driven)
            </label>
            <input
              type="number"
              id="transportation_miles"
              name="transportation_miles"
              value={metrics.transportation_miles}
              onChange={handleChange}
              min="0"
              step="0.1"
              required
              aria-required="true"
              aria-invalid={!!errors.transportation_miles}
              aria-describedby={errors.transportation_miles ? 'transport-error' : 'transport-desc'}
              style={errors.transportation_miles ? errorInputStyle : inputStyle}
            />
            <span id="transport-desc" style={{ position: 'absolute', width: '1px', height: '1px', overflow: 'hidden', clip: 'rect(0,0,0,0)' }}>
              Miles driven using carbon-emitting transport
            </span>
            {errors.transportation_miles && (
              <p id="transport-error" role="alert" aria-live="assertive" style={errorTextStyle}>
                {errors.transportation_miles}
              </p>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="energy_kwh" style={{ color: '#1a1a1a', fontWeight: 'bold' }}>
              Energy Usage (kWh)
            </label>
            <input
              type="number"
              id="energy_kwh"
              name="energy_kwh"
              value={metrics.energy_kwh}
              onChange={handleChange}
              min="0"
              step="0.1"
              required
              aria-required="true"
              aria-invalid={!!errors.energy_kwh}
              aria-describedby={errors.energy_kwh ? 'energy-error' : 'energy-desc'}
              style={errors.energy_kwh ? errorInputStyle : inputStyle}
            />
            <span id="energy-desc" style={{ position: 'absolute', width: '1px', height: '1px', overflow: 'hidden', clip: 'rect(0,0,0,0)' }}>
              Energy usage in kilowatt-hours
            </span>
            {errors.energy_kwh && (
              <p id="energy-error" role="alert" aria-live="assertive" style={errorTextStyle}>
                {errors.energy_kwh}
              </p>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="diet_meat_meals" style={{ color: '#1a1a1a', fontWeight: 'bold' }}>
              Meat-Heavy Meals
            </label>
            <input
              type="number"
              id="diet_meat_meals"
              name="diet_meat_meals"
              value={metrics.diet_meat_meals}
              onChange={handleChange}
              min="0"
              step="1"
              required
              aria-required="true"
              aria-invalid={!!errors.diet_meat_meals}
              aria-describedby={errors.diet_meat_meals ? 'diet-error' : 'diet-desc'}
              style={errors.diet_meat_meals ? errorInputStyle : inputStyle}
            />
            <span id="diet-desc" style={{ position: 'absolute', width: '1px', height: '1px', overflow: 'hidden', clip: 'rect(0,0,0,0)' }}>
              Number of meat-heavy meals consumed
            </span>
            {errors.diet_meat_meals && (
              <p id="diet-error" role="alert" aria-live="assertive" style={errorTextStyle}>
                {errors.diet_meat_meals}
              </p>
            )}
          </div>
        </fieldset>

        <button
          type="submit"
          disabled={isLoading}
          aria-busy={isLoading}
          aria-label={isLoading ? 'Analyzing your carbon impact, please wait' : 'Submit your data to get AI insights'}
          style={{
            backgroundColor: isLoading ? '#9e9e9e' : '#2e7d32',
            color: '#ffffff',
            fontWeight: 'bold',
            fontSize: '1rem',
            padding: '0.75rem 1.5rem',
            border: 'none',
            borderRadius: '4px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            width: '100%',
          }}
        >
          {isLoading ? 'Analyzing Impact...' : 'Get AI Insights'}
        </button>
      </form>
    </section>
  );
}

export default CarbonForm;
