import { useState } from 'react'
import { Link, useNavigate } from 'react-router'
import Header from '../../components/header/Header'
import './Login.css'

function LoginPage({ onLogin }) {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleChange = (event) => {
    setForm({ ...form, [event.target.name]: event.target.value })
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSubmitting(true)

    try {
      await onLogin(form.email, form.password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.message || 'Unable to log in.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <Header />

      <main className="auth-card">
        <h2>Welcome back</h2>
        <p>Sign in to manage people, conversations, and students.</p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="field-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              className="form-field"
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="field-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              className="form-field"
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              required
            />
          </div>

          {error && <div className="error-box">{error}</div>}

          <button type="submit" className="primary-button" disabled={submitting}>
            {submitting ? 'Signing in...' : 'Login'}
          </button>
        </form>

        <p className="auth-switch">
          Need an account? <Link to="/signup">Sign up</Link>
        </p>
      </main>
    </div>
  )
}

export default LoginPage