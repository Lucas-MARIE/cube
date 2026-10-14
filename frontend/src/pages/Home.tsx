// ============================================================
// Cube.com Frontend - Home Page
// Landing page welcoming users and presenting key features.
// ============================================================

import React from "react";
import { Link } from "react-router-dom";

const Home: React.FC = () => {
  return (
    <div style={styles.container}>
      <header style={styles.hero}>
        <h1 style={styles.title}>Bienvenue sur Cube.com 🧊</h1>
        <p style={styles.subtitle}>
          La plateforme d'apprentissage et de compétition Rubik's Cube style Chess.com
        </p>
        <div style={styles.ctaGroup}>
          <Link to="/practice" style={styles.primaryButton}>
            ⏱️ S'entraîner au Chrono
          </Link>
          <Link to="/lessons" style={styles.secondaryButton}>
            📚 Suivre les Leçons
          </Link>
        </div>
      </header>

      <section style={styles.grid}>
        <div style={styles.card}>
          <div style={styles.cardIcon}>👤</div>
          <h2 style={styles.cardTitle}>Profil & Progression</h2>
          <p style={styles.cardText}>
            Suivez vos temps de résolution, votre Personal Best (PB), et vos moyennes AO5/AO12 calculées en temps réel.
          </p>
        </div>

        <div style={styles.card}>
          <div style={styles.cardIcon}>📖</div>
          <h2 style={styles.cardTitle}>Méthode Fridrich (CFOP)</h2>
          <p style={styles.cardText}>
            Accédez à toutes les formules F2L, OLL et PLL avec visualisations interactives et scrambles dédiés.
          </p>
        </div>

        <div style={styles.card}>
          <div style={styles.cardIcon}>⚔️</div>
          <h2 style={styles.cardTitle}>Duels & Matchmaking</h2>
          <p style={styles.cardText}>
            Défiez d'autres cubeurs en duel 1v1 avec le même mélange de départ et un classement Elo dynamique.
          </p>
        </div>
      </section>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    maxWidth: "1100px",
    margin: "0 auto",
    padding: "2rem",
    fontFamily: "system-ui, -apple-system, sans-serif",
    color: "#e0e0e0",
  },
  hero: {
    textAlign: "center",
    padding: "3rem 1rem",
    background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
    borderRadius: "16px",
    marginBottom: "3rem",
    border: "1px solid #0f3460",
  },
  title: {
    fontSize: "2.8rem",
    color: "#00d4ff",
    marginBottom: "1rem",
  },
  subtitle: {
    fontSize: "1.2rem",
    color: "#a0a0b0",
    maxWidth: "600px",
    margin: "0 auto 2rem auto",
    lineHeight: 1.6,
  },
  ctaGroup: {
    display: "flex",
    gap: "1rem",
    justifyContent: "center",
    flexWrap: "wrap",
  },
  primaryButton: {
    backgroundColor: "#00d4ff",
    color: "#0a0a14",
    padding: "0.8rem 1.6rem",
    borderRadius: "8px",
    textDecoration: "none",
    fontWeight: "bold",
    fontSize: "1.05rem",
  },
  secondaryButton: {
    backgroundColor: "transparent",
    color: "#00d4ff",
    border: "2px solid #00d4ff",
    padding: "0.8rem 1.6rem",
    borderRadius: "8px",
    textDecoration: "none",
    fontWeight: "bold",
    fontSize: "1.05rem",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
    gap: "2rem",
  },
  card: {
    backgroundColor: "#16213e",
    padding: "2rem",
    borderRadius: "12px",
    border: "1px solid #1f4068",
  },
  cardIcon: {
    fontSize: "2.5rem",
    marginBottom: "1rem",
  },
  cardTitle: {
    fontSize: "1.3rem",
    color: "#ffffff",
    marginBottom: "0.5rem",
  },
  cardText: {
    color: "#a0a0b0",
    lineHeight: 1.5,
  },
};

export default Home;

