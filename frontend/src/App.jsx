import React, { useState } from 'react';
import CarbonForm from './components/CarbonForm.jsx';
import Dashboard from './components/Dashboard.jsx';

function App() {
  const [data, setData] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (metrics) => {
    setLoading(true);
    setError(null);
    try {
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/api/v1/carbon`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Mock token since Firebase is not fully configured on client
          'Authorization': 'Bearer mock_local_token'
        },
        body: JSON.stringify(metrics)
      });

      if (!response.ok) {
        throw new Error('Failed to submit metrics to the server.');
      }

      const result = await response.json();
      setData(metrics);
      setInsights(result.insights);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="container" id="main-content">
      <header role="banner">
        <h1>Carbon Footprint Awareness Platform</h1>
        <p>Track your emissions and get personalized AI recommendations to reduce your impact.</p>
      </header>
      
      {error && (
        <div className="alert alert-error" role="alert" aria-live="assertive">
          <strong>Error: </strong> {error}
        </div>
      )}

      {!data ? (
        <CarbonForm onSubmit={handleSubmit} isLoading={loading} />
      ) : (
        <Dashboard data={data} insights={insights} onReset={() => setData(null)} />
      )}
    </main>
  );
}

export default App;
