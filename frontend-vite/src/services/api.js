import { apiClient } from "./authApi";
import {
  mockVehicles,
  mockAlerts,
  mockDashboardSummary,
  mockCharts,
  mockRecommendations,
  mockPredictions,
  mockServiceTasks,
  mockManufacturingInsights,
  mockReports
} from "./mockData";

const safeResponse = (data, fallback) => {
  if (!data || (Array.isArray(data) && data.length === 0)) {
    return fallback;
  }
  return data;
};

export async function fetchDashboardSummary() {
  try {
    const res = await apiClient.get(`/dashboard/api/dashboard/summary`);
    return safeResponse(res.data, mockDashboardSummary);
  } catch (error) {
    console.warn("Dashboard summary fallback to mock data", error?.message);
    return mockDashboardSummary;
  }
}

export async function fetchVehicles() {
  try {
    const res = await apiClient.get(`/vehicles/`);
    return safeResponse(res.data, mockVehicles);
  } catch (error) {
    console.warn("Vehicles fallback to mock data", error?.message);
    return mockVehicles;
  }
}

export async function createVehicle(vehicleData) {
  try {
    const res = await apiClient.post(`/vehicles/`, vehicleData);
    return res.data;
  } catch (error) {
    console.warn("Failed to create vehicle on backend, creating locally", error?.message);
    // Fallback: just return it with a fake ID
    return {
      id: "v" + Math.random().toString(36).substr(2, 9),
      ...vehicleData,
      health_score: vehicleData.health_score || 100,
      risk_level: "Low",
      status: "Active"
    };
  }
}

export async function fetchVehicleById(vehicleId) {
  try {
    const res = await apiClient.get(`/viz/vehicle-overview/${vehicleId}`);
    return safeResponse(res.data, mockVehicles.find((v) => v.id === vehicleId));
  } catch (error) {
    console.warn("Vehicle by id fallback to mock data", error?.message);
    return mockVehicles.find((v) => v.id === vehicleId) || null;
  }
}

export async function fetchAlerts() {
  try {
    const res = await apiClient.get(`/alerts`);
    return safeResponse(res.data, mockAlerts);
  } catch (error) {
    console.warn("Alerts fallback to mock data", error?.message);
    return mockAlerts;
  }
}

export async function resolveAlert(alertId) {
  try {
    const res = await apiClient.patch(`/alerts/${alertId}/resolve`);
    return res.data;
  } catch (error) {
    console.warn("Resolve alert fallback", error?.message);
    return { success: true, id: alertId, status: "Resolved" };
  }
}

export async function acknowledgeAlert(alertId) {
  try {
    const res = await apiClient.patch(`/alerts/${alertId}/acknowledge`);
    return res.data;
  } catch (error) {
    console.warn("Acknowledge alert fallback", error?.message);
    return { success: true, id: alertId, status: "Acknowledged" };
  }
}

export async function fetchSystemStatus() {
  try {
    const res = await apiClient.get(`/`);
    return {
      healthy: true,
      message: res.data?.message || "API available"
    };
  } catch {
    return {
      healthy: false,
      message: "Backend unavailable - running on mock data"
    };
  }
}

export function getChartData() {
  return mockCharts;
}

export function getRecommendations() {
  return mockRecommendations;
}

export function getPredictions() {
  return mockPredictions;
}

export function getServiceTasks() {
  return mockServiceTasks;
}

export function getManufacturingInsights() {
  return mockManufacturingInsights;
}

// Reports
export async function downloadDashboardReport() {
  const res = await apiClient.get(`/dashboard/reports`, { responseType: 'blob' });
  triggerBrowserDownload(res.data, 'executive_dashboard_report.pdf');
  return res.data;
}

export async function generateReport(format, type) {
  const res = await apiClient.get(`/reports/generate`, {
    params: { format, type },
    responseType: 'blob' 
  });
  const ext = format === 'pdf' ? 'pdf' : 'csv';
  triggerBrowserDownload(res.data, `fleet_report_${type}.${ext}`);
  return res.data;
}

export async function exportDataZip() {
  const res = await apiClient.get(`/reports/export/zip`, { responseType: 'blob' });
  triggerBrowserDownload(res.data, 'export_data.zip');
  return res.data;
}

function triggerBrowserDownload(blob, filename) {
  const url = window.URL.createObjectURL(new Blob([blob]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.parentNode.removeChild(link);
}

export function getReports() {
  return mockReports;
}

// ─── ML Predictions API ───────────────────────────────────
export async function getPrediction(sensorData, { explain = false } = {}) {
  try {
    const params = explain ? { explain: true } : {};
    const res = await apiClient.post(`/predictions/predict`, sensorData, { params });
    return res.data;
  } catch (error) {
    console.warn("Prediction API error", error?.message);
    throw error;
  }
}

export async function getPredictionHistory(params = {}) {
  try {
    const res = await apiClient.get(`/predictions/history`, { params });
    return res.data;
  } catch (error) {
    console.warn("Prediction history fallback", error?.message);
    return [];
  }
}

export async function getPredictionStats(hours = 24) {
  try {
    const res = await apiClient.get(`/predictions/stats`, { params: { hours } });
    return res.data;
  } catch (error) {
    console.warn("Prediction stats fallback", error?.message);
    return {
      total_predictions: 0,
      high_risk_count: 0,
      medium_risk_count: 0,
      low_risk_count: 0,
      avg_failure_probability: 0,
      recent_failure_rate: 0,
    };
  }
}

export async function getModelInfo() {
  try {
    const res = await apiClient.get(`/predictions/model-info`);
    return res.data;
  } catch (error) {
    console.warn("Model info fallback", error?.message);
    return null;
  }
}

// ─── Service Schedules API ────────────────────────────────

export async function fetchServiceSchedules(params = {}) {
  try {
    const res = await apiClient.get(`/service-schedules/`, { params });
    return res.data;
  } catch (error) {
    console.warn("Service schedules fallback", error?.message);
    return [];
  }
}

export async function fetchServiceScheduleStats() {
  try {
    const res = await apiClient.get(`/service-schedules/stats`);
    return res.data;
  } catch (error) {
    console.warn("Schedule stats fallback", error?.message);
    return {
      total_schedules: 0,
      pending_count: 0,
      scheduled_count: 0,
      in_progress_count: 0,
      completed_count: 0,
      cancelled_count: 0,
      high_priority_count: 0,
      medium_priority_count: 0,
      low_priority_count: 0,
      upcoming_24h: 0,
      overdue_count: 0,
      urgent_services: 0,
      inspection_services: 0,
      repair_services: 0,
    };
  }
}

export async function fetchSchedulesByVehicle(vehicleId, params = {}) {
  try {
    const res = await apiClient.get(`/service-schedules/vehicle/${vehicleId}`, { params });
    return res.data;
  } catch (error) {
    console.warn("Vehicle schedules fallback", error?.message);
    return [];
  }
}

export async function updateServiceSchedule(scheduleId, updateData) {
  try {
    const res = await apiClient.patch(`/service-schedules/${scheduleId}`, updateData);
    return res.data;
  } catch (error) {
    console.warn("Update schedule error", error?.message);
    throw error;
  }
}

export async function cancelServiceSchedule(scheduleId) {
  try {
    const res = await apiClient.delete(`/service-schedules/${scheduleId}`);
    return res.data;
  } catch (error) {
    console.warn("Cancel schedule error", error?.message);
    throw error;
  }
}

