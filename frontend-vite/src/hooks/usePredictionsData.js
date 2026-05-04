import { useEffect, useState } from "react";
import { fetchVehicles } from "../services/api";

export default function usePredictionsData() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const vehicles = await fetchVehicles();
        const enriched = vehicles.map((vehicle) => ({
          id: vehicle.id,
          vehicle: vehicle.name,
          failure_prob: 100 - vehicle.health_score,
          suggested_action: vehicle.risk_level === "High" ? "Immediate service" : "Monitor"
        }));
        setPredictions(enriched);
      } catch (err) {
        setError(err?.message || "Unable to load predictions");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return { predictions, loading, error };
}
