// ============================================================
// Cube.com Frontend - Navbar Component
// Top navigation bar with links to all main pages.
// ============================================================

import { Link, useNavigate } from "react-router-dom";

/**
 * Navigation bar component displayed at the top of every page.
 * Shows different links based on authentication state.
 */
function Navbar() {
  const navigate = useNavigate();
  const isLoggedIn = !!localStorage.getItem("access_token");

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/login");
  };

  return (
    <nav className="navbar" style={styles.navbar}>
      {/* Brand */}
      <Link to="/" style={styles.brand}>
        🧊 Cube.com
      </Link>

      {/* Navigation Links */}
      <div style={styles.links}>
        <Link to="/" style={styles.link}>
          Home
        </Link>
        <Link to="/lessons" style={styles.link}>
          Lessons
        </Link>
        <Link to="/practice" style={styles.link}>
          Practice
        </Link>

        {isLoggedIn ? (
          <>
            <Link to="/profile" style={styles.link}>
              Profile
            </Link>
            <button onClick={handleLogout} style={styles.button}>
              Logout
            </button>
          </>
        ) : (
          <Link to="/login" style={styles.link}>
            Login
          </Link>
        )}
      </div>
    </nav>
  );
}

// Inline styles (replace with Tailwind/CSS modules in production)
const styles: Record<string, React.CSSProperties> = {
  navbar: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "1rem 2rem",
    backgroundColor: "#1a1a2e",
    color: "#fff",
  },
  brand: {
    fontSize: "1.5rem",
    fontWeight: "bold",
    color: "#00d4ff",
    textDecoration: "none",
  },
  links: {
    display: "flex",
    gap: "1.5rem",
    alignItems: "center",
  },
  link: {
    color: "#e0e0e0",
    textDecoration: "none",
    fontSize: "1rem",
  },
  button: {
    background: "transparent",
    border: "1px solid #e0e0e0",
    color: "#e0e0e0",
    padding: "0.4rem 1rem",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "1rem",
  },
};

export default Navbar;
