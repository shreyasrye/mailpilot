import React, { useState } from 'react';

const SemanticSearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (query) {
      onSearch(query);  // Trigger the search function passed as a prop
    }
  };

  return (
    <form onSubmit={handleSearch} className="semantic-search-bar">
      <input
        type="text"
        placeholder="Search emails..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="search-input"
      />
      <button type="submit" className="search-button">Search</button>
    </form>
  );
};

export default SemanticSearchBar;
