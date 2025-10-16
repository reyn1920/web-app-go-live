import { useEffect, useState } from 'react'

const API_BASE = 'http://localhost:8080/api'

interface Tenant {
  id: string
  name: string
}

interface Channel {
  id: string
  title: string
  youtube_channel_id?: string
}

interface Video {
  id: string
  title: string
  status: string
}

function App() {
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [selectedTenant, setSelectedTenant] = useState<string>('')
  const [channels, setChannels] = useState<Channel[]>([])
  const [videos, setVideos] = useState<Video[]>([])

  // Fetch tenants on mount
  useEffect(() => {
    fetch(`${API_BASE}/tenants`)
      .then((r) => r.json())
      .then(setTenants)
      .catch(console.error)
  }, [])

  // Fetch channels when tenant selected
  useEffect(() => {
    if (!selectedTenant) return
    fetch(`${API_BASE}/channels`, {
      headers: { 'X-Tenant-Id': selectedTenant },
    })
      .then((r) => r.json())
      .then(setChannels)
      .catch(console.error)
  }, [selectedTenant])

  // Fetch videos when tenant selected
  useEffect(() => {
    if (!selectedTenant) return
    fetch(`${API_BASE}/videos`, {
      headers: { 'X-Tenant-Id': selectedTenant },
    })
      .then((r) => r.json())
      .then(setVideos)
      .catch(console.error)
  }, [selectedTenant])

  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui' }}>
      <h1>🐵 MonkeyPaw V5 Desktop</h1>

      <section style={{ margin: '2rem 0' }}>
        <h2>Select Tenant</h2>
        <select
          value={selectedTenant}
          onChange={(e) => setSelectedTenant(e.target.value)}
          style={{ padding: '0.5rem', fontSize: '1rem', width: '300px' }}
        >
          <option value="">-- Select Tenant --</option>
          {tenants.map((t) => (
            <option key={t.id} value={t.id}>
              {t.name}
            </option>
          ))}
        </select>
      </section>

      {selectedTenant && (
        <>
          <section style={{ margin: '2rem 0' }}>
            <h2>Channels ({channels.length})</h2>
            <ul>
              {channels.map((c) => (
                <li key={c.id}>
                  <strong>{c.title}</strong>
                  {c.youtube_channel_id && ` - YT: ${c.youtube_channel_id}`}
                </li>
              ))}
            </ul>
          </section>

          <section style={{ margin: '2rem 0' }}>
            <h2>Videos ({videos.length})</h2>
            <ul>
              {videos.map((v) => (
                <li key={v.id}>
                  <strong>{v.title}</strong> - Status: {v.status}
                </li>
              ))}
            </ul>
          </section>
        </>
      )}

      {!selectedTenant && (
        <p style={{ color: '#666', marginTop: '2rem' }}>
          Select a tenant to view channels and videos
        </p>
      )}
    </div>
  )
}

export default App

