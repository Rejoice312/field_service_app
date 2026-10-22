import { Fragment } from "react"
import { Link } from "react-router"
import './Header.css'

function Header({ user, onLogout }) {
    return (
        <Fragment>
            <header className="header">
                <div className="brand-area">
                    <div className="brand-mark">FS</div>
                    <div>
                        <div className="brand-title">Field Service App</div>
                        {user && <div className="brand-subtitle">Welcome, {user.name}</div>}
                    </div>
                </div>

                <nav className="header-nav" aria-label="Main navigation">
                    <Link className="header-navlink" to="/dashboard">Dashboard</Link>
                    <Link className="header-navlink" to="/data">Data Manager</Link>
                    {onLogout && (
                        <button type="button" className="logout-button" onClick={onLogout}>
                            Logout
                        </button>
                    )}
                </nav>
            </header>
        </Fragment>
    )
}

export default Header