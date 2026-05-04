export const mockVehicles = [
  {
    id: "v1",
    name: "Mahindra Thar",
    model: "Thar 4x4 Adventure",
    registration_number: "MH12AB3456",
    health_score: 91,
    risk_level: "Low",
    alerts_count: 1,
    status: "Active",
    mileage: 42000,
    location: "Pune, MH",
    fuel_level: 64,
    last_maintenance: "2025-12-08T09:25:00.000Z"
  },
  {
    id: "v2",
    name: "Tata Nexon EV",
    model: "Nexon EV Max",
    registration_number: "KA05CD7890",
    health_score: 84,
    risk_level: "Medium",
    alerts_count: 3,
    status: "Active",
    mileage: 59000,
    location: "Bengaluru, KA",
    fuel_level: 78,
    last_maintenance: "2025-11-20T08:50:00.000Z"
  },
  {
    id: "v3",
    name: "Toyota Innova",
    model: "Crysta 2.8",
    registration_number: "DL1AF1234",
    health_score: 73,
    risk_level: "High",
    alerts_count: 6,
    status: "In Maintenance",
    mileage: 98000,
    location: "New Delhi, DL",
    fuel_level: 41,
    last_maintenance: "2025-11-01T10:20:00.000Z"
  },
  {
    id: "v4",
    name: "Hyundai Creta",
    model: "Creta SX(O)",
    registration_number: "HR26XY5678",
    health_score: 88,
    risk_level: "Low",
    alerts_count: 2,
    status: "Active",
    mileage: 63000,
    location: "Gurugram, HR",
    fuel_level: 55,
    last_maintenance: "2025-12-02T13:40:00.000Z"
  },
  {
    id: "v5",
    name: "Ford Ranger",
    model: "Raptor Limited",
    registration_number: "TN10QP4321",
    health_score: 65,
    risk_level: "High",
    alerts_count: 8,
    status: "Active",
    mileage: 110000,
    location: "Chennai, TN",
    fuel_level: 33,
    last_maintenance: "2025-10-15T11:10:00.000Z"
  },
  {
    id: "v6",
    name: "Volvo FH16",
    model: "FH16 750",
    registration_number: "WB09MN1122",
    health_score: 79,
    risk_level: "Medium",
    alerts_count: 4,
    status: "Active",
    mileage: 220000,
    location: "Kolkata, WB",
    fuel_level: 48,
    last_maintenance: "2025-12-11T07:30:00.000Z"
  }
];

export const mockAlerts = [
  {
    id: "a1",
    vehicle_id: "v3",
    severity: "Critical",
    status: "Active",
    message: "Engine oil pressure dropped below safe threshold.",
    created_at: "2026-03-22T14:18:00.000Z"
  },
  {
    id: "a2",
    vehicle_id: "v5",
    severity: "High",
    status: "Active",
    message: "Brake pad wear is at 92% and requires replacement.",
    created_at: "2026-03-21T09:10:00.000Z"
  },
  {
    id: "a3",
    vehicle_id: "v2",
    severity: "Medium",
    status: "Acknowledged",
    message: "Battery health dropped to 70% with charging anomalies.",
    created_at: "2026-03-20T11:35:00.000Z"
  },
  {
    id: "a4",
    vehicle_id: "v1",
    severity: "Low",
    status: "Resolved",
    message: "Tire pressure variance standard deviation exceeded.",
    created_at: "2026-03-19T19:05:00.000Z"
  },
  {
    id: "a5",
    vehicle_id: "v6",
    severity: "Medium",
    status: "Active",
    message: "Coolant temperature spikes detected in the last 2 hours.",
    created_at: "2026-03-20T17:45:00.000Z"
  }
];

