import { useEffect, useState } from 'react'
import './App.css'

const DATES = ['2015-06-02', '2015-06-03', '2015-06-04', '2015-06-05', '2015-06-06', '2015-06-07', '2015-06-08']
const api = (path, opts) => fetch(path, opts).then(r => r.json())
const post = (path, body) => api(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
const cap = s => (s || '').toLowerCase().replace(/(^|\s)\S/g, t => t.toUpperCase())
const fmt = s => s.slice(11, 16)
const day = s => s.slice(8, 10) + '/' + s.slice(5, 7)

function Airport({ label, value, onPick }) {
  const [q, setQ] = useState(value?.label || '')
  const [opts, setOpts] = useState([])
  useEffect(() => { if (value?.label) setQ(value.label) }, [value])
  useEffect(() => {
    if (q.length < 2 || (value && q === value.label)) { setOpts([]); return }
    const t = setTimeout(() => api(`/api/airports?q=${encodeURIComponent(q)}`).then(setOpts), 200)
    return () => clearTimeout(t)
  }, [q])
  return (
    <div className="field">
      <label>{label}</label>
      <input value={q} placeholder="cidade ou código" onChange={e => { setQ(e.target.value); onPick(null) }} />
      {opts.length > 0 && <ul className="opts">{opts.map(o => <li key={o.airport_id} onClick={() => { onPick(o); setQ(o.label); setOpts([]) }}>{o.label}</li>)}</ul>}
    </div>
  )
}

export default function App() {
  const [view, setView] = useState('passenger')
  const [origin, setOrigin] = useState(null)
  const [dest, setDest] = useState(null)
  const [date, setDate] = useState('')
  const [sort, setSort] = useState('co2')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [suggested, setSuggested] = useState([])
  const [stats, setStats] = useState(null)
  const [health, setHealth] = useState(null)
  const [buying, setBuying] = useState(null)
  const [receipt, setReceipt] = useState(null)
  const [explain, setExplain] = useState('')
  const [pref, setPref] = useState('Quero ajudar florestas brasileiras')
  const [rec, setRec] = useState(null)
  const [offset, setOffset] = useState(null)
  const [esg, setEsg] = useState(null)
  const [greenest, setGreenest] = useState([])
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState(null)

  const refresh = () => { api('/api/stats').then(setStats); api('/api/esg').then(setEsg) }
  useEffect(() => { api('/api/routes/suggested').then(setSuggested); api('/api/health').then(setHealth); api('/api/routes/greenest').then(setGreenest); refresh() }, [])

  const runSearch = async (o = origin, d = dest, dt = date) => {
    if (!o && !d) return
    setLoading(true)
    const p = new URLSearchParams()
    if (o) p.set('origin', o.airport_id); if (d) p.set('destination', d.airport_id); if (dt) p.set('date', dt)
    setData(await api(`/api/search?${p}`)); setLoading(false); refresh()
  }
  const pickRoute = r => {
    const o = { airport_id: r.from_id, label: cap(r.from_city) }, d = { airport_id: r.to_id, label: cap(r.to_city) }
    setOrigin(o); setDest(d); setDate(''); setReceipt(null); setRec(null); setOffset(null); runSearch(o, d, '')
  }
  const results = (data?.results || []).slice().sort((a, b) => sort === 'co2' ? a.per_pax_kg - b.per_pax_kg : sort === 'price' ? a.price - b.price : a.departure.localeCompare(b.departure))

  const buy = async e => {
    e.preventDefault()
    const f = new FormData(e.target)
    const alternatives = results.filter(r => r.flight_id !== buying.flight_id).map(r => r.flight_id)
    const r = await post('/api/purchase', { flight_id: buying.flight_id, passenger_name: f.get('name'), email: f.get('email'), alternatives })
    setReceipt(r); setBuying(null); setRec(null); setOffset(null); setExplain(''); refresh()
    api(`/api/explain?flight_id=${buying.flight_id}&alternatives=${alternatives.join(',')}`).then(x => setExplain(x.text))
    runSearch()
  }
  const recommend = async () => { setRec({ loading: true }); setRec(await post('/api/carbon/projects/recommend', { preference: pref, flight_id: receipt.flight.flight_id, co2_kg: receipt.co2_kg })) }
  const confirmOffset = async projectId => {
    const r = await post('/api/carbon/offset', { flight_id: receipt.flight.flight_id, project_id: projectId, passenger_key: receipt.passenger_key, co2_kg: receipt.co2_kg, preference: pref, purchase_id: receipt.purchase_id })
    setOffset(r); refresh()
  }
  const ask = async e => { e.preventDefault(); setAnswer({ answer: '…' }); setAnswer(await post('/api/ask', { question })) }

  return (
    <div className="app">
      <header>
        <div className="brand"><span className="leaf">✈︎</span> GreenFlight <small>escolha o assento que custa menos carbono e compense o resto no checkout</small></div>
        <div className="kpis">
          <div><b>{stats?.n ?? 0}</b><span>passagens</span></div>
          <div><b>{esg?.co2_offset_kg ?? 0} kg</b><span>CO₂ compensados</span></div>
          <div><b>{esg?.green_points_issued ?? 0}</b><span>Green Points</span></div>
          <div className={health?.db === 'tidb' ? 'ok' : 'warn'}><b>{health?.db === 'tidb' ? 'TiDB Cloud' : 'modo local'}</b><span>{health?.bedrock ? 'Bedrock on' : 'Bedrock off'}</span></div>
          <button className={view === 'airline' ? 'on' : ''} onClick={() => setView(view === 'airline' ? 'passenger' : 'airline')}>{view === 'airline' ? '← passageiro' : 'Dashboard ESG'}</button>
        </div>
      </header>

      {view === 'airline' && esg && (
        <section className="esg">
          <h2>GreenFlight · ESG Dashboard da companhia</h2>
          <div className="grid">
            <div><b>{Math.round(esg.adoption_rate * 100)}%</b><span>Carbon Offset Adoption</span></div>
            <div><b>{esg.co2_offset_kg} kg</b><span>CO₂ compensado</span></div>
            <div><b>{esg.participants}</b><span>passageiros participantes</span></div>
            <div><b>{esg.projects}</b><span>projetos ambientais</span></div>
            <div><b>{esg.green_points_issued}</b><span>Green Points distribuídos</span></div>
            <div><b>R$ {esg.amount_brl}</b><span>destinado a projetos</span></div>
          </div>
          <div className="two">
            <div><h3>Projetos mais escolhidos</h3><table><tbody>{esg.top_projects.map(t => <tr key={t.name}><td>{t.name}</td><td>{t.offsets}×</td><td>{t.co2_kg} kg</td></tr>)}{!esg.top_projects.length && <tr><td>ainda sem compensações</td></tr>}</tbody></table></div>
            <div><h3>Adesão por rota</h3><table><tbody>{esg.by_route.map(t => <tr key={t.route}><td>{t.route}</td><td>{t.offsets}×</td><td>{t.co2_kg} kg</td></tr>)}{!esg.by_route.length && <tr><td>ainda sem compensações</td></tr>}</tbody></table></div>
          </div>
          <h3>Rotas mais limpas da semana (kg CO₂ por passageiro, ocupação real)</h3>
          <table><thead><tr><th>Rota</th><th>Voos</th><th>kg CO₂/pax</th><th>Preço médio</th></tr></thead><tbody>{greenest.map(g => <tr key={g.route}><td>{g.route}</td><td>{g.flights}</td><td>{g.avg_kg}</td><td>R$ {g.avg_price}</td></tr>)}</tbody></table>
        </section>
      )}

      {view === 'passenger' && (<>
        <section className="search">
          <Airport label="Origem" value={origin} onPick={setOrigin} />
          <Airport label="Destino" value={dest} onPick={setDest} />
          <div className="field"><label>Data (semana do dataset)</label>
            <select value={date} onChange={e => setDate(e.target.value)}><option value="">qualquer dia</option>{DATES.map(d => <option key={d} value={d}>{day(d)}/2015</option>)}</select></div>
          <button className="primary" disabled={loading || (!origin && !dest)} onClick={() => runSearch()}>{loading ? 'buscando…' : 'Buscar voos'}</button>
        </section>
        {suggested.length > 0 && <div className="chips"><span>Rotas com voos na semana:</span>{suggested.map(r => <button key={r.from_id + '-' + r.to_id} onClick={() => pickRoute(r)}>{cap(r.from_city)} → {cap(r.to_city)} <em>{r.n}×</em></button>)}</div>}

        {receipt && (
          <section className="checkout">
            <div className="receipt">
              <h3>✓ Passagem confirmada · {receipt.flight.flightno} · {receipt.flight.from.city} → {receipt.flight.to.city} · {receipt.passenger_name}</h3>
              <p>R$ {receipt.flight.price.toFixed(2)} · <b>{receipt.co2_kg} kg CO₂</b> por passageiro (selo {receipt.label}) · você evitou <b>{receipt.co2_avoided_kg} kg</b> escolhendo este voo · ocupação agora {Math.round(receipt.flight.occupancy * 100)}%{receipt.s3_key ? ' · recibo no S3' : ''}</p>
              <p className="ai">{explain || 'Gerando explicação com Bedrock…'}</p>
            </div>
            {!offset ? (
              <div className="offer">
                <h3>🌱 Torne sua viagem mais verde</h3>
                <div className="big">{receipt.co2_kg} kg CO₂ <small>estimados para o seu assento</small></div>
                <p>Compense por <b>R$ {receipt.offset_quote.offset_price.toFixed(2)}</b> e ganhe <b>+{receipt.offset_quote.green_points} Green Points</b></p>
                <label>Que tipo de projeto você gostaria de apoiar?</label>
                <div className="row"><input value={pref} onChange={e => setPref(e.target.value)} /><button className="primary" onClick={recommend} disabled={rec?.loading}>{rec?.loading ? 'buscando…' : 'Recomendar projeto'}</button></div>
                {rec && !rec.loading && (
                  <div className="projects">
                    <p className="meta">busca: {rec.engine === 'tidb-vector' ? 'TiDB Vector Search (EMBED_TEXT)' : 'busca local por palavras'} · recomendação: {rec.bedrock ? 'Amazon Bedrock (Claude)' : 'regra local'}</p>
                    {rec.projects.map(p => (
                      <div key={p.id} className={`project ${rec.recommended?.project_id === p.id ? 'rec' : ''}`}>
                        <div><b>{p.name}</b> <span className="meta">{p.country} · {p.project_type.replace('_', ' ').toLowerCase()} · R$ {p.price_per_ton}/t</span><p>{p.description}</p>
                          {rec.recommended?.project_id === p.id && <p className="ai">IA recomenda: {rec.recommended.short_reason}</p>}</div>
                        <button className="primary" onClick={() => confirmOffset(p.id)}>Compensar</button>
                      </div>))}
                  </div>)}
              </div>
            ) : (
              <div className="rewards">
                <h3>VIAGEM MAIS VERDE · +{offset.green_points} Green Points</h3>
                <p>Compensação de <b>{offset.co2_kg} kg CO₂</b> por <b>R$ {offset.offset_price.toFixed(2)}</b> no projeto <b>{offset.project}</b>.</p>
                <div className="grid">
                  <div><b>{offset.wallet.total_points}</b><span>pontos na carteira</span></div>
                  <div><b>{offset.wallet.next_benefit.points_needed}</b><span>pontos até: {offset.wallet.next_benefit.benefit}</span></div>
                  <div><b>{offset.wallet.total_co2_offset} kg</b><span>CO₂ compensados por você</span></div>
                  <div><b>{offset.wallet.offsets}</b><span>viagens compensadas</span></div>
                </div>
                {offset.wallet.unlocked.length > 0 && <p className="meta">benefícios liberados: {offset.wallet.unlocked.join(', ')}</p>}
              </div>
            )}
          </section>
        )}

        {data && (
          <section className="results">
            <div className="bar"><span>{data.count} voos{data.widened_to_week ? ' (sem voo na data; mostrando a semana)' : ''}</span>
              <div className="sort">ordenar por{[['co2', 'carbono'], ['price', 'preço'], ['time', 'horário']].map(([k, v]) => <button key={k} className={sort === k ? 'on' : ''} onClick={() => setSort(k)}>{v}</button>)}</div></div>
            {results.map(r => (
              <article key={r.flight_id} className={`card L${r.label}`}>
                <div className="col route">
                  <div className="codes">{r.from.code} <i>→</i> {r.to.code}</div>
                  <div className="cities">{r.from.city} → {r.to.city}</div>
                  <div className="meta">{day(r.departure)} · {fmt(r.departure)}–{fmt(r.arrival)} · {Math.floor(r.duration_min / 60)}h{String(r.duration_min % 60).padStart(2, '0')} · {r.distance_km} km</div>
                  <div className="meta">{r.airline} · {r.flightno} · {r.aircraft}</div>
                </div>
                <div className="col occ">
                  <div className="occbar"><span style={{ width: `${Math.round(r.occupancy * 100)}%` }} /></div>
                  <div className="meta">{Math.round(r.occupancy * 100)}% ocupado · {r.seats_left} assentos livres</div>
                  <div className="meta">após sua compra: {r.per_pax_kg_after_purchase} kg/pax</div>
                </div>
                <div className="col co2">
                  <div className="badge">{r.label}</div>
                  <div className="kg"><b>{r.per_pax_kg}</b> kg CO₂/pax</div>
                  <div className="meta">≈ {r.trees_year_equivalent} árvores/ano · evita {r.co2_avoided_vs_worst} kg vs pior opção</div>
                  <div className="tags">{r.is_greenest && <span className="green">escolha verde</span>}{r.is_cheapest && <span className="cheap">menor preço</span>}</div>
                </div>
                <div className="col price"><div className="money">R$ {r.price.toFixed(2)}</div><button className="primary" onClick={() => setBuying(r)} disabled={r.seats_left <= 0}>Comprar</button></div>
              </article>))}
          </section>
        )}

        <section className="ask">
          <form onSubmit={ask}><input value={question} onChange={e => setQuestion(e.target.value)} placeholder="Pergunte ao GreenFlight: por que voo cheio emite menos por pessoa?" /><button className="primary" type="submit">Perguntar</button></form>
          {answer && <div className="answer"><p>{answer.answer}</p>{answer.sources?.length > 0 && <small>fontes ({answer.vector ? 'busca vetorial TiDB' : 'busca local'}): {answer.sources.map(s => s.topic).join(', ')}</small>}</div>}
        </section>
      </>)}

      {buying && (
        <div className="modal" onClick={() => setBuying(null)}>
          <form onClick={e => e.stopPropagation()} onSubmit={buy}>
            <h3>Comprar {buying.flightno} · {buying.from.city} → {buying.to.city}</h3>
            <p>{buying.per_pax_kg_after_purchase} kg CO₂ por passageiro com você a bordo · R$ {buying.price.toFixed(2)}</p>
            <input name="name" placeholder="nome do passageiro" required /><input name="email" placeholder="e-mail (identifica sua carteira Green Points)" type="email" />
            <div className="row"><button type="button" onClick={() => setBuying(null)}>cancelar</button><button className="primary" type="submit">Confirmar compra</button></div>
          </form>
        </div>
      )}
      <footer>GreenFlight · time latam-hackathon-007 · dataset airportdb (junho/2015) · emissão por assento-km e ocupação em tempo real · TiDB Cloud (SQL + Vector) · Amazon Bedrock · EC2 · S3 · Kiro</footer>
    </div>
  )
}
