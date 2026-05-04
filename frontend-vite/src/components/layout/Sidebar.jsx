import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Car, 
  AlertTriangle, 
  BrainCircuit, 
  FileText, 
  Activity
} from 'lucide-react';

const Sidebar = () => {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard className="nav-icon" /> },
    { name: 'Vehicles', path: '/vehicles', icon: <Car className="nav-icon" /> },
    { name: 'Alerts', path: '/alerts', icon: <AlertTriangle className="nav-icon" /> },
    { name: 'Predictions', path: '/predictions', icon: <BrainCircuit className="nav-icon" /> },
    { name: 'Reports', path: '/reports', icon: <FileText className="nav-icon" /> }
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <Activity className="sidebar-brand-icon" size={28} />
        <span>AutoPredict SaaS</span>
      </div>
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink 
            to={item.path} 
            key={item.name}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            {item.icon}
            <span>{item.name}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
