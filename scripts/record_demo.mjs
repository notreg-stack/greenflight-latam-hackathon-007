// Grava o vídeo de demo do GreenFlight com Playwright (Chromium headless, 1280x800).
// Uso: node scripts/record_demo.mjs [http://localhost:8787] → docs/demo/greenflight-demo.webm
import { createRequire } from 'node:module'
import { mkdirSync, readdirSync, renameSync } from 'node:fs'
const require = createRequire(new URL('../frontend/package.json', import.meta.url))   // playwright vive em frontend/node_modules
const { chromium } = require('playwright')

const BASE = process.argv[2] || 'http://localhost:8787'
const OUT = new URL('../docs/demo/', import.meta.url).pathname
mkdirSync(OUT, { recursive: true })

const browser = await chromium.launch()
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 }, recordVideo: { dir: OUT, size: { width: 1280, height: 800 } }, locale: 'pt-BR' })
const page = await ctx.newPage()
const t0 = Date.now()
const log = m => console.log(`${((Date.now() - t0) / 1000).toFixed(1)}s  ${m}`)
const pause = ms => page.waitForTimeout(ms)

// legenda no canto inferior, para o vídeo contar a história mesmo sem áudio
const caption = async text => page.evaluate(t => {
  let el = document.getElementById('__cap')
  if (!el) { el = document.createElement('div'); el.id = '__cap'; document.body.appendChild(el)
    Object.assign(el.style, { position: 'fixed', left: '24px', right: '24px', bottom: '20px', zIndex: 9999, background: 'rgba(8,20,14,.92)', color: '#e9f1ec', border: '1px solid #3ddc84', borderRadius: '10px', padding: '12px 16px', font: '600 18px/1.4 -apple-system, Segoe UI, Roboto, sans-serif' }) }
  el.textContent = t
}, text)

await page.goto(BASE); await pause(1500)
await caption('GreenFlight · Ana quer viajar. Ela vai escolher o assento pela pegada de carbono, não só pelo preço.'); log('abertura'); await pause(5000)

await page.getByRole('button', { name: /Aalen-heidenheim → Votuporanga/i }).click(); await pause(2500)
await caption('Cada voo mostra kg de CO₂ por passageiro com a ocupação real, selo A–E, preço e horário. A lista já vem ordenada por carbono.'); log('busca'); await pause(6000)
await page.mouse.wheel(0, 300); await pause(2500)
await page.getByRole('button', { name: 'preço' }).click(); await caption('Ordenar por preço mostra o trade-off: o mais barato nem sempre é o mais limpo.'); await pause(4500)
await page.getByRole('button', { name: 'carbono' }).click(); await page.mouse.wheel(0, -300); await pause(1500)
await caption('Escolha verde: o voo mais cheio da rota. Quem compra entra no denominador e a emissão por pessoa cai em tempo real.'); await pause(5000)

await page.getByRole('button', { name: 'Comprar' }).first().click(); await pause(1200)
await page.getByPlaceholder('nome do passageiro').fill('Ana Ribeiro'); await page.getByPlaceholder(/e-mail/).fill('ana@exemplo.com'); await pause(1200)
await page.getByRole('button', { name: 'Confirmar compra' }).click(); log('compra')
await caption('Compra confirmada. O recibo diz quanto CO₂ Ana evitou contra a pior opção e a ocupação já atualizada.'); await pause(4000)
await page.waitForFunction(() => document.querySelector('.receipt .ai')?.textContent && !document.querySelector('.receipt .ai').textContent.includes('Gerando'), null, { timeout: 30000 }).catch(() => {})
await caption('A explicação é gerada pelo Amazon Bedrock (Claude) com os números do TiDB: aeronave, ocupação e distância.'); await pause(7000)

await page.locator('.offer').scrollIntoViewIfNeeded(); await pause(1000)
await caption('Checkout verde: compensar por poucos reais e ganhar Green Points. Ana descreve o projeto que quer apoiar.'); await pause(4500)
const pref = page.locator('.offer input'); await pref.fill(''); await pref.pressSequentially('Quero ajudar florestas brasileiras', { delay: 45 }); await pause(800)
await page.getByRole('button', { name: 'Recomendar projeto' }).click(); log('recomendar')
await page.waitForSelector('.project', { timeout: 30000 })
await caption('TiDB Vector Search (EMBED_TEXT) encontra os projetos mais próximos da frase; o Bedrock escolhe um e explica por quê.'); await pause(7500)
await page.locator('.project.rec button, .project button').first().click(); log('compensar')
await page.waitForSelector('.rewards', { timeout: 20000 })
await caption('Viagem mais verde: +Green Points na carteira, próximo benefício, CO₂ compensado e viagens compensadas.'); await pause(6500)

await page.getByRole('button', { name: 'Dashboard ESG' }).click(); await pause(1500); await page.mouse.wheel(0, -1000)
await caption('Para a companhia: adesão à compensação, CO₂ compensado, projetos mais escolhidos, adesão por rota e a análise do airportdb inteiro por trecho, com valor por tonelada.'); log('esg'); await pause(8000)
await page.mouse.wheel(0, 500); await pause(5000)
await page.mouse.wheel(0, -1000); await pause(500)
await caption('TiDB Cloud São Paulo: SQL, vetor e analytics na mesma base · Bedrock Singapura · EC2 · S3 · specs no Kiro. Próximo passo: API de emissão por trecho para motores de busca.'); await pause(14000)

await ctx.close(); await browser.close()
const f = readdirSync(OUT).find(n => n.endsWith('.webm') && !n.startsWith('greenflight'))
if (f) renameSync(OUT + f, OUT + 'greenflight-demo.webm')
log('vídeo salvo em docs/demo/greenflight-demo.webm')
