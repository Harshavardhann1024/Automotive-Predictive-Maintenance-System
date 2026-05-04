import { useEffect, useState } from "react";
import { fetchVehicles } from "../services/api";

export default function useVehiclesData() {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const data = await fetchVehicles();
        setVehicles(data);
      } catch (err) {
        setError(err?.message || "Unable to load vehicle data");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return { vehicles, loading, error };
}
