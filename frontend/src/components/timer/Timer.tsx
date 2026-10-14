// ============================================================
// Cube.com Frontend - Timer Component
// Stopwatch-style timer for tracking Rubik's Cube solve times.
// ============================================================

import { useState, useRef, useCallback } from "react";

interface TimerProps {
  onSolve?: (timeMs: number) => void;
}

/**
 * Timer component with start, stop, and reset functionality.
 * Displays elapsed time in mm:ss.ms format.
 */
function Timer({ onSolve }: TimerProps) {
  const [elapsedMs, setElapsedMs] = useState<number>(0);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const startTimeRef = useRef<number>(0);

  /**
   * Start the timer. Records the start timestamp and begins
   * updating the elapsed time every 10ms.
   */
  const start = useCallback(() => {
    if (isRunning) return;

    startTimeRef.current = Date.now() - elapsedMs;
    setIsRunning(true);

    intervalRef.current = setInterval(() => {
      setElapsedMs(Date.now() - startTimeRef.current);
    }, 10);
  }, [isRunning, elapsedMs]);

  /**
   * Stop the timer and record the final elapsed time.
   */
  const stop = useCallback(() => {
    if (!isRunning) return;

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    const finalMs = Date.now() - startTimeRef.current;
    setElapsedMs(finalMs);
    setIsRunning(false);
    if (onSolve) {
      onSolve(finalMs);
    }
  }, [isRunning, onSolve]);

  /**
   * Reset the timer back to zero.
   */
  const reset = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setElapsedMs(0);
    setIsRunning(false);
  }, []);

  /**
   * Format milliseconds into mm:ss.ms display string.
   */
  const formatTime = (ms: number): string => {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    const centiseconds = Math.floor((ms % 1000) / 10);

    return `${minutes.toString().padStart(2, "0")}:${seconds
      .toString()
      .padStart(2, "0")}.${centiseconds.toString().padStart(2, "0")}`;
  };

  return (
    <div style={styles.container}>
      {/* Time Display */}
      <div style={styles.display}>{formatTime(elapsedMs)}</div>

      {/* Control Buttons */}
      <div style={styles.controls}>
        {!isRunning ? (
          <button onClick={start} style={{ ...styles.button, ...styles.startBtn }}>
            Start
          </button>
        ) : (
          <button onClick={stop} style={{ ...styles.button, ...styles.stopBtn }}>
            Stop
          </button>
        )}
        <button
          onClick={reset}
          style={{ ...styles.button, ...styles.resetBtn }}
          disabled={isRunning}
        >
          Reset
        </button>
      </div>
    </div>
  );
}

// Inline styles (replace with Tailwind/CSS modules in production)
const styles: Record<string, React.CSSProperties> = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "1.5rem",
    padding: "2rem",
  },
  display: {
    fontFamily: "'Courier New', monospace",
    fontSize: "4rem",
    fontWeight: "bold",
    color: "#00d4ff",
    textShadow: "0 0 20px rgba(0, 212, 255, 0.3)",
  },
  controls: {
    display: "flex",
    gap: "1rem",
  },
  button: {
    padding: "0.75rem 2rem",
    fontSize: "1.1rem",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontWeight: "bold",
    transition: "opacity 0.2s",
  },
  startBtn: {
    backgroundColor: "#00c853",
    color: "#fff",
  },
  stopBtn: {
    backgroundColor: "#ff1744",
    color: "#fff",
  },
  resetBtn: {
    backgroundColor: "#616161",
    color: "#fff",
  },
};

export default Timer;
