import React, { useState } from 'react';

function OperationsDashboard() {
  const [inputs, setInputs] = useState({
    stadium_zone_id: 'ZONE_A',
    current_crowd_count: '',
    active_transit_vehicles: ''
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setInputs(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    const payload = {
      stadium_zone_id: inputs.stadium_zone_id,
      current_crowd_count: parseInt(inputs.current_crowd_count, 10) || 0,
      active_transit_vehicles: parseInt(inputs.active_transit_vehicles, 10) || 0
    };

    try {
      const baseUrl = import.meta.env.VITE_API_URL || 'https://carbon-backend-949126109965.us-central1.run.app';
      const response = await fetch(`${baseUrl}/api/v1/operations/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error('Failed to analyze operations data from the server.');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <section className="card" aria-labelledby="form-heading">
        <h2 id="form-heading">Telemetry Submission</h2>
        <form onSubmit={handleSubmit} aria-label="Stadium telemetry input form">
          
          <div className="form-group">
            <label htmlFor="stadium_zone_id">Stadium Zone</label>
            <select
              id="stadium_zone_id"
              name="stadium_zone_id"
              value={inputs.stadium_zone_id}
              onChange={handleChange}
              aria-required="true"
            >
              <option value="ZONE_A">Zone A (North Gate)</option>
              <option value="ZONE_B">Zone B (South Gate)</option>
              <option value="ZONE_C">Zone C (East Plaza)</option>
              <option value="ZONE_D">Zone D (West Plaza)</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="current_crowd_count">Current Crowd Count</label>
            <input
              type="number"
              id="current_crowd_count"
              name="current_crowd_count"
              value={inputs.current_crowd_count}
              onChange={handleChange}
              min="0"
              required
              aria-required="true"
              placeholder="e.g. 12000"
            />
          </div>

          <div className="form-group">
            <label htmlFor="active_transit_vehicles">Active Transit Vehicles</label>
            <input
              type="number"
              id="active_transit_vehicles"
              name="active_transit_vehicles"
              value={inputs.active_transit_vehicles}
              onChange={handleChange}
              min="0"
              required
              aria-required="true"
              placeholder="e.g. 15"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            aria-busy={loading}
            aria-label={loading ? 'Analyzing telemetry data, please wait' : 'Analyze stadium metrics'}
          >
            {loading ? 'Analyzing Telemetry...' : 'Analyze Metrics'}
          </button>
        </form>
      </section>

      {error && (
        <div className="alert alert-error" role="alert" aria-live="assertive">
          <strong>Error: </strong> {error}
        </div>
      )}

      <section className="card" aria-labelledby="insights-heading">
        <h2 id="insights-heading">Operations Insights</h2>
        <div
          id="insight-container"
          aria-live="polite"
          aria-atomic="true"
          style={{ minHeight: '100px' }}
        >
          {!result && !loading && (
            <p style={{ color: '#333333' }}>Submit the operations form above to generate real-time multilingual dispatch signals.</p>
          )}

          {loading && (
            <p style={{ color: '#0d47a1', fontWeight: 'bold' }}>FIFA Logistics Coordinator is parsing crowd flow telemetry...</p>
          )}

          {result && (
            <div style={{ marginTop: '1rem' }}>
              <div
                className={result.fifa_safety_compliance ? "alert alert-success" : "alert alert-error"}
                role="status"
              >
                <strong>Status: </strong>
                {result.fifa_safety_compliance 
                  ? "FIFA Safety Compliant - Standard Operations" 
                  : "Safety Alert - Non-Compliance Detected!"}
              </div>

              <table>
                <caption>Operations Telemetry Metrics</caption>
                <thead>
                  <tr>
                    <th scope="col">Parameter</th>
                    <th scope="col">Value</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Stadium Zone ID</td>
                    <td>{result.stadium_zone_id}</td>
                  </tr>
                  <tr>
                    <td>Crowd Density Index</td>
                    <td>{result.crowd_density_index.toFixed(4)}</td>
                  </tr>
                  <tr>
                    <td>Transit Bottleneck Risk</td>
                    <td>{result.transit_bottleneck_risk}</td>
                  </tr>
                </tbody>
              </table>

              <div style={{ marginTop: '1.5rem', padding: '1rem', borderLeft: '4px solid #0d47a1', backgroundColor: '#f0f4c3' }}>
                <h3 style={{ marginTop: 0, color: '#1b3a0a' }}>Despacho Multilingüe (ES)</h3>
                <p style={{ fontStyle: 'italic', margin: 0 }}>{result.multilingual_dispatch_es}</p>
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

export default OperationsDashboard;
