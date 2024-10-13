import React, { useState } from 'react';
import SemanticSearchBar from '../components/SemanticSearchBar';

const SemanticSearch = () => {
  const [result, setResult] = useState('');

  const performSearch = async (query) => {
    try {
      const response = await fetch('http://localhost:8081/semantic-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });
      const data = await response.json();
      setResult(data.result);  // Assume the backend returns the search result in the 'result' field
    } catch (error) {
      console.error('Error fetching search results:', error);
    }
  };

  return (
    <div className="semantic-search-page">
      <h1>Semantic Search</h1>
      <SemanticSearchBar onSearch={performSearch} />
      <div className="results-section">
        <h2>Result:</h2>
        {result ? <p>{result}</p> : <p>No results yet.</p>}
      </div>
    </div>
  );
};

export default SemanticSearch;
