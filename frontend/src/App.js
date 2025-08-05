import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import JobDetails from './pages/JobDetails';
import CVUpload from './pages/CVUpload';
import SavedJobs from './pages/SavedJobs';
import authService from './api/auth.service';

function App() {
  const currentUser = authService.getCurrentUser();

  const handleLogout = () => {
    authService.logout();
    window.location.reload();
  };

  return (
    <Router>
      <nav className="bg-white shadow-md">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center py-4">
            <Link to="/" className="text-2xl font-bold text-gray-800">JobGenie</Link>
            <div className="flex items-center space-x-4">
              <Link to="/cv-upload" className="text-gray-800 hover:text-blue-500 font-medium">
                🔍 AI Job Match
              </Link>
              {currentUser && (
                <Link to="/saved-jobs" className="text-gray-800 hover:text-purple-500 font-medium">
                  💾 Saved Jobs
                </Link>
              )}
              <Link to="/" className="text-gray-800 hover:text-blue-500">
                📋 All Jobs
              </Link>
              {currentUser ? (
                <>
                  <span className="text-gray-600">Welcome, {currentUser.username}</span>
                  <button onClick={handleLogout} className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors">
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link to="/login" className="text-gray-800 hover:text-blue-500">Login</Link>
                  <Link to="/register" className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors">
                    Register
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="bg-gray-50 min-h-screen">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/cv-upload" element={<CVUpload />} />
          <Route path="/saved-jobs" element={<SavedJobs />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/jobs/:id" element={<JobDetails />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;
