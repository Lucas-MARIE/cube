// ============================================================
// Cube.com Frontend - User Profile & Stats Page
// ============================================================

import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { userService } from "../services/userService";
import type { User, Stats } from "../types";

const Profile: React.FC = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/login");
      return;
    }

    Promise.all([userService.getProfile(), userService.getStats()])
      .then(([userRes, statsRes]) => {
        setUser(userRes.data);
        setStats(statsRes.data);
      })
      .catch(() => {
        localStorage.removeItem("access_token");
        navigate("/login");
      })
      .finally(() => setLoading(false));
  }, [navigate]);

  if (loading) {
    return <div style={{ color: "#fff", textAlign: "center", padding: "4rem" }}>Chargement du profil...</div>;
  }

  const formatMs = (ms?: number | null) => {
    if (!ms || ms <= 0) return "--";
    return (ms / 1000).toFixed(2) + "s";
  };

  return (
    <div style={styles.container}>
      <div style={styles.headerCard}>
        <div style={styles.avatar}>
          {user?.avatar_url ? (
            <img src={user.avatar_url} alt="Avatar" style={styles.avatarImg} />
          ) : (
            <span>🧊</span>
          )}
        </div>
        <div>
          <h1 style={styles.username}>{user?.username || "Cubeur"}</h1>
          <p style={styles.email}>{user?.email}</p>
          <p style={styles.meta}>Membre depuis : {new Date(user?.created_at || "").toLocaleDateString()}</p>
        </div>
      </div>

      <h2 style={styles.sectionTitle}>Statistiques de Speedcubing</h2>
      <div style={styles.statsGrid}>
        <div style={styles.statBox}>
          <div style={styles.statLabel}>Personal Best (PB)</div>
          <div style={styles.statValueHighlight}>{formatMs(stats?.personal_best)}</div>
        </div>
        <div style={styles.statBox}>
          <div style={styles.statLabel}>Average of 5 (AO5)</div>
          <div style={styles.statValue}>{formatMs(stats?.ao5)}</div>
        </div>
        <div style={styles.statBox}>
          <div style={styles.statLabel}>Average of 12 (AO12)</div>
          <div style={styles.statValue}>{formatMs(stats?.ao12)}</div>
        </div>
        <div style={styles.statBox}>
          <div style={styles.statLabel}>Total Résolutions</div>
          <div style={styles.statValue}>{stats?.total_solves ?? 0}</div>
        </div>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    maxWidth: "900px",
    margin: "0 auto",
    padding: "2rem",
    color: "#fff",
  },
  headerCard: {
    display: "flex",
    alignItems: "center",
    gap: "2rem",
    backgroundColor: "#16213e",
    border: "1px solid #1f4068",
    borderRadius: "12px",
    padding: "2rem",
    marginBottom: "2rem",
  },
  avatar: {
    width: "80px",
    height: "80px",
    borderRadius: "50%",
    backgroundColor: "#0f3460",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    fontSize: "2.5rem",
    overflow: "hidden",
  },
  avatarImg: {
    width: "100%",
    height: "100%",
    objectFit: "cover",
  },
  username: {
    margin: "0 0 0.3rem 0",
    fontSize: "1.8rem",
    color: "#00d4ff",
  },
  email: {
    margin: "0 0 0.5rem 0",
    color: "#a0a0b0",
  },
  meta: {
    margin: 0,
    fontSize: "0.85rem",
    color: "#7e8a9b",
  },
  sectionTitle: {
    fontSize: "1.4rem",
    marginBottom: "1rem",
    color: "#ffffff",
  },
  statsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: "1.5rem",
  },
  statBox: {
    backgroundColor: "#16213e",
    border: "1px solid #1f4068",
    borderRadius: "10px",
    padding: "1.5rem",
    textAlign: "center",
  },
  statLabel: {
    fontSize: "0.9rem",
    color: "#a0a0b0",
    marginBottom: "0.5rem",
  },
  statValue: {
    fontSize: "1.8rem",
    fontWeight: "bold",
    color: "#ffffff",
  },
  statValueHighlight: {
    fontSize: "1.8rem",
    fontWeight: "bold",
    color: "#00d4ff",
  },
};

export default Profile;

