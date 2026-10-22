import { useEffect, useMemo, useState } from 'react'
import { Navigate, Route, Routes, useNavigate } from 'react-router'
import Header from './components/header/Header'
import DashboardPage from './pages/dashboard/Dashboard'
import DataManager from './pages/data_manager/DataManager'
import LoginPage from './pages/login/Login'
import Signup from './pages/signup/Signup'
import './App.css'



function getStoredToken() {
  return localStorage.getItem('field_service_token') || ''
}

async function apiFetch(path, options = {}, token = '') {
  const response = await fetch(path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  })

  const contentType = response.headers.get('content-type') || ''
  const isJson = contentType.includes('application/json')
  const payload = isJson ? await response.json() : await response.text()

  if (!response.ok) {
    const message = typeof payload === 'string' ? payload : payload?.detail || 'Request failed'
    throw new Error(message)
  }

  return payload
}

function App() {
  const navigate = useNavigate()
  const [token, setToken] = useState(getStoredToken())
  const [user, setUser] = useState(null)
  const [loadingUser, setLoadingUser] = useState(Boolean(getStoredToken()))

  useEffect(() => {
    if (!token) {
      setUser(null)
      setLoadingUser(false)
      return
    }

    let isMounted = true
    setLoadingUser(true)

    apiFetch('/api/users/me', {}, token)
      .then((profile) => {
        if (isMounted) {
          setUser(profile)
        }
      })
      .catch(() => {
        localStorage.removeItem('field_service_token')
        setToken('')
        setUser(null)
        navigate('/login')
      })
      .finally(() => {
        if (isMounted) {
          setLoadingUser(false)
        }
      })

    return () => {
      isMounted = false
    }
  }, [token, navigate])

  const authValue = useMemo(
    () => ({
      token,
      user,
      loadingUser,
      setToken,
      setUser,
    }),
    [token, user, loadingUser],
  )

  const handleLogin = async (email, password) => {
    const form = new URLSearchParams({ username: email, password })
    const loginResponse = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form.toString(),
    })

    const payload = await loginResponse.json().catch(() => ({}))

    if (!loginResponse.ok) {
      throw new Error(payload?.detail || 'Login failed')
    }

    localStorage.setItem('field_service_token', payload.access_token)
    setToken(payload.access_token)
    navigate('/dashboard')
  }

  const handleSignup = async (payload) => {
    const response = await fetch('/api/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    const data = await response.json().catch(() => ({}))

    if (!response.ok) {
      throw new Error(data?.detail || 'Signup failed')
    }

    return data
  }

  const handleLogout = () => {
    localStorage.removeItem('field_service_token')
    setToken('')
    setUser(null)
    navigate('/login')
  }

  return (
    <Routes>
      <Route path="/" element={<Navigate to={token ? '/dashboard' : '/login'} replace />} />

      <Route
        path="/login"
        element={
          token ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <LoginPage onLogin={handleLogin} />
          )
        }
      />

      <Route
        path="/signup"
        element={
          token ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <Signup onSignup={handleSignup} />
          )
        }
      />

      <Route
        path="/dashboard"
        element={
          token ? (
            <DashboardPage user={user} token={token} onLogout={handleLogout} />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />

      <Route
        path="/data"
        element={
          token ? (
            <DataManager user={user} token={token} onLogout={handleLogout} />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
    </Routes>
  )
}

export { apiFetch }

export default App
