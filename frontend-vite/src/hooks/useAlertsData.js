import { useEffect, useState } from "react";
import { fetchAlerts } from "../services/api";

export default function useAlertsData() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const data = await fetchAlerts();
        setAlerts(data);
      } catch (err) {
        setError(err?.message || "Unable to load alerts");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return { alerts, loading, error };
}
