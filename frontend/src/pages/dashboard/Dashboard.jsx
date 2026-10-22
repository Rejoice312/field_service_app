import { useEffect, useMemo, useState } from 'react'
import Header from '../../components/header/Header'
import { apiFetch } from '../../App'
import './Dashboard.css'

function DashboardPage({ user, token, onLogout }) {
  const [people, setPeople] = useState([])
  const [conversations, setConversations] = useState([])
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) {
      return
    }

    const loadDashboardData = async () => {
      setLoading(true)
      setError('')

      try {
        const [peopleData, conversationsData, studentsData] = await Promise.all([
          apiFetch('/api/me/persons', {}, token),
          apiFetch('/api/me/conversations', {}, token),
          apiFetch('/api/me/students', {}, token),
        ])

        setPeople(peopleData)
        setConversations(conversationsData)
        setStudents(studentsData)
      } catch (err) {
        setError(err.message || 'Unable to load dashboard metrics.')
      } finally {
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [token])

  const personMap = useMemo(
    () => Object.fromEntries(people.map((person) => [person.id, person])),
    [people],
  )

  const currentMonth = new Date().toISOString().slice(0, 7)

  const monthlyBibleStudies = useMemo(() => {
    const monthMap = new Map()

    for (const conversation of conversations) {
      if (conversation.type !== 'Bible Study') {
        continue
      }

      const monthKey = conversation.date?.slice(0, 7)
      if (!monthKey) {
        continue
      }

      const monthEntry = monthMap.get(monthKey) || new Set()
      monthEntry.add(conversation.person_id)
      monthMap.set(monthKey, monthEntry)
    }

    return Array.from(monthMap.entries())
      .map(([month, peopleSet]) => ({ month, count: peopleSet.size }))
      .sort((a, b) => a.month.localeCompare(b.month))
  }, [conversations])

  const bibleStudyCurrentMonthUnique = useMemo(
    () =>
      new Set(
        conversations
          .filter((conversation) => conversation.type === 'Bible Study' && conversation.date?.slice(0, 7) === currentMonth)
          .map((conversation) => conversation.person_id),
      ).size,
    [conversations, currentMonth],
  )

  const newConversationsCurrentMonth = useMemo(
    () => conversations.filter((conversation) => conversation.type === 'Initial Call' && conversation.date?.slice(0, 7) === currentMonth).length,
    [conversations, currentMonth],
  )

  const studentStudyCounts = useMemo(() => {
    const counts = new Map()

    for (const student of students) {
      const name = personMap[student.person_id]?.name || `Student ${student.person_id}`
      counts.set(student.person_id, {
        name,
        count: conversations.filter(
          (conversation) =>
            conversation.person_id === student.person_id &&
            conversation.type === 'Bible Study',
        ).length,
      })
    }

    return Array.from(counts.values())
      .filter((entry) => entry.count > 0)
      .sort((a, b) => b.count - a.count)
  }, [students, conversations, personMap])

  const maxStudyCount = Math.max(...studentStudyCounts.map((entry) => entry.count), 0)

  return (
    <>
      <Header user={user} onLogout={onLogout} />

      <main className="page-shell dashboard-page">
        <section className="page-header">
          <div>
            <p className="eyebrow">Overview</p>
            <h2>Dashboard</h2>
          </div>
        </section>

        {error && <div className="error-box dashboard-error">{error}</div>}

        {loading ? (
          <div className="panel loading-panel">Loading dashboard metrics…</div>
        ) : (
          <>
            <section className="kpi-grid">
              <article className="card dashboard-card">
                <h3>Bible Studies</h3>
                <p className="metric-value">{bibleStudyCurrentMonthUnique}</p>
              </article>

              <article className="card dashboard-card">
                <h3>New Conversations</h3>
                <p className="metric-value">{newConversationsCurrentMonth}</p>
              </article>
            </section>

            <section className="panel dashboard-panel">
              <div className="section-heading">
                <h3>Monthly report</h3>
                <span>{currentMonth}</span>
              </div>

              {monthlyBibleStudies.length ? (
                <div className="table-wrap">
                  <table className="data-table dashboard-table">
                    <thead>
                      <tr>
                        <th>Year-Month</th>
                        <th>Bible studies</th>
                      </tr>
                    </thead>
                    <tbody>
                      {monthlyBibleStudies.map((row) => (
                        <tr key={row.month}>
                          <td>{row.month}</td>
                          <td>{row.count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="empty-state">No Bible study records found yet.</div>
              )}
            </section>

            <section className="panel dashboard-panel">
              <div className="section-heading">
                <h3>Studies per student</h3>
                <span>Bible Study conversations</span>
              </div>

              {studentStudyCounts.length ? (
                <div className="bar-chart-wrap">
                  <div className="bar-chart">
                    {studentStudyCounts.map((entry) => {
                      const barHeight = maxStudyCount ? (entry.count / maxStudyCount) * 100 : 0

                      return (
                        <div key={entry.name} className="bar-column">
                          <div className="bar-value">{entry.count}</div>
                          <div className="bar-rail">
                            <div className="bar-fill" style={{ height: `${barHeight}%` }} />
                          </div>
                          <div className="bar-label">{entry.name}</div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              ) : (
                <div className="empty-state">No Bible study counts for students yet.</div>
              )}
            </section>
          </>
        )}
      </main>
    </>
  )
}

export default DashboardPage
