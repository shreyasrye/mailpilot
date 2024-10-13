import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import SemanticSearch from './pages/SemanticSearch';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/search" element={<SemanticSearch />} />
        {/* Other routes */}
      </Routes>
    </Router>
  );
}

export default App;
