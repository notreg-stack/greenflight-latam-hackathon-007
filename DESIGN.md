# DESIGN.md — CO²mpensa Aí

Identidade derivada do logo oficial (`frontend/public/logo.png`): círculo de setas azul → verde → laranja, avião, folha, árvore, coração e mão. Fundo branco/claro. Tagline: **Compense sua pegada com um clique**.

## Tokens
| Token | Valor | Uso |
|---|---|---|
| `--bg` | `#F5F9FC` | fundo da página (claro, como o logo) |
| `--panel` / `--panel2` | `#FFFFFF` / `#EEF4F9` | cartões e campos |
| `--line` | `#D8E3EE` | bordas |
| `--ink` | `#173B5C` | texto principal (azul-marinho do wordmark) |
| `--muted` | `#5C7188` | texto secundário |
| `--blue` | `#1E6FB5` | marca, títulos, códigos de aeroporto, KPIs (o "voo") |
| `--green` | `#2E9E5B` | ação primária, compensação, selo A, "escolha verde" (a "folha") |
| `--orange` | `#F28C28` | destaque do checkout verde, selo D, avisos (o "sol/ação") |
| `--amber` / `--red` | `#E6A100` / `#D9534F` | selos C e E |

## Regras
- Semântica de carbono é sempre a escala A–E (verde → vermelho); azul nunca significa "bom" ou "ruim", só marca.
- Um único botão primário verde por bloco; laranja aparece como borda/realce, não como botão.
- Logo em 64 px no cabeçalho e 28 px no rodapé; favicon é o mesmo PNG (`frontend/public/favicon.png`).
- "CO²" sempre com o 2 sobrescrito em verde no wordmark; no texto corrido, "CO₂".
- Cantos 10–14 px, sombras suaves azuladas (`rgba(23,59,92,.05–.2)`), sem gradientes fortes além da barra de ocupação (verde → laranja).
- Tipografia do sistema (-apple-system, Segoe UI, Roboto); pesos 800 para números e wordmark, 600 para nomes de rota.
- Tabelas com cabeçalho em `--panel2`, caixa alta pequena, números alinhados à esquerda para leitura rápida.

## Base
Copiado de `~/.claude/designs/airbnb.DESIGN.md` (consumidor/viagem) e sobrescrito pelos tokens acima. Em conflito, este arquivo vence.