export const mockCharts = {
  fleetHealth: [
    { day: "Mon", score: 82 },
    { day: "Tue", score: 80 },
    { day: "Wed", score: 83 },
    { day: "Thu", score: 78 },
    { day: "Fri", score: 84 },
    { day: "Sat", score: 86 },
    { day: "Sun", score: 85 }
  ],
  riskTrend: [
    { day: "Mon", highRisk: 5 },
    { day: "Tue", highRisk: 6 },
    { day: "Wed", highRisk: 7 },
    { day: "Thu", highRisk: 9 },
    { day: "Fri", highRisk: 8 },
    { day: "Sat", highRisk: 7 },
    { day: "Sun", highRisk: 6 }
  ],
  alertFrequency: [
    { day: "Mon", alerts: 11 },
    { day: "Tue", alerts: 14 },
    { day: "Wed", alerts: 10 },
    { day: "Thu", alerts: 16 },
    { day: "Fri", alerts: 12 },
    { day: "Sat", alerts: 9 },
    { day: "Sun", alerts: 13 }
  ],
  sensorData: [
    { ts: "08:00", rpm: 2800, temp: 86, vibration: 0.3 },
    { ts: "10:00", rpm: 3000, temp: 88, vibration: 0.34 },
    { ts: "12:00", rpm: 3300, temp: 90, vibration: 0.39 },
    { ts: "14:00", rpm: 3100, temp: 87, vibration: 0.35 },
    { ts: "16:00", rpm: 2950, temp: 85, vibration: 0.31 },
    { ts: "18:00", rpm: 2800, temp: 82, vibration: 0.27 }
  ]
};

export const mockDashboardSummary = {
  total_vehicles: mockVehicles.length,
  active_alerts: mockAlerts.filter((a) => a.status === "Active").length,
  average_health: Math.round(mockVehicles.reduce((sum, v) => sum + v.health_score, 0) / mockVehicles.length),
  high_risk_vehicles: mockVehicles.filter((v) => v.risk_level === "High").length,
  total_predictions: 3421,
  recent_readings: 12756,
  timestamp: new Date().toISOString()
};

export const mockRecommendations = [
  { id: "r1", title: "Schedule engine check for high-risk vehicles", due: "2026-03-28" },
  { id: "r2", title: "Run winter-grade coolant inspection", due: "2026-04-02" },
  { id: "r3", title: "Replace worn brake pads in Ford Ranger", due: "2026-03-26" }
];

export const mockPredictions = mockVehicles.map((v) => ({
  id: v.id,
  name: v.name,
  failure_probability: Math.max(8, Math.min(100, 100 - v.health_score + (v.alerts_count * 3))),
  next_service_due: "2026-04-15",
  suggested_action: v.risk_level === "High" ? "Service ASAP" : "Monitor"
}));

export const mockServiceTasks = [
  { id: "s1", vehicle: "Toyota Innova", type: "Brake inspection", priority: "High", eta: "2026-03-25", assigned_to: "Technician A" },
  { id: "s2", vehicle: "Ford Ranger", type: "Oil change", priority: "Medium", eta: "2026-03-25", assigned_to: "Technician B" },
  { id: "s3", vehicle: "Volvo FH16", type: "Coolant system check", priority: "High", eta: "2026-03-26", assigned_to: "Technician C" }
];

export const mockManufacturingInsights = [
  { id: "m1", label: "brake_actuator", issue: "Actuator leak", vehicles_impacted: 14, risk_score: 88 },
  { id: "m2", label: "battery_pack", issue: "Cell imbalance", vehicles_impacted: 10, risk_score: 72 },
  { id: "m3", label: "sensor_module", issue: "Calibration drift", vehicles_impacted: 18, risk_score: 66 }
];

export const mockReports = [
  { id: "rep1", title: "Weekly Fleet Status", type: "PDF", generated_on: "2026-03-24", status: "Ready" },
  { id: "rep2", title: "Alert Heatmap", type: "PDF", generated_on: "2026-03-22", status: "Ready" },
  { id: "rep3", title: "Service Performance", type: "Excel", generated_on: "2026-03-21", status: "Processing" }
];

