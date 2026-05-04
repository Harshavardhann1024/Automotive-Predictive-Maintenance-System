import React, { useContext } from 'react';
import { Search, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';

const Header = () => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  return (
    <header className="top-header" style={{ justifyContent: 'flex-end' }}>
      <div className="header-actions">
        
        {user && (
          <div className="user-profile" onClick={() => navigate('/profile')} style={{ cursor: 'pointer' }}>
            <div className="avatar">{user.name?.charAt(0).toUpperCase()}</div>
            <div className="user-info">
              <span className="user-name">{user.name}</span>
              <span className="user-role" style={{ textTransform: 'capitalize' }}>{user.role}</span>
            </div>
          </div>
        )}

        <button className="header-icon-btn" onClick={logout} title="Logout">
          <LogOut size={20} />
        </button>
      </div>
    </header>
  );
};

export default Header;
