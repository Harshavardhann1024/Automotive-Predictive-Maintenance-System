// Seed realistic mock data across the application

export const dashboardKPIs = {
  totalVehicles: 3240,
  activeAlerts: 142,
  avgFleetHealth: 88,
  highRiskVehicles: 18
};

export const fleetHealthTrend = [
  { month: 'Oct', health: 85, threshold: 80 },
  { month: 'Nov', health: 86, threshold: 80 },
  { month: 'Dec', health: 87, threshold: 80 },
  { month: 'Jan', health: 89, threshold: 80 },
  { month: 'Feb', health: 88, threshold: 80 },
  { month: 'Mar', health: 88, threshold: 80 },
];

export const failRiskTrend = [
  { month: 'Oct', risk: 15 },
  { month: 'Nov', risk: 14 },
  { month: 'Dec', risk: 18 },
  { month: 'Jan', risk: 12 },
  { month: 'Feb', risk: 10 },
  { month: 'Mar', risk: 12 },
];

export const vehiclesData = [
  { id: 'V-1001', regNumber: 'MH 12 AB 1234', model: 'Mahindra Thar', mileage: 45200, healthScore: 92, riskTier: 'Low', status: 'Active', target: 90 },
  { id: 'V-1002', regNumber: 'KA 03 XY 9876', model: 'Tata Nexon EV', mileage: 12400, healthScore: 98, riskTier: 'Low', status: 'Active', target: 90 },
  { id: 'V-1003', regNumber: 'DL 01 BC 4321', model: 'Toyota Innova', mileage: 84000, healthScore: 65, riskTier: 'High', status: 'Maintenance', target: 90 },
  { id: 'V-1004', regNumber: 'TN 09 LM 5678', model: 'Hyundai Creta', mileage: 36000, healthScore: 88, riskTier: 'Medium', status: 'Active', target: 90 },
  { id: 'V-1005', regNumber: 'UP 16 ER 1122', model: 'Ford Ranger', mileage: 112000, healthScore: 45, riskTier: 'Critical', status: 'Inactive', target: 90 },
  { id: 'V-1006', regNumber: 'MH 14 PQ 8899', model: 'Volvo FH16', mileage: 220500, healthScore: 78, riskTier: 'Medium', status: 'Active', target: 90 },
  { id: 'V-1007', regNumber: 'GJ 05 RS 3344', model: 'Tata Ace EV', mileage: 8500, healthScore: 96, riskTier: 'Low', status: 'Active', target: 90 },
  { id: 'V-1008', regNumber: 'HR 26 ZX 7755', model: 'Ashok Leyland Dost', mileage: 54000, healthScore: 82, riskTier: 'Low', status: 'Active', target: 90 },
];

export const recentAlerts = [
  { id: 'ALT-4892', vehicle: 'Toyota Innova (DL 01 BC 4321)', type: 'Brake Pad Wear', severity: 'Critical', time: '10 mins ago', status: 'Open' },
  { id: 'ALT-4891', vehicle: 'Volvo FH16 (MH 14 PQ 8899)', type: 'Engine Temp High', severity: 'High', time: '1 hr ago', status: 'Open' },
  { id: 'ALT-4890', vehicle: 'Ford Ranger (UP 16 ER 1122)', type: 'Transmission Fluid', severity: 'High', time: '2 hrs ago', status: 'In Progress' },
  { id: 'ALT-4889', vehicle: 'Hyundai Creta (TN 09 LM 5678)', type: 'Tire Pressure Low', severity: 'Low', time: '5 hrs ago', status: 'Resolved' },
  { id: 'ALT-4888', vehicle: 'Mahindra Thar (MH 12 AB 1234)', type: 'Battery Voltage Drop', severity: 'Medium', time: '1 day ago', status: 'Resolved' },
];

export const predictiveInsights = [
  { id: 1, component: 'Transmission Unit', probability: 87, timeToFailure: '3-5 days', vehicleId: 'V-1005', model: 'Ford Ranger', costImpact: '$2,400' },
  { id: 2, component: 'Brake Calipers', probability: 92, timeToFailure: '1-2 days', vehicleId: 'V-1003', model: 'Toyota Innova', costImpact: '$450' },
  { id: 3, component: 'Coolant Pump', probability: 76, timeToFailure: '7-10 days', vehicleId: 'V-1006', model: 'Volvo FH16', costImpact: '$850' },
];

export const manufacturingDefects = [
  { batchId: 'BCH-2025-X1', component: 'Alternator Assemblies', defectRate: '4.2%', issues: 145, status: 'Investigation', severity: 'High' },
  { batchId: 'BCH-2025-Y2', component: 'EV Battery Cells (NMC)', defectRate: '1.8%', issues: 32, status: 'Monitoring', severity: 'Medium' },
  { batchId: 'BCH-2025-Z4', component: 'Suspension Struts', defectRate: '0.4%', issues: 12, status: 'Resolved', severity: 'Low' },
];

export const serviceQueue = [
  { jobId: 'JOB-9021', vehicle: 'DL 01 BC 4321', task: 'Brake System Overhaul', estimatedTime: '4 hrs', technician: 'Rahul S.', status: 'Ongoing' },
  { jobId: 'JOB-9022', vehicle: 'UP 16 ER 1122', task: 'Transmission Diagnostics', estimatedTime: '2 hrs', technician: 'Amit V.', status: 'Waiting' },
  { jobId: 'JOB-9023', vehicle: 'MH 14 PQ 8899', task: 'Radiator Flush', estimatedTime: '1.5 hrs', technician: 'Vikram K.', status: 'Scheduled' },
];

export const componentHealthData = [
  { name: 'Engine', health: 85 },
  { name: 'Transmission', health: 65 },
  { name: 'Brakes', health: 40 },
  { name: 'Battery', health: 92 },
  { name: 'Suspension', health: 78 },
];

export const vehicleSensorData = [
  { time: '08:00', temp: 85, vibration: 2.1 },
  { time: '09:00', temp: 88, vibration: 2.3 },
  { time: '10:00', temp: 95, vibration: 2.6 },
  { time: '11:00', temp: 105, vibration: 3.4 }, /* Anomaly */
  { time: '12:00', temp: 110, vibration: 4.2 }, /* Critical */
  { time: '13:00', temp: 85, vibration: 2.0 },
];
