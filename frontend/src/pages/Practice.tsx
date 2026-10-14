// ============================================================
// Cube.com Frontend - Practice & Timer Page
// ============================================================

import React, { useEffect, useState } from "react";
import Timer from "../components/timer/Timer";
import { lessonService } from "../services/lessonService";
import { userService } from "../services/userService";

const Practice: React.FC = () => {
  const [scramble, setScramble] = useState<string>("Chargement du mélange...");
  const [recentSolves, setRecentSolves] = useState<number[]>([]);
  const [isLogged, setIsLogged] = useState(false);

  const fetchNewScramble = async () => {
    try {
      const res = await lessonService.getRandomScramble();
      setScramble(res.data.scramble);
    } catch {
      setScramble("R U R' U' D R2 U' L D2 R B2 D2 R' F2 R2 D2 B2 U2");
    }
  };

  useEffect(() => {
    setIsLogged(!!localStorage.getItem("access_token"));
    fetchNewScramble();
  }, []);

  const handleSolve = async (timeMs: number) => {
    setRecentSolves((prev) => [timeMs, ...prev].slice(0, 5));
    if (isLogged) {
      try {
        await userService.recordSolve(timeMs, scramble);
      } catch (e) {
        console.warn("Could not save solve to server", e);
      }
    }
    fetchNewScramble();
  };

  return (
    <div style={styles.container}>
      <header style={styles.scrambleCard}>
        <div style={styles.scrambleLabel}>MÉLANGE (SCRAMBLE)</div>
        <div style={styles.scrambleText}>{scramble}</div>
        <button onClick={fetchNewScramble} style={styles.refreshBtn}>
          🔄 Nouveau mélange
        </button>
      </header>

      <div style={styles.timerWrapper}>
        <Timer onSolve={handleSolve} />
      </div>

      <div style={styles.historyCard}>
        <h3 style={styles.historyTitle}>Derniers temps</h3>
        {recentSolves.length === 0 ? (
          <p style={{ color: "#7e8a9b", margin: 0 }}>Effectuez un solve pour voir vos temps.</p>
        ) : (
          <div style={styles.solveList}>
            {recentSolves.map((ms, index) => (
              <span key={index} style={styles.solvePill}>
                {(ms / 1000).toFixed(2)}s
              </span>
            ))}
          </div>
        )}
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
    textAlign: "center",
  },
  scrambleCard: {
    backgroundColor: "#16213e",
    border: "1px solid #1f4068",
    borderRadius: "12px",
    padding: "1.5rem",
    marginBottom: "2.5rem",
  },
  scrambleLabel: {
    fontSize: "0.85rem",
    color: "#00d4ff",
    fontWeight: "bold",
    marginBottom: "0.5rem",
    letterSpacing: "0.05em",
  },
  scrambleText: {
    fontSize: "1.3rem",
    fontFamily: "monospace",
    color: "#ffffff",
    marginBottom: "1rem",
    lineHeight: 1.4,
  },
  refreshBtn: {
    background: "none",
    border: "1px solid #233756",
    color: "#a0a0b0",
    padding: "0.4rem 1rem",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "0.9rem",
  },
  timerWrapper: {
    marginBottom: "3rem",
  },
  historyCard: {
    backgroundColor: "#16213e",
    border: "1px solid #1f4068",
    borderRadius: "12px",
    padding: "1.5rem",
    maxWidth: "500px",
    margin: "0 auto",
  },
  historyTitle: {
    margin: "0 0 1rem 0",
    fontSize: "1.1rem",
    color: "#a0a0b0",
  },
  solveList: {
    display: "flex",
    gap: "0.75rem",
    justifyContent: "center",
    flexWrap: "wrap",
  },
  solvePill: {
    backgroundColor: "#0d1527",
    border: "1px solid #00d4ff",
    color: "#00d4ff",
    padding: "0.4rem 0.8rem",
    borderRadius: "6px",
    fontFamily: "monospace",
    fontWeight: "bold",
  },
};

export default Practice;

