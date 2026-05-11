import React, { useEffect, useMemo, useState } from "react";

interface Incident {
  id: number;
  incident_type: string;
  confidence: number;
  severity: string;
  latitude: number | null;
  longitude: number | null;
  detected_at: string;
  relief_amount: string | null;
  estimated_affected_area: number | null;
  estimated_affected_population: number | null;
  image_url: string | null;
  video_url: string | null;
}

interface Props {
  apiBase: string;
  refreshKey?: number;
}

const titleCase = (value: string) =>
  value.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

export const IncidentList: React.FC<Props> = ({ apiBase, refreshKey }) => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/incidents/`, {
        credentials: "include",
      });
      const data = await res.json();
      setIncidents(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, [refreshKey]);

  const totals = useMemo(() => {
    const relief = incidents.reduce(
      (sum, item) => sum + Number.parseFloat(item.relief_amount || "0"),
      0,
    );
    const critical = incidents.filter((item) => item.severity === "critical").length;

    return { relief, critical };
  }, [incidents]);

  const formatCurrency = (amount: string | number | null) => {
    if (amount === null || amount === "") return "--";
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(typeof amount === "number" ? amount : parseFloat(amount));
  };

  return (
    <div>
      <div className="panel-header incident-header">
        <div>
          <span className="eyebrow">Incident registry</span>
          <h2>Recent Incidents</h2>
        </div>
        <button className="button secondary" onClick={load} disabled={loading}>
          {loading ? "Refreshing" : "Refresh"}
        </button>
      </div>

      <div className="summary-row">
        <div className="summary-card">
          <span className="summary-value">{incidents.length}</span>
          <span className="summary-label">Total incidents</span>
        </div>
        <div className="summary-card">
          <span className="summary-value">{totals.critical}</span>
          <span className="summary-label">Critical cases</span>
        </div>
        <div className="summary-card">
          <span className="summary-value">{formatCurrency(totals.relief)}</span>
          <span className="summary-label">Estimated relief</span>
        </div>
      </div>

      <div className="table">
        {incidents.length === 0 ? (
          <div className="empty-state">
            <h3>No incidents recorded</h3>
            <p>New detections will appear here after a successful analysis.</p>
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Type</th>
                <th>Severity</th>
                <th>Confidence</th>
                <th>Affected Area</th>
                <th>Population</th>
                <th>Relief</th>
                <th>Detected</th>
              </tr>
            </thead>
            <tbody>
              {incidents.map((incident) => (
                <tr key={incident.id}>
                  <td>
                    <span className="incident-type">
                      {titleCase(incident.incident_type)}
                    </span>
                  </td>
                  <td>
                    <span className={`severity-badge severity-${incident.severity}`}>
                      {titleCase(incident.severity)}
                    </span>
                  </td>
                  <td>{(incident.confidence * 100).toFixed(1)}%</td>
                  <td>
                    {incident.estimated_affected_area
                      ? `${incident.estimated_affected_area.toFixed(2)} km2`
                      : "--"}
                  </td>
                  <td>
                    {incident.estimated_affected_population
                      ? incident.estimated_affected_population.toLocaleString()
                      : "--"}
                  </td>
                  <td className="relief-cell">
                    {formatCurrency(incident.relief_amount)}
                  </td>
                  <td>{new Date(incident.detected_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
