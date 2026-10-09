import { useEffect, useMemo, useState } from 'react'
import { BrowserRouter, NavLink, Route, Routes, useNavigate } from 'react-router-dom'
import {
  ArrowDownRight,
  ArrowUpRight,
  Bell,
  CheckCircle2,
  CreditCard,
  Database,
  Flame,
  Gauge,
  LayoutDashboard,
  Moon,
  Plus,
  SunMedium,
  Target,
  TrendingUp,
  Wallet,
} from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001'

const navItems = [
  { label: 'Overview', to: '/', icon: LayoutDashboard },
  { label: 'Habits', to: '/habits', icon: Flame },
  { label: 'Transactions', to: '/transactions', icon: Wallet },
  { label: 'Goals', to: '/goals', icon: Target },
  { label: 'Architecture', to: '/architecture', icon: Database },
]

const themeOptions = [
  { value: 'light', label: 'Light', icon: SunMedium },
  { value: 'dark', label: 'Dark', icon: Moon },
]

async function apiFetch(path, options = {}, token) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) }
  if (token) headers.Authorization = `Bearer ${token}`

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })

  if (response.status === 204) return null

  const payload = await response.text()
  const data = payload ? JSON.parse(payload) : null

  if (!response.ok) {
    throw new Error(data?.detail || data?.message || 'Request failed')
  }

  return data
}

