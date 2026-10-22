import { useEffect, useMemo, useState, useRef } from 'react'
import Header from '../../components/header/Header'
import { API_DOMAIN, apiFetch } from '../../App'

const emptyPersonForm = {
  name: '',
  phone: '',
  addr: '',
  region: '',
}

const emptyConversationForm = {
  date: new Date().toISOString().slice(0, 10),
  topic: '',
  next_topic: '',
  type: 'Initial Call',
  person_id: '',
}

const emptyStudentForm = {
  person_id: '',
  std_date: new Date().toISOString().slice(0, 10),
  handover_date: '',
  handover_teacher: '',
}

export function DataManager({ user, token, onLogout }) {
  const [people, setPeople] = useState([])
  const [conversations, setConversations] = useState([])
  const [students, setStudents] = useState([])
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showForms, setShowForms] = useState({ person: false, conversation: false, student: false })
  const [editingPersonId, setEditingPersonId] = useState(null)
  const [editingConversationId, setEditingConversationId] = useState(null)
  const [editingStudentPersonId, setEditingStudentPersonId] = useState(null)
  const [personForm, setPersonForm] = useState(emptyPersonForm)
  const [conversationForm, setConversationForm] = useState(emptyConversationForm)
  const [studentForm, setStudentForm] = useState(emptyStudentForm)

  const panelRefs = {
    person: useRef(null),
    conversation: useRef(null),
    student: useRef(null),
  }

  const loadData = async () => {
    setError('')

    try {
      const [peopleData, conversationsData, studentsData] = await Promise.all([
        apiFetch(`${API_DOMAIN}/api/me/persons`, {}, token),
        apiFetch(`${API_DOMAIN}/api/me/conversations`, {}, token),
        apiFetch(`${API_DOMAIN}/api/me/students`, {}, token),
      ])

      setPeople(peopleData)
      setConversations(conversationsData)
      setStudents(studentsData)
    } catch (err) {
      setError(err.message || 'Could not load your data.')
    }
  }

  useEffect(() => {
    if (token) {
      loadData()
    }
  }, [token])

  const stats = useMemo(
    () => ({
      people: people.length,
      conversations: conversations.length,
      students: students.length,
    }),
    [people, conversations, students],
  )

  const closeForm = (formKey) => {
    setShowForms((current) => ({ ...current, [formKey]: false }))
    if (formKey === 'person') {
      setPersonForm(emptyPersonForm)
      setEditingPersonId(null)
    }
    if (formKey === 'conversation') {
      setConversationForm({ ...emptyConversationForm, person_id: '' })
      setEditingConversationId(null)
    }
    if (formKey === 'student') {
      setStudentForm({ ...emptyStudentForm, person_id: '' })
      setEditingStudentPersonId(null)
    }
  }

  const focusFormPanel = (formKey) => {
    const panel = panelRefs[formKey]?.current
    if (panel) {
      panel.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  const openPersonForm = (person = null) => {
    if (showForms.person && !person && !editingPersonId) {
      closeForm('person')
      return
    }

    setEditingPersonId(person ? person.id : null)
    setPersonForm(person ? { ...emptyPersonForm, ...person } : emptyPersonForm)
    setShowForms({ person: true, conversation: false, student: false })
    setError('')
    setSuccess('')
    setTimeout(() => focusFormPanel('person'), 50)
  }

  const openConversationForm = (conversation = null) => {
    if (showForms.conversation && !conversation && !editingConversationId) {
      closeForm('conversation')
      return
    }

    setEditingConversationId(conversation ? conversation.id : null)
    setConversationForm(
      conversation
        ? {
            date: conversation.date,
            topic: conversation.topic,
            next_topic: conversation.next_topic || '',
            type: conversation.type,
            person_id: String(conversation.person_id),
          }
        : { ...emptyConversationForm, person_id: '' },
    )
    setShowForms({ person: false, conversation: true, student: false })
    setError('')
    setSuccess('')
    setTimeout(() => focusFormPanel('conversation'), 50)
  }

  const openStudentForm = (student = null) => {
    if (showForms.student && !student && !editingStudentPersonId) {
      closeForm('student')
      return
    }

    setEditingStudentPersonId(student ? student.person_id : null)
    setStudentForm(
      student
        ? {
            person_id: String(student.person_id),
            std_date: student.std_date,
            handover_date: student.handover_date || '',
            handover_teacher: student.handover_teacher || '',
          }
        : { ...emptyStudentForm, person_id: '' },
    )
    setShowForms({ person: false, conversation: false, student: true })
    setError('')
    setSuccess('')
    setTimeout(() => focusFormPanel('student'), 50)
  }

  const handlePersonChange = (event) => {
    setPersonForm({ ...personForm, [event.target.name]: event.target.value })
  }

  const handleConversationChange = (event) => {
    setConversationForm({ ...conversationForm, [event.target.name]: event.target.value })
  }

  const handleStudentChange = (event) => {
    setStudentForm({ ...studentForm, [event.target.name]: event.target.value })
  }

  const handlePersonSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSuccess('')

    const payload = {
      name: personForm.name,
      phone: personForm.phone || null,
      addr: personForm.addr || null,
      region: personForm.region || null,
    }

    try {
      if (editingPersonId) {
        await apiFetch(`${API_DOMAIN}/api/me/persons?person_id=${editingPersonId}`, {
          method: 'PATCH',
          body: JSON.stringify(payload),
        }, token)
        setSuccess('Person updated successfully.')
      } else {
        await apiFetch(
          `${API_DOMAIN}/api/me/persons`,
          {
            method: 'POST',
            body: JSON.stringify([payload]),
          },
          token,
        )
        setSuccess('Person added successfully.')
      }

      setPersonForm(emptyPersonForm)
      setEditingPersonId(null)
      closeForm('person')
      loadData()
    } catch (err) {
      setError(err.message || 'Failed to save person.')
    }
  }

  const handleConversationSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSuccess('')

    const payload = {
      date: conversationForm.date,
      topic: conversationForm.topic,
      next_topic: conversationForm.next_topic || null,
      type: conversationForm.type,
      person_id: Number(conversationForm.person_id),
    }

    try {
      if (editingConversationId) {
        await apiFetch(`${API_DOMAIN}/api/me/conversations?conversation_id=${editingConversationId}`, {
          method: 'PATCH',
          body: JSON.stringify(payload),
        }, token)
        setSuccess('Conversation updated successfully.')
      } else {
        await apiFetch(
          `${API_DOMAIN}/api/me/conversations`,
          {
            method: 'POST',
            body: JSON.stringify(payload),
          },
          token,
        )
        setSuccess('Conversation added successfully.')
      }

      setConversationForm({ ...emptyConversationForm, person_id: conversationForm.person_id || '' })
      setEditingConversationId(null)
      closeForm('conversation')
      loadData()
    } catch (err) {
      setError(err.message || 'Failed to save conversation.')
    }
  }

  const handleStudentSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSuccess('')

    const payload = {
      person_id: Number(studentForm.person_id),
      std_date: studentForm.std_date,
      handover_date: studentForm.handover_date || null,
      handover_teacher: studentForm.handover_teacher || null,
    }

    try {
      if (editingStudentPersonId) {
        await apiFetch(`${API_DOMAIN}/api/me/students/?student_id=${editingStudentPersonId}`, { method: 'DELETE' }, token)
        await apiFetch(`${API_DOMAIN}/api/me/students`, {
          method: 'POST',
          body: JSON.stringify(payload),
        }, token)
        setSuccess('Student updated successfully.')
      } else {
        await apiFetch(`${API_DOMAIN}/api/me/students`, {
          method: 'POST',
          body: JSON.stringify(payload),
        }, token)
        setSuccess('Student added successfully.')
      }

      setStudentForm({ ...emptyStudentForm, person_id: studentForm.person_id || '' })
      setEditingStudentPersonId(null)
      closeForm('student')
      loadData()
    } catch (err) {
      setError(err.message || 'Failed to save student.')
    }
  }

  const deleteConversation = async (conversationId) => {
    const confirmed = window.confirm('Delete this conversation?')
    if (!confirmed) return

    try {
      await apiFetch(`${API_DOMAIN}/api/me/conversations?conversation_id=${conversationId}`, { method: 'DELETE' }, token)
      setSuccess('Conversation deleted.')
      loadData()
    } catch (err) {
      setError(err.message || 'Failed to delete conversation.')
    }
  }

  const deleteStudent = async (studentId) => {
    const confirmed = window.confirm('Delete this student record?')
    if (!confirmed) return

    try {
      await apiFetch(`${API_DOMAIN}/api/me/students/?student_id=${studentId}`, { method: 'DELETE' }, token)
      setSuccess('Student removed.')
      loadData()
    } catch (err) {
      setError(err.message || 'Failed to delete student.')
    }
  }

  const resetFormState = (formKey) => {
    setShowForms((current) => ({ ...current, [formKey]: false }))
  }

  const tableStyles = {
    maxHeight: '400px',
    overflowY: 'auto',
  }

  return (
    <>
      <Header user={user} onLogout={onLogout} />

      <main className="page-shell">
        <section className="page-header">
          <div>
            <p className="eyebrow">Data overview</p>
            <h2>Data Manager</h2>
          </div>
        </section>

        <div className="grid">
          <div className="card">
            <h3>People</h3>
            <p className="metric-value">{stats.people}</p>
            <div className="metric-subtext">Total registered people</div>
          </div>
          <div className="card">
            <h3>Conversations</h3>
            <p className="metric-value">{stats.conversations}</p>
            <div className="metric-subtext">Total call records</div>
          </div>
          <div className="card">
            <h3>Students</h3>
            <p className="metric-value">{stats.students}</p>
            <div className="metric-subtext">Marked as students</div>
          </div>
        </div>

        {(error || success) && (
          <div className="panel" style={{ marginBottom: '1.5rem' }}>
            {error && <div className="error-box">{error}</div>}
            {success && (
              <div style={{ background: '#eefaf2', border: '1px solid #cfe7d7', color: '#1f6d41', borderRadius: '10px', padding: '0.8rem 0.9rem' }}>
                {success}
              </div>
            )}
          </div>
        )}

        <div className="panel" style={{ marginBottom: '1.5rem' }}>
          <div className="toolbar">
            <h3 style={{ margin: 0 }}>People</h3>
            <button type="button" className="primary-button" onClick={() => (showForms.person ? closeForm('person') : openPersonForm())}>
              {showForms.person ? 'Close form' : 'Add person'}
            </button>
          </div>

          {showForms.person && (
            <form onSubmit={handlePersonSubmit}>
              <div className="form-grid">
                <div className="field-group">
                  <label htmlFor="person-name">Name</label>
                  <input id="person-name" className="form-field" name="name" value={personForm.name} onChange={handlePersonChange} required />
                </div>
                <div className="field-group">
                  <label htmlFor="person-phone">Phone</label>
                  <input id="person-phone" className="form-field" name="phone" value={personForm.phone} onChange={handlePersonChange} />
                </div>
                <div className="field-group">
                  <label htmlFor="person-region">Region</label>
                  <input id="person-region" className="form-field" name="region" value={personForm.region} onChange={handlePersonChange} />
                </div>
                <div className="field-group" style={{ gridColumn: '1 / -1' }}>
                  <label htmlFor="person-address">Address</label>
                  <input id="person-address" className="form-field" name="addr" value={personForm.addr} onChange={handlePersonChange} />
                </div>
              </div>
              <div className="form-actions">
                <button type="button" className="secondary-button" onClick={() => closeForm('person')}>
                  Cancel
                </button>
                <button type="submit" className="primary-button">{editingPersonId ? 'Update person' : 'Save person'}</button>
              </div>
            </form>
          )}
        </div>

        <div className="panel" style={{ marginBottom: '1.5rem' }} ref={panelRefs.conversation}>
          <div className="toolbar">
            <h3 style={{ margin: 0 }}>Conversations</h3>
            <button type="button" className="primary-button" onClick={() => (showForms.conversation ? closeForm('conversation') : openConversationForm())}>
              {showForms.conversation ? 'Close form' : 'Add conversation'}
            </button>
          </div>

          {showForms.conversation && (
            <form onSubmit={handleConversationSubmit}>
              <div className="form-grid">
                <div className="field-group">
                  <label htmlFor="conversation-person">Person</label>
                  <select id="conversation-person" className="form-select" name="person_id" value={conversationForm.person_id} onChange={handleConversationChange} required>
                    <option value="">Select a person</option>
                    {people.map((person) => (
                      <option key={person.id} value={person.id}>{person.name}</option>
                    ))}
                  </select>
                </div>
                <div className="field-group">
                  <label htmlFor="conversation-date">Date</label>
                  <input id="conversation-date" className="form-field" type="date" name="date" value={conversationForm.date} onChange={handleConversationChange} required />
                </div>
                <div className="field-group">
                  <label htmlFor="conversation-type">Type</label>
                  <select id="conversation-type" className="form-select" name="type" value={conversationForm.type} onChange={handleConversationChange}>
                    <option value="Initial Call">Initial Call</option>
                    <option value="Following Up">Following Up</option>
                    <option value="Bible Study">Bible Study</option>
                  </select>
                </div>
                <div className="field-group" style={{ gridColumn: '1 / -1' }}>
                  <label htmlFor="conversation-topic">Topic</label>
                  <textarea id="conversation-topic" className="form-textarea" name="topic" value={conversationForm.topic} onChange={handleConversationChange} required />
                </div>
                <div className="field-group" style={{ gridColumn: '1 / -1' }}>
                  <label htmlFor="conversation-next-topic">Next topic</label>
                  <textarea id="conversation-next-topic" className="form-textarea" name="next_topic" value={conversationForm.next_topic} onChange={handleConversationChange} />
                </div>
              </div>
              <div className="form-actions">
                <button type="button" className="secondary-button" onClick={() => closeForm('conversation')}>
                  Cancel
                </button>
                <button type="submit" className="primary-button">{editingConversationId ? 'Update conversation' : 'Save conversation'}</button>
              </div>
            </form>
          )}
        </div>

        <div className="panel" style={{ marginBottom: '1.5rem' }} ref={panelRefs.student}>
          <div className="toolbar">
            <h3 style={{ margin: 0 }}>Students</h3>
            <button type="button" className="primary-button" onClick={() => (showForms.student ? closeForm('student') : openStudentForm())}>
              {showForms.student ? 'Close form' : 'Add student'}
            </button>
          </div>

          {showForms.student && (
            <form onSubmit={handleStudentSubmit}>
              <div className="form-grid">
                <div className="field-group">
                  <label htmlFor="student-person">Person</label>
                  <select id="student-person" className="form-select" name="person_id" value={studentForm.person_id} onChange={handleStudentChange} required>
                    <option value="">Select a person</option>
                    {people.map((person) => (
                      <option key={person.id} value={person.id}>{person.name}</option>
                    ))}
                  </select>
                </div>
                <div className="field-group">
                  <label htmlFor="student-date">Student date</label>
                  <input id="student-date" className="form-field" type="date" name="std_date" value={studentForm.std_date} onChange={handleStudentChange} required />
                </div>
                <div className="field-group">
                  <label htmlFor="student-handover-date">Handover date</label>
                  <input id="student-handover-date" className="form-field" type="date" name="handover_date" value={studentForm.handover_date} onChange={handleStudentChange} />
                </div>
                <div className="field-group">
                  <label htmlFor="student-teacher">Handover teacher</label>
                  <input id="student-teacher" className="form-field" name="handover_teacher" value={studentForm.handover_teacher} onChange={handleStudentChange} />
                </div>
              </div>
              <div className="form-actions">
                <button type="button" className="secondary-button" onClick={() => closeForm('student')}>
                  Cancel
                </button>
                <button type="submit" className="primary-button">{editingStudentPersonId ? 'Update student' : 'Save student'}</button>
              </div>
            </form>
          )}
        </div>

        <div className="panel">
          <h3>People</h3>
          {people.length ? (
            <div className="table-wrap" style={tableStyles}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Phone</th>
                    <th>Address</th>
                    <th>Region</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {people.map((person) => (
                    <tr key={person.id}>
                      <td>{person.name}</td>
                      <td>{person.phone || '-'}</td>
                      <td>{person.addr || '-'}</td>
                      <td>{person.region || '-'}</td>
                      <td>
                        <div className="table-actions">
                          <button type="button" className="secondary-button" onClick={() => openPersonForm(person)}>Edit</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">No people found yet.</div>
          )}
        </div>

        <div className="panel" style={{ marginTop: '1.5rem' }}>
          <h3>Conversations</h3>
          {conversations.length ? (
            <div className="table-wrap" style={tableStyles}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Person</th>
                    <th>Type</th>
                    <th>Topic</th>
                    <th>Next topic</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {conversations.map((conversation) => (
                    <tr key={conversation.id}>
                      <td>{conversation.date}</td>
                      <td>{people.find((person) => person.id === conversation.person_id)?.name || conversation.person_id}</td>
                      <td>{conversation.type}</td>
                      <td>{conversation.topic}</td>
                      <td>{conversation.next_topic || '-'}</td>
                      <td>
                        <div className="table-actions">
                          <button type="button" className="secondary-button" onClick={() => openConversationForm(conversation)}>Edit</button>
                          <button type="button" className="danger-button" onClick={() => deleteConversation(conversation.id)}>Delete</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">No conversations yet.</div>
          )}
        </div>

        <div className="panel" style={{ marginTop: '1.5rem' }}>
          <h3>Students</h3>
          {students.length ? (
            <div className="table-wrap" style={tableStyles}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Person</th>
                    <th>Study date</th>
                    <th>Handover date</th>
                    <th>Teacher</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((student) => (
                    <tr key={student.person_id}>
                      <td>{people.find((person) => person.id === student.person_id)?.name || student.person_id}</td>
                      <td>{student.std_date}</td>
                      <td>{student.handover_date || '-'}</td>
                      <td>{student.handover_teacher || '-'}</td>
                      <td>
                        <div className="table-actions">
                          <button type="button" className="secondary-button" onClick={() => openStudentForm(student)}>Edit</button>
                          <button type="button" className="danger-button" onClick={() => deleteStudent(student.person_id)}>Delete</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">No students yet.</div>
          )}
        </div>
      </main>
    </>
  )
}

export default DataManager