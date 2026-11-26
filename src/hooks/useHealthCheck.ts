import { useState, useEffect, useCallback } from 'react';
import { checkHealth } from '../services/api';
import type { HealthStatus } from '../types/api';

/**
 * Custom hook to poll the backend health-check endpoint.
 */
export function useHealthCheck(intervalMs = 30000) {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      const data = await checkHealth();
      setHealth(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setHealth(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const timer = setInterval(refresh, intervalMs);
    return () => clearInterval(timer);
  }, [refresh, intervalMs]);

  return { health, error, loading, refresh };
}
