import React from 'react';
import OperationsDashboard from './components/OperationsDashboard.jsx';

function App() {
  return (
    <main id="main-content">
      <header role="banner">
        <h1>FIFA World Cup 2026 Operations Center</h1>
        <p style={{ margin: '0.5rem 0' }}>Stadium Crowd Flow & Multilingual Transit Routing Telemetry</p>
        <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap', marginTop: '1rem', fontSize: '0.9rem', color: '#1a1a1a', fontWeight: '500' }}>
          <span style={{ backgroundColor: '#e3f2fd', padding: '0.35rem 0.85rem', borderRadius: '16px', border: '1px solid #bbdefb' }}><span role="img" aria-label="lightning bolt">⚡</span> Decision Support</span>
          <span style={{ backgroundColor: '#e8f5e9', padding: '0.35rem 0.85rem', borderRadius: '16px', border: '1px solid #c8e6c9' }}><span role="img" aria-label="seedling">🌱</span> Sustainability Offset</span>
          <span style={{ backgroundColor: '#fff3e0', padding: '0.35rem 0.85rem', borderRadius: '16px', border: '1px solid #ffe0b2' }}><span role="img" aria-label="world map">🗺️</span> Navigation & Routing</span>
          <span style={{ backgroundColor: '#f3e5f5', padding: '0.35rem 0.85rem', borderRadius: '16px', border: '1px solid #e1bee7' }}><span role="img" aria-label="speaking head">🗣️</span> Multilingual Assist</span>
        </div>
      </header>
      <OperationsDashboard />
    </main>
  );
}

export default App;
