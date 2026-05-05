import React, { useState, useEffect, useCallback } from 'react';
import {
  Calendar,
  Clock,
  AlertTriangle,
  CheckCircle2,
  Wrench,
  Search,
  RefreshCw,
  Filter,
  ChevronDown,
  ChevronUp,
  XCircle,
  Zap,
  Shield,
  TrendingUp,
  Timer,
  ClipboardList,
  User,
  ArrowRight,
} from 'lucide-react';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Legend,
  BarChart, Bar,
} from 'recharts';
import {
  fetchServiceSchedules,
  fetchServiceScheduleStats,
  updateServiceSchedule,
  cancelServiceSchedule,
} from '../services/api';

// ─── Constants ───
const STATUS_OPTIONS = [
  { value: '', label: 'All Statuses' },
  { value: 'pending', label: 'Pending' },
  { value: 'scheduled', label: 'Scheduled' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
];

const PRIORITY_OPTIONS = [
  { value: '', label: 'All Priorities' },
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
];

const PIE_COLORS = ['#f59e0b', '#3b82f6', '#6366f1', '#10b981', '#94a3b8'];
const PRIORITY_COLORS = { high: '#dc2626', medium: '#d97706', low: '#059669' };
const STATUS_COLORS = {
  pending: '#f59e0b',
  scheduled: '#3b82f6',
  in_progress: '#6366f1',
  completed: '#10b981',
  cancelled: '#94a3b8',
};

// ─── Helper functions ───
function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

function formatRelativeTime(dateStr) {
  if (!dateStr) return '';
  const now = new Date();
  const target = new Date(dateStr);
  const diff = target - now;
  const hours = Math.floor(Math.abs(diff) / (1000 * 60 * 60));
  const days = Math.floor(hours / 24);

  if (diff < 0) return `${days > 0 ? days + 'd ' : ''}${hours % 24}h overdue`;
  if (days > 0) return `in ${days}d ${hours % 24}h`;
  return `in ${hours}h`;
}

function getServiceTypeIcon(type) {
  switch (type) {
    case 'urgent': return <Zap size={16} />;
    case 'repair': return <Wrench size={16} />;
    default: return <Search size={16} />;
  }
}

function getServiceTypeLabel(type) {
  switch (type) {
    case 'urgent': return 'Urgent Service';
    case 'repair': return 'Repair';
    case 'inspection': return 'Inspection';
    default: return type;
  }
}

// ─── Priority Alert Banner Component ───
function PriorityAlertBanner({ stats }) {
  const urgentCount = stats.high_priority_count + stats.overdue_count;
  if (urgentCount === 0) return null;

  return (
    <div className="sched-alert-banner">
      <div className="sched-alert-banner-content">
        <div className="sched-alert-banner-icon">
          <AlertTriangle size={22} />
        </div>
        <div className="sched-alert-banner-text">
          <strong>{urgentCount} vehicle{urgentCount !== 1 ? 's' : ''} need immediate attention</strong>
          <span>
            {stats.high_priority_count > 0 && `${stats.high_priority_count} high-priority`}
            {stats.high_priority_count > 0 && stats.overdue_count > 0 && ' · '}
            {stats.overdue_count > 0 && `${stats.overdue_count} overdue`}
          </span>
        </div>
      </div>
      <div className="sched-alert-banner-pulse" />
    </div>
  );
}

// ─── Service Card Component ───
function ServiceCard({ schedule, onStatusUpdate, onCancel }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const isOverdue = new Date(schedule.scheduled_date) < new Date() &&
    ['pending', 'scheduled'].includes(schedule.status);

  const handleStatusChange = async (newStatus) => {
    setIsUpdating(true);
    try {
      await onStatusUpdate(schedule.id, { status: newStatus });
    } finally {
      setIsUpdating(false);
    }
  };

  const nextStatusMap = {
    pending: 'scheduled',
    scheduled: 'in_progress',
    in_progress: 'completed',
  };
  const nextStatus = nextStatusMap[schedule.status];

  return (
    <div className={`sched-card sched-card-${schedule.priority} ${isOverdue ? 'sched-card-overdue' : ''}`}>
      <div className="sched-card-header" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="sched-card-left">
          <div className={`sched-card-icon sched-icon-${schedule.service_type}`}>
            {getServiceTypeIcon(schedule.service_type)}
          </div>
          <div className="sched-card-info">
            <div className="sched-card-title">
              {getServiceTypeLabel(schedule.service_type)}
              {isOverdue && <span className="sched-overdue-tag">OVERDUE</span>}
            </div>
            <div className="sched-card-meta">
              <span className="sched-card-vehicle">
                Vehicle: {schedule.vehicle_id ? schedule.vehicle_id.substring(0, 8) + '...' : 'Unassigned'}
              </span>
            </div>
          </div>
        </div>
        <div className="sched-card-right">
          <span className={`sched-priority-badge sched-priority-${schedule.priority}`}>
            {schedule.priority.toUpperCase()}
          </span>
          <span className={`sched-status-badge sched-status-${schedule.status}`}>
            {schedule.status.replace('_', ' ').toUpperCase()}
          </span>
          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </div>

      <div className="sched-card-body">
        <div className="sched-card-details-row">
          <div className="sched-detail-item">
            <Calendar size={14} />
            <span>{formatDate(schedule.scheduled_date)}</span>
          </div>
          <div className="sched-detail-item">
            <Timer size={14} />
            <span className={isOverdue ? 'text-danger' : ''}>{formatRelativeTime(schedule.scheduled_date)}</span>
          </div>
          {schedule.failure_probability != null && (
            <div className="sched-detail-item">
              <TrendingUp size={14} />
              <span>Failure: {(schedule.failure_probability * 100).toFixed(1)}%</span>
            </div>
          )}
        </div>
      </div>

      {isExpanded && (
        <div className="sched-card-expanded">
          <div className="sched-expanded-grid">
            <div className="sched-expanded-item">
              <span className="sched-expanded-label">Risk Level</span>
              <span className={`badge badge-${schedule.risk_level === 'High' || schedule.risk_level === 'HIGH' ? 'danger' : schedule.risk_level === 'Medium' || schedule.risk_level === 'MEDIUM' ? 'warning' : 'success'}`}>
                {schedule.risk_level || '—'}
              </span>
            </div>
            <div className="sched-expanded-item">
              <span className="sched-expanded-label">Created</span>
              <span>{formatDate(schedule.created_at)}</span>
            </div>
            {schedule.technician && (
              <div className="sched-expanded-item">
                <span className="sched-expanded-label">Technician</span>
                <span className="flex items-center gap-2"><User size={14} /> {schedule.technician}</span>
              </div>
            )}
            {schedule.notes && (
              <div className="sched-expanded-item sched-expanded-full">
                <span className="sched-expanded-label">Notes</span>
                <span>{schedule.notes}</span>
              </div>
            )}
          </div>

          {schedule.status !== 'completed' && schedule.status !== 'cancelled' && (
            <div className="sched-card-actions">
              {nextStatus && (
                <button
                  className="btn btn-primary sched-action-btn"
                  onClick={(e) => { e.stopPropagation(); handleStatusChange(nextStatus); }}
                  disabled={isUpdating}
                >
                  {isUpdating ? <RefreshCw size={14} className="animate-spin" /> : <ArrowRight size={14} />}
                  Mark as {nextStatus.replace('_', ' ')}
                </button>
              )}
              <button
                className="btn btn-secondary sched-action-btn"
                onClick={(e) => { e.stopPropagation(); handleStatusChange('completed'); }}
                disabled={isUpdating}
              >
                <CheckCircle2 size={14} />
                Complete
              </button>
              <button
                className="btn sched-cancel-btn"
                onClick={(e) => { e.stopPropagation(); onCancel(schedule.id); }}
                disabled={isUpdating}
              >
                <XCircle size={14} />
                Cancel
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Schedule Timeline Component ───
function ScheduleTimeline({ schedules }) {
  const upcoming = schedules
    .filter(s => ['pending', 'scheduled', 'in_progress'].includes(s.status))
    .sort((a, b) => new Date(a.scheduled_date) - new Date(b.scheduled_date))
    .slice(0, 8);

  if (upcoming.length === 0) {
    return (
      <div className="sched-timeline-empty">
        <CheckCircle2 size={40} style={{ color: 'var(--success)', opacity: 0.5 }} />
        <p>No upcoming services scheduled</p>
      </div>
    );
  }

  return (
    <div className="sched-timeline">
      {upcoming.map((s, idx) => {
        const isOverdue = new Date(s.scheduled_date) < new Date();
        return (
          <div key={s.id} className={`sched-timeline-item ${isOverdue ? 'sched-timeline-overdue' : ''}`}>
            <div className="sched-timeline-dot-wrapper">
              <div className={`sched-timeline-dot sched-dot-${s.priority}`} />
              {idx < upcoming.length - 1 && <div className="sched-timeline-line" />}
            </div>
            <div className="sched-timeline-content">
              <div className="sched-timeline-header">
                <span className="sched-timeline-type">
                  {getServiceTypeIcon(s.service_type)}
                  {getServiceTypeLabel(s.service_type)}
                </span>
                <span className={`sched-priority-badge-sm sched-priority-${s.priority}`}>
                  {s.priority}
                </span>
              </div>
              <div className="sched-timeline-date">
                <Clock size={12} />
                {formatDate(s.scheduled_date)}
                {isOverdue && <span className="sched-overdue-tag-sm">OVERDUE</span>}
              </div>
              <div className="sched-timeline-vehicle">
                Vehicle: {s.vehicle_id ? s.vehicle_id.substring(0, 8) + '...' : 'Unassigned'}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ─── Main Page Component ───
export default function ServiceSchedulingPage() {
  const [schedules, setSchedules] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [lastRefresh, setLastRefresh] = useState(null);

  const loadData = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);

    try {
      const params = {};
      if (statusFilter) params.status = statusFilter;
      if (priorityFilter) params.priority = priorityFilter;

      const [schedulesData, statsData] = await Promise.all([
        fetchServiceSchedules(params),
        fetchServiceScheduleStats(),
      ]);

      setSchedules(schedulesData);
      setStats(statsData);
      setLastRefresh(new Date());
    } catch (err) {
      console.error('Failed to load service schedules:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [statusFilter, priorityFilter]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Auto-refresh every 30s
  useEffect(() => {
    const interval = setInterval(() => loadData(true), 30000);
    return () => clearInterval(interval);
  }, [loadData]);

  const handleStatusUpdate = async (scheduleId, updateData) => {
    try {
      await updateServiceSchedule(scheduleId, updateData);
      await loadData(true);
    } catch (err) {
      console.error('Failed to update schedule:', err);
    }
  };

  const handleCancel = async (scheduleId) => {
    try {
      await cancelServiceSchedule(scheduleId);
      await loadData(true);
    } catch (err) {
      console.error('Failed to cancel schedule:', err);
    }
  };

  // ─── Chart Data ───
  const statusPieData = stats ? [
    { name: 'Pending', value: stats.pending_count, color: STATUS_COLORS.pending },
    { name: 'Scheduled', value: stats.scheduled_count, color: STATUS_COLORS.scheduled },
    { name: 'In Progress', value: stats.in_progress_count, color: STATUS_COLORS.in_progress },
    { name: 'Completed', value: stats.completed_count, color: STATUS_COLORS.completed },
    { name: 'Cancelled', value: stats.cancelled_count, color: STATUS_COLORS.cancelled },
  ].filter(d => d.value > 0) : [];

  const typePieData = stats ? [
    { name: 'Urgent', value: stats.urgent_services, color: '#dc2626' },
    { name: 'Inspection', value: stats.inspection_services, color: '#3b82f6' },
    { name: 'Repair', value: stats.repair_services, color: '#f59e0b' },
  ].filter(d => d.value > 0) : [];

  // Group schedules by date for trend line
  const trendData = (() => {
    const grouped = {};
    schedules.forEach(s => {
      const date = new Date(s.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      if (!grouped[date]) grouped[date] = { date, count: 0, urgent: 0, inspection: 0 };
      grouped[date].count++;
      if (s.service_type === 'urgent') grouped[date].urgent++;
      else grouped[date].inspection++;
    });
    return Object.values(grouped).slice(-7);
  })();

  if (loading) {
    return (
      <div className="sched-loading">
        <RefreshCw size={32} className="animate-spin" style={{ color: 'var(--primary)' }} />
        <p>Loading service schedules...</p>
      </div>
    );
  }

  return (
    <div className="sched-page">
      {/* Header */}
      <div className="page-header">
        <div>
          <div className="flex items-center gap-3">
            <div className="sched-header-icon">
              <ClipboardList size={22} />
            </div>
            <div>
              <h1 className="page-title">Service Scheduling</h1>
              <p className="page-subtitle">
                Predictive maintenance workflows powered by ML risk analysis
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {lastRefresh && (
            <span className="text-xs text-muted">
              Updated {lastRefresh.toLocaleTimeString()}
            </span>
          )}
          <button
            className="btn btn-secondary"
            onClick={() => loadData(true)}
            disabled={refreshing}
          >
            <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Priority Alert Banner */}
      {stats && <PriorityAlertBanner stats={stats} />}

      {/* Stat Cards */}
      {stats && (
        <div className="grid-cols-4 sched-stats-row">
          <div className="card stat-card">
            <div className="stat-header">
              <span className="stat-title">Total Schedules</span>
              <div className="stat-icon primary"><ClipboardList size={18} /></div>
            </div>
            <div className="stat-value">{stats.total_schedules}</div>
            <div className="stat-trend neutral">
              {stats.upcoming_24h} upcoming in 24h
            </div>
          </div>

          <div className="card stat-card">
            <div className="stat-header">
              <span className="stat-title">Pending Services</span>
              <div className="stat-icon warning"><Clock size={18} /></div>
            </div>
            <div className="stat-value">{stats.pending_count}</div>
            <div className="stat-trend neutral">
              {stats.scheduled_count} scheduled
            </div>
          </div>

          <div className="card stat-card">
            <div className="stat-header">
              <span className="stat-title">High Priority</span>
              <div className="stat-icon danger"><AlertTriangle size={18} /></div>
            </div>
            <div className="stat-value">{stats.high_priority_count}</div>
            <div className={`stat-trend ${stats.overdue_count > 0 ? 'down' : 'up'}`}>
              {stats.overdue_count > 0 ? `${stats.overdue_count} overdue` : 'All on track'}
            </div>
          </div>

          <div className="card stat-card">
            <div className="stat-header">
              <span className="stat-title">Completed</span>
              <div className="stat-icon success"><CheckCircle2 size={18} /></div>
            </div>
            <div className="stat-value">{stats.completed_count}</div>
            <div className="stat-trend up">
              {stats.in_progress_count} in progress
            </div>
          </div>
        </div>
      )}

      {/* Main content grid */}
      <div className="sched-main-grid">
        {/* Left: Filters + Service Cards */}
        <div className="sched-left-col">
          {/* Filters */}
          <div className="card sched-filters-card">
            <div className="sched-filters-row">
              <div className="sched-filter-group">
                <Filter size={14} />
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="sched-filter-select"
                >
                  {STATUS_OPTIONS.map(o => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </select>
              </div>
              <div className="sched-filter-group">
                <Shield size={14} />
                <select
                  value={priorityFilter}
                  onChange={(e) => setPriorityFilter(e.target.value)}
                  className="sched-filter-select"
                >
                  {PRIORITY_OPTIONS.map(o => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </select>
              </div>
              <span className="sched-result-count">
                {schedules.length} result{schedules.length !== 1 ? 's' : ''}
              </span>
            </div>
          </div>

          {/* Service Cards List */}
          <div className="sched-cards-list">
            {schedules.length === 0 ? (
              <div className="sched-empty-state">
                <CheckCircle2 size={48} style={{ color: 'var(--success)', opacity: 0.4 }} />
                <h3>No service schedules found</h3>
                <p className="text-muted">
                  Service schedules are automatically created when predictions detect MEDIUM or HIGH risk.
                </p>
              </div>
            ) : (
              schedules.map(s => (
                <ServiceCard
                  key={s.id}
                  schedule={s}
                  onStatusUpdate={handleStatusUpdate}
                  onCancel={handleCancel}
                />
              ))
            )}
          </div>
        </div>

        {/* Right: Timeline + Charts */}
        <div className="sched-right-col">
          {/* Timeline */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Upcoming Schedule</h3>
              <Calendar size={16} className="card-action" />
            </div>
            <ScheduleTimeline schedules={schedules} />
          </div>

          {/* Status Distribution Pie */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Status Distribution</h3>
            </div>
            {statusPieData.length > 0 ? (
              <div className="sched-chart-container">
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie
                      data={statusPieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {statusPieData.map((entry, i) => (
                        <Cell key={i} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border)',
                        borderRadius: 'var(--radius-md)',
                        fontSize: '0.8125rem',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div className="sched-pie-legend">
                  {statusPieData.map((d, i) => (
                    <div key={i} className="sched-pie-legend-item">
                      <span className="legend-dot" style={{ backgroundColor: d.color }} />
                      <span>{d.name}</span>
                      <strong>{d.value}</strong>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="sched-chart-empty">No data available</div>
            )}
          </div>

          {/* Service Type Distribution */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Service Types</h3>
            </div>
            {typePieData.length > 0 ? (
              <div className="sched-chart-container">
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie
                      data={typePieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {typePieData.map((entry, i) => (
                        <Cell key={i} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border)',
                        borderRadius: 'var(--radius-md)',
                        fontSize: '0.8125rem',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div className="sched-pie-legend">
                  {typePieData.map((d, i) => (
                    <div key={i} className="sched-pie-legend-item">
                      <span className="legend-dot" style={{ backgroundColor: d.color }} />
                      <span>{d.name}</span>
                      <strong>{d.value}</strong>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="sched-chart-empty">No data available</div>
            )}
          </div>

          {/* Trend Chart */}
          {trendData.length > 1 && (
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Service Trends</h3>
                <TrendingUp size={16} className="card-action" />
              </div>
              <div className="sched-chart-container">
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="date" tick={{ fontSize: 11, fill: 'var(--text-secondary)' }} />
                    <YAxis tick={{ fontSize: 11, fill: 'var(--text-secondary)' }} allowDecimals={false} />
                    <Tooltip
                      contentStyle={{
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border)',
                        borderRadius: 'var(--radius-md)',
                        fontSize: '0.8125rem',
                      }}
                    />
                    <Bar dataKey="urgent" name="Urgent" fill="#dc2626" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="inspection" name="Inspection" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                    <Legend wrapperStyle={{ fontSize: '0.75rem' }} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