function downloadCsv(filename, rows) {
  const headers = rows.length > 0 ? Object.keys(rows[0]) : []
  const csvRows = [headers.join(',')]

  rows.forEach((row) => {
    csvRows.push(headers.map((key) => {
      const value = row[key]
      const escaped = String(value ?? '').replace(/"/g, '""')
      return `"${escaped}"`
    }).join(','))
  })

  const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

function AppShell() {
  const navigate = useNavigate()
  const [theme, setTheme] = useState(() => localStorage.getItem('gm-theme') || 'light')
  const [auth, setAuth] = useState(() => {
    const stored = localStorage.getItem('gm-auth')
    return stored ? JSON.parse(stored) : null
  })
  const [habits, setHabits] = useState([])
  const [transactions, setTransactions] = useState([])
  const [goals, setGoals] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('gm-theme', theme)
  }, [theme])

  useEffect(() => {
    if (auth?.token) {
      localStorage.setItem('gm-auth', JSON.stringify(auth))
    } else {
      localStorage.removeItem('gm-auth')
    }
  }, [auth])

  const refreshData = async (token) => {
    if (!token) return
    setLoading(true)
    setError('')

    try {
      const [habitData, txData, goalData] = await Promise.all([
        apiFetch('/habits/', {}, token).catch(() => []),
        apiFetch('/transactions', {}, token).catch(() => []),
        apiFetch('/goals/', {}, token).catch(() => []),
      ])

      setHabits(habitData || [])
      setTransactions(txData || [])
      setGoals(goalData || [])
    } catch (err) {
      setError(err.message || 'Unable to load data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (auth?.token) refreshData(auth.token)
    else {
      setHabits([])
      setTransactions([])
      setGoals([])
    }
  }, [auth?.token])

  return !auth ? (
    <LoginScreen onAuthSuccess={setAuth} theme={theme} setTheme={setTheme} />
  ) : (
    <div className="app-shell" data-theme={theme}>
      <aside className="sidebar">
        <div className="brand-wrap">
          <img src="/GM-Logo1.png" alt="Geeky Monks logo" className="brand-mark" />
          <div>
            <p className="eyebrow">Wellness + money</p>
            <h1>gm-tracker</h1>
          </div>
        </div>

        <nav className="nav" aria-label="Main navigation">
          {navItems.map(({ label, to, icon: Icon }) => (
            <NavLink key={label} to={to} end={to === '/'} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <Icon size={18} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-card">
          <p className="eyebrow">Focus</p>
          <h3>Build repeatable momentum across work, health, and wealth.</h3>
          <button className="primary-btn small" onClick={() => navigate('/goals')}>Add milestone</button>
        </div>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow">{new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'short', year: 'numeric' })}</p>
            <h2>Good morning, {auth.user?.name || 'there'}</h2>
          </div>

          <div className="topbar-actions">
            <div className="theme-switcher" aria-label="Theme switcher">
              {themeOptions.map(({ value, label, icon: Icon }) => (
                <button
                  key={value}
                  type="button"
                  className={theme === value ? 'theme-pill active' : 'theme-pill'}
                  onClick={() => setTheme(value)}
                >
                  <Icon size={15} />
                  {label}
                </button>
              ))}
            </div>
            <button className="ghost-btn" aria-label="Notifications" onClick={() => setError('No new notifications — you are all caught up.') }><Bell size={18} /></button>
            <button className="primary-btn" onClick={() => setAuth(null)}>Log out</button>
          </div>
        </header>

        {error && <div className="inline-alert">{error}</div>}

        <Routes>
          <Route path="/" element={<OverviewScreen habits={habits} transactions={transactions} goals={goals} loading={loading} />} />
          <Route path="/habits" element={<HabitsScreen habits={habits} setHabits={setHabits} token={auth.token} />} />
          <Route path="/transactions" element={<TransactionsScreen transactions={transactions} setTransactions={setTransactions} token={auth.token} />} />
          <Route path="/goals" element={<GoalsScreen goals={goals} setGoals={setGoals} token={auth.token} />} />
          <Route path="/architecture" element={<ArchitectureScreen />} />
        </Routes>
      </main>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  )
}

function LoginScreen({ onAuthSuccess, theme, setTheme }) {
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')

  const handleChange = (event) => {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setBusy(true)
    setMessage('')

    try {
      const path = mode === 'login' ? '/auth/login' : '/auth/register'
      const payload = mode === 'login'
        ? { email: form.email, password: form.password }
        : { name: form.name, email: form.email, password: form.password }

      const result = await apiFetch(path, { method: 'POST', body: JSON.stringify(payload) })

      if (mode === 'login') {
        onAuthSuccess({ token: result.access_token, user: { name: form.name || 'User', email: form.email } })
      } else {
        setMode('login')
        setForm({ name: '', email: '', password: '' })
        setMessage('Account created. You can log in now.')
      }
    } catch (error) {
      setMessage(error.message || 'Authentication failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-shell" data-theme={theme}>
      <div className="auth-card">
        <div className="auth-branding">
          <img src="/GM-Logo2.png" alt="Geeky Monks logo" className="auth-logo" />
          <div className="theme-switcher inline">
            {themeOptions.map(({ value, label, icon: Icon }) => (
              <button
                key={value}
                type="button"
                className={theme === value ? 'theme-pill active' : 'theme-pill'}
                onClick={() => setTheme(value)}
              >
                <Icon size={14} />
                {label}
              </button>
            ))}
          </div>
        </div>

        <div className="auth-form-wrap">
          <div className="segmented-control">
            <button type="button" className={mode === 'login' ? 'segment active' : 'segment'} onClick={() => setMode('login')}>Login</button>
            <button type="button" className={mode === 'register' ? 'segment active' : 'segment'} onClick={() => setMode('register')}>Register</button>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            {mode === 'register' && (
              <label>
                <span>Name</span>
                <input name="name" value={form.name} onChange={handleChange} placeholder="Sai" required />
              </label>
            )}

            <label>
              <span>Email</span>
              <input type="email" name="email" value={form.email} onChange={handleChange} placeholder="you@example.com" required />
            </label>

            <label>
              <span>Password</span>
              <input type="password" name="password" value={form.password} onChange={handleChange} placeholder="Minimum 8 chars" required />
            </label>

            {message && <div className="inline-alert auth-alert">{message}</div>}

            <button type="submit" className="primary-btn wide" disabled={busy}>
              {busy ? 'Please wait...' : mode === 'login' ? 'Log in' : 'Create account'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

function OverviewScreen({ habits, transactions, goals, loading }) {
  const navigate = useNavigate()

  const summaryCards = useMemo(() => {
    const income = transactions.filter((tx) => tx.type === 'income').reduce((total, tx) => total + Number(tx.amount || 0), 0)
    const expenses = transactions.filter((tx) => tx.type === 'expense').reduce((total, tx) => total + Number(tx.amount || 0), 0)
    const completedHabits = habits.filter((habit) => Number(habit.progress || 0) >= 80).length

    return [
      { label: 'Income', value: `₹${income.toLocaleString('en-IN')}`, change: income > 0 ? 'Live' : 'No data', tone: 'up', icon: ArrowUpRight },
      { label: 'Expenses', value: `₹${expenses.toLocaleString('en-IN')}`, change: expenses > 0 ? 'Live' : 'No data', tone: 'down', icon: ArrowDownRight },
      { label: 'Habits', value: `${completedHabits}/${habits.length || 0}`, change: habits.length ? 'Live' : 'Empty', tone: 'neutral', icon: Flame },
      { label: 'Goals', value: `${goals.length || 0}`, change: goals.length ? 'Live' : 'Empty', tone: 'up', icon: Target },
    ]
  }, [habits, transactions, goals])

  const exportTransactions = () => {
    const rows = transactions.map((tx) => ({
      id: tx.id ?? '',
      type: tx.type ?? '',
      category: tx.category ?? '',
      description: tx.description ?? '',
      amount: Number(tx.amount ?? 0),
      transaction_date: tx.transaction_date ?? '',
    }))
    downloadCsv('gm-transactions.csv', rows)
  }

  return (
    <>
      <section className="hero-card">
        <div>
          <p className="eyebrow accent">Today at a glance</p>
          <h3>Build a life that is consistent, measurable, and calm.</h3>
        </div>

        <div className="hero-metrics">
          <div>
            <span>Habits complete</span>
            <strong>{habits.filter((habit) => Number(habit.progress || 0) >= 80).length || 0}/{habits.length || 0}</strong>
          </div>
          <div>
            <span>Net cash</span>
            <strong>₹{Math.max((transactions.filter((tx) => tx.type === 'income').reduce((sum, tx) => sum + Number(tx.amount || 0), 0) - transactions.filter((tx) => tx.type === 'expense').reduce((sum, tx) => sum + Number(tx.amount || 0), 0)), 0).toLocaleString('en-IN')}</strong>
          </div>
        </div>
      </section>

      <section className="stats-grid">
        {summaryCards.map(({ label, value, change, tone, icon: Icon }) => (
          <article key={label} className="stat-card">
            <div className="stat-header">
              <span>{label}</span>
              <div className={`chip ${tone}`}><Icon size={14} />{change}</div>
            </div>
            <strong>{value}</strong>
          </article>
        ))}
      </section>

      <section className="content-grid">
        <div className="panel">
          <div className="panel-header"><h3>Habit momentum</h3><button className="link-btn" onClick={() => navigate('/habits')}>View all</button></div>
          {loading ? <p className="empty-state">Loading data...</p> : habits.length === 0 ? (
            <p className="empty-state">No habits yet. Add your first habit to begin.</p>
          ) : (
            <div className="habit-list">
              {habits.map((habit) => (
                <div key={habit.id || habit.name} className="habit-row">
                  <div className="habit-main">
                    <div className="tiny-dot done" />
                    <div>
                      <strong>{habit.name}</strong>
                      <span>{habit.frequency || 'daily'}</span>
                    </div>
                  </div>
                  <div className="habit-meta">
                    <span>{habit.streak || 0} day streak</span>
                    <div className="progress-bar"><span style={{ width: `${habit.progress || 0}%` }} /></div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="panel">
          <div className="panel-header"><h3>Upcoming payments</h3><button className="link-btn" onClick={() => navigate('/transactions')}>Manage</button></div>
          <div className="list-stack">
            <p className="empty-state">No upcoming payments yet. Add recurring or scheduled payments to see them here.</p>
          </div>
        </div>
      </section>

      <section className="content-grid bottom-grid">
        <div className="panel">
          <div className="panel-header"><h3>Recent transactions</h3><button className="link-btn" onClick={exportTransactions}>Export</button></div>
          {transactions.length === 0 ? (
            <p className="empty-state">No transactions yet. Add your first one to see the cashflow.</p>
          ) : (
            <div className="transaction-list">
              {transactions.slice(0, 5).map((tx) => (
                <div key={tx.id || `${tx.description}-${tx.transaction_date}`} className="transaction-row">
                  <div className={`transaction-icon ${tx.type}`}>{tx.type === 'income' ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}</div>
                  <div className="tx-copy"><strong>{tx.description || tx.category}</strong><span>{tx.category} · {tx.transaction_date}</span></div>
                  <span className={`tx-amount ${tx.type}`}>{tx.type === 'income' ? '+' : '-'}₹{Number(tx.amount || 0).toLocaleString('en-IN')}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="panel">
          <div className="panel-header"><h3>Goal radar</h3><button className="link-btn" onClick={() => navigate('/goals')}>View goals</button></div>
          {goals.length === 0 ? (
            <p className="empty-state">No goals yet. Define the next big milestone.</p>
          ) : (
            <div className="goal-list">
              {goals.map((goal) => (
                <div key={goal.id || goal.title} className="goal-row">
                  <div className="goal-head"><strong>{goal.title}</strong><span>{goal.target_date}</span></div>
                  <div className="progress-bar"><span style={{ width: `${goal.progress || 50}%` }} /></div>
                  <div className="goal-balance"><span>{goal.description || 'In progress'}</span><span>{goal.progress || 50}%</span></div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </>
  )
}

function HabitsScreen({ habits, setHabits, token }) {
  const [form, setForm] = useState({ name: '', description: '', frequency: 'daily' })
  const [message, setMessage] = useState('')

  const handleChange = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }))

  const handleSubmit = async (event) => {
    event.preventDefault()
    setMessage('')
    try {
      const created = await apiFetch('/habits/', { method: 'POST', body: JSON.stringify(form) }, token)
      setHabits((current) => [...current, { ...created, progress: 0, streak: 0 }])
      setForm({ name: '', description: '', frequency: 'daily' })
      setMessage('Habit created successfully.')
    } catch (error) {
      setMessage(error.message)
    }
  }

  return (
    <section className="screen-panel">
      <div className="screen-header">
        <div><p className="eyebrow accent">Habits</p><h3>Consistency blueprint</h3></div>
      </div>

      <div className="dual-layout">
        <form className="entry-form" onSubmit={handleSubmit}>
          <label><span>Name</span><input name="name" value={form.name} onChange={handleChange} placeholder="Study AI" required /></label>
          <label><span>Description</span><input name="description" value={form.description} onChange={handleChange} placeholder="Minimum 1 hour" /></label>
          <label><span>Frequency</span><select name="frequency" value={form.frequency} onChange={handleChange}><option value="daily">Daily</option><option value="weekly">Weekly</option><option value="monthly">Monthly</option></select></label>
          {message && <div className="inline-alert">{message}</div>}
          <button type="submit" className="primary-btn">Add habit</button>
        </form>

        <div className="list-stack narrow">
          {habits.length === 0 ? (
            <p className="empty-state">No habits yet. Add your first habit above.</p>
          ) : (
            habits.map((habit) => (
              <div key={habit.id || habit.name} className="info-card compact">
                <div className="card-topline"><div className="label-pill">{habit.frequency || 'daily'}</div><CheckCircle2 size={18} className="success" /></div>
                <h4>{habit.name}</h4>
                <p>{habit.description || 'No description added yet.'}</p>
                <div className="progress-bar large"><span style={{ width: `${habit.progress || 0}%` }} /></div>
                <div className="card-foot"><span>{habit.progress || 0}% complete</span><span>{habit.streak || 0} day streak</span></div>
              </div>
            ))
          )}
        </div>
      </div>
    </section>
  )
}

function TransactionsScreen({ transactions, setTransactions, token }) {
  const [form, setForm] = useState({ amount: '', type: 'expense', category: 'food', description: '', transaction_date: new Date().toISOString().slice(0, 10) })
  const [message, setMessage] = useState('')

  const handleChange = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }))

  const handleSubmit = async (event) => {
    event.preventDefault()
    setMessage('')
    try {
      const created = await apiFetch('/transactions', { method: 'POST', body: JSON.stringify({ ...form, amount: Number(form.amount) }) }, token)
      setTransactions((current) => [created, ...current])
      setForm({ amount: '', type: 'expense', category: 'food', description: '', transaction_date: new Date().toISOString().slice(0, 10) })
      setMessage('Transaction added.')
    } catch (error) {
      setMessage(error.message)
    }
  }

  return (
    <section className="screen-panel">
      <div className="screen-header"><div><p className="eyebrow accent">Transactions</p><h3>Cashflow overview</h3></div></div>
      <div className="dual-layout">
        <form className="entry-form" onSubmit={handleSubmit}>
          <label><span>Amount</span><input name="amount" type="number" value={form.amount} onChange={handleChange} placeholder="1250" required /></label>
          <label><span>Type</span><select name="type" value={form.type} onChange={handleChange}><option value="expense">Expense</option><option value="income">Income</option></select></label>
          <label><span>Category</span><select name="category" value={form.category} onChange={handleChange}><option value="food">Food</option><option value="salary">Salary</option><option value="transport">Transport</option><option value="family">Family</option><option value="insurance">Insurance</option><option value="investment">Investment</option><option value="other">Other</option></select></label>
          <label><span>Description</span><input name="description" value={form.description} onChange={handleChange} placeholder="Dinner with team" /></label>
          <label><span>Transaction date</span><input name="transaction_date" type="date" value={form.transaction_date} onChange={handleChange} required /></label>
          {message && <div className="inline-alert">{message}</div>}
          <button type="submit" className="primary-btn">Add transaction</button>
        </form>

        <div className="list-stack narrow">
          {transactions.length === 0 ? (
            <p className="empty-state">No transactions yet. Add the first movement.</p>
          ) : (
            transactions.map((tx) => (
              <div key={tx.id || `${tx.description}-${tx.transaction_date}`} className="info-card compact">
                <div className="card-topline"><div className="label-pill">{tx.category}</div><div className={`transaction-icon ${tx.type}`}><ArrowUpRight size={15} /></div></div>
                <h4>{tx.description || tx.category}</h4>
                <p>{tx.transaction_date}</p>
                <div className="card-foot"><span>{tx.type}</span><span className={`tx-amount ${tx.type}`}>{tx.type === 'income' ? '+' : '-'}₹{Number(tx.amount || 0).toLocaleString('en-IN')}</span></div>
              </div>
            ))
          )}
        </div>
      </div>
    </section>
  )
}

function GoalsScreen({ goals, setGoals, token }) {
  const [form, setForm] = useState({ title: '', description: '', target_date: new Date(Date.now() + 86400000 * 30).toISOString().slice(0, 10) })
  const [message, setMessage] = useState('')

  const handleChange = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }))

  const handleSubmit = async (event) => {
    event.preventDefault()
    setMessage('')
    try {
      const created = await apiFetch('/goals/', { method: 'POST', body: JSON.stringify(form) }, token)
      setGoals((current) => [...current, { ...created, progress: 0 }])
      setForm({ title: '', description: '', target_date: new Date(Date.now() + 86400000 * 30).toISOString().slice(0, 10) })
      setMessage('Goal created successfully.')
    } catch (error) {
      setMessage(error.message)
    }
  }

  return (
    <section className="screen-panel">
      <div className="screen-header"><div><p className="eyebrow accent">Goals</p><h3>What you are building</h3></div></div>
      <div className="dual-layout">
        <form className="entry-form" onSubmit={handleSubmit}>
          <label><span>Title</span><input name="title" value={form.title} onChange={handleChange} placeholder="Learn FastAPI" required /></label>
          <label><span>Description</span><textarea name="description" value={form.description} onChange={handleChange} rows="4" placeholder="Become comfortable building production APIs" /></label>
          <label><span>Target date</span><input name="target_date" type="date" value={form.target_date} onChange={handleChange} required /></label>
          {message && <div className="inline-alert">{message}</div>}
          <button type="submit" className="primary-btn">Add goal</button>
        </form>

        <div className="list-stack narrow">
          {goals.length === 0 ? (
            <p className="empty-state">No goals yet. Set the next milestone.</p>
          ) : (
            goals.map((goal) => (
              <div key={goal.id || goal.title} className="info-card compact">
                <div className="card-topline"><div className="label-pill alt">Goal</div><TrendingUp size={18} className="muted" /></div>
                <h4>{goal.title}</h4>
                <p>{goal.description || 'No description provided yet.'}</p>
                <div className="progress-bar large"><span style={{ width: `${goal.progress || 0}%` }} /></div>
                <div className="card-foot"><span>{goal.target_date}</span><span>{goal.progress || 0}%</span></div>
              </div>
            ))
          )}
        </div>
      </div>
    </section>
  )
}

function ArchitectureScreen() {
  const layers = [
    { title: 'UI', detail: 'React + Vite dashboard, auth, forms, navigation' },
    { title: 'Routes', detail: 'FastAPI routers: /auth, /transactions, /habits, /goals, /dashboard' },
    { title: 'Schemas', detail: 'Pydantic validation for create/update/read payloads' },
    { title: 'In-memory store', detail: 'Module-level dicts for dev mode before real DB integration' },
  ]

  return (
    <section className="screen-panel architecture-panel">
      <div className="screen-header">
        <div><p className="eyebrow accent">Architecture</p><h3>Backend blueprint</h3></div>
        <img src="/GM-Logo3.png" alt="Geeky Monks icon" className="mini-logo" />
      </div>

      <div className="architecture-visual">
        <img src="/backend-architecture.svg" alt="GM Tracker backend architecture diagram" className="architecture-svg" />
      </div>

      <div className="architecture-diagram">
        {layers.map((block, idx) => (
          <div key={block.title} className="diagram-block">
            <div className="diagram-badge">{idx + 1}</div>
            <strong>{block.title}</strong>
            <span>{block.detail}</span>
          </div>
        ))}
      </div>

      <div className="diagram-notes">
        <div className="note"><CreditCard size={16} /> <span>Auth</span></div>
        <div className="note"><Gauge size={16} /> <span>Transactions</span></div>
        <div className="note"><Target size={16} /> <span>Goals</span></div>
        <div className="note"><Flame size={16} /> <span>Habits</span></div>
      </div>
    </section>
  )
}

export default App
