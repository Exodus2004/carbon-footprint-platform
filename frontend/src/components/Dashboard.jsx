import React from 'react';

function Dashboard({ data, insights, onReset }) {
  // Carbon estimation factors
  const estTransport = data.transportation_miles * 0.404; // kg CO2 per mile (avg car)
  const estEnergy = data.energy_kwh * 0.385; // kg CO2 per kWh
  const estDiet = data.diet_meat_meals * 2.5; // kg CO2 per meat meal (rough avg)
  const totalCarbon = (estTransport + estEnergy + estDiet).toFixed(2);

  const statRowStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '1rem 0',
    borderBottom: '1px solid #e0e0e0',
    color: '#1a1a1a',
    fontSize: '1rem',
  };

  const totalRowStyle = {
    ...statRowStyle,
    fontSize: '1.25rem',
    borderBottom: 'none',
    marginTop: '1rem',
    paddingTop: '1rem',
    borderTop: '2px solid #424242',
  };

  return (
    <div role="region" aria-label="Dashboard showing your carbon footprint results and AI insights">

      <section className="card" aria-labelledby="insights-heading">
        <h2 id="insights-heading" style={{ color: '#1a1a1a' }}>AI Environmental Insights</h2>
        <div
          className="alert alert-success"
          role="status"
          aria-live="polite"
          aria-atomic="true"
          style={{ color: '#1b5e20', backgroundColor: '#e8f5e9', border: '1px solid #2e7d32', borderRadius: '4px', padding: '1rem' }}
        >
          <p>{insights}</p>
        </div>
      </section>

      <section className="card" aria-labelledby="metrics-heading">
        <h2 id="metrics-heading" style={{ color: '#1a1a1a' }}>Your Weekly Estimated Emissions</h2>

        <table
          role="table"
          aria-label="Breakdown of estimated weekly CO2 emissions by category"
          style={{ width: '100%', borderCollapse: 'collapse' }}
        >
          <thead style={{ position: 'absolute', width: '1px', height: '1px', overflow: 'hidden', clip: 'rect(0,0,0,0)' }}>
            <tr>
              <th scope="col">Category</th>
              <th scope="col">Estimated Emissions</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={statRowStyle}>
                <span>Transportation</span>
              </td>
              <td style={statRowStyle}>
                <strong aria-label={`Transportation emissions: ${estTransport.toFixed(2)} kilograms CO2 equivalent`}>
                  {estTransport.toFixed(2)} kg CO2e
                </strong>
              </td>
            </tr>
            <tr>
              <td style={statRowStyle}>
                <span>Energy Usage</span>
              </td>
              <td style={statRowStyle}>
                <strong aria-label={`Energy usage emissions: ${estEnergy.toFixed(2)} kilograms CO2 equivalent`}>
                  {estEnergy.toFixed(2)} kg CO2e
                </strong>
              </td>
            </tr>
            <tr>
              <td style={statRowStyle}>
                <span>Diet</span>
              </td>
              <td style={statRowStyle}>
                <strong aria-label={`Diet emissions: ${estDiet.toFixed(2)} kilograms CO2 equivalent`}>
                  {estDiet.toFixed(2)} kg CO2e
                </strong>
              </td>
            </tr>
            <tr>
              <td style={totalRowStyle}>
                <strong>Total Estimated</strong>
              </td>
              <td style={totalRowStyle}>
                <strong aria-label={`Total estimated emissions: ${totalCarbon} kilograms CO2 equivalent`}>
                  {totalCarbon} kg CO2e
                </strong>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <button
        onClick={onReset}
        aria-label="Clear current results and submit a new carbon footprint entry"
        style={{
          backgroundColor: '#2e7d32',
          color: '#ffffff',
          fontWeight: 'bold',
          fontSize: '1rem',
          padding: '0.75rem 1.5rem',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          width: '100%',
        }}
      >
        Submit New Entry
      </button>
    </div>
  );
}

export default Dashboard;
