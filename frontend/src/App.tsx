import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import PatientsPage from './pages/PatientsPage'
import ReportsPage from './pages/ReportsPage'
import HomePage from './pages/HomePage'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-container">
            <Link to="/" className="nav-logo">
              Lab2FHIR
            </Link>
            <div className="nav-links">
              <Link to="/" className="nav-link">Home</Link>
              <Link to="/patients" className="nav-link">Patients</Link>
              <Link to="/reports" className="nav-link">Reports</Link>
            </div>
          </div>
        </nav>
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/patients" element={<PatientsPage />} />
            <Route path="/reports" element={<ReportsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
