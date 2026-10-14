// ============================================================
// Cube.com Frontend - Root App Component
// Defines the main application routes and layout.
// ============================================================

import { Routes, Route } from "react-router-dom";
import Navbar from "./components/common/Navbar";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import Lessons from "./pages/Lessons";
import Practice from "./pages/Practice";

/**
 * Root application component.
 * Renders the navigation bar and defines all page routes.
 */
function App() {
  return (
    <div className="app">
      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/lessons" element={<Lessons />} />
          <Route path="/practice" element={<Practice />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
