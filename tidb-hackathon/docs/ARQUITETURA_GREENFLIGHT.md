# GreenFlight — Carbon Offset + Green Rewards + IA

## Hackathon AWS + TiDB

GreenFlight é uma aplicação para integrar compensação de carbono diretamente ao checkout de uma passagem aérea.

A solução combina:

- compensação estimada das emissões de CO₂ da viagem;
- recomendação de projetos ambientais por IA;
- busca semântica com TiDB Vector Search;
- programa de fidelidade `Green Rewards`;
- geração de indicadores ESG;
- dashboard para companhia aérea;
- AWS para infraestrutura e IA;
- TiDB Cloud para armazenamento transacional, analítico e vetorial.

A ideia central é transformar sustentabilidade em uma experiência simples para o passageiro e em uma fonte de dados, engajamento e diferenciação para a companhia aérea.

> **Não queremos apenas calcular carbono. Queremos transformar a escolha sustentável do passageiro em impacto ambiental mensurável, recompensa e dados de negócio.**

---

# 1. Problema

Atualmente, comprar uma passagem aérea é simples. Entender e compensar o impacto ambiental dessa viagem não é.

Em muitos casos, a compensação de carbono:

- está fora do fluxo principal de compra;
- é pouco explicada;
- não gera benefício direto ao passageiro;
- não está conectada a projetos ambientais específicos;
- não utiliza personalização;
- não se transforma em dados úteis para a companhia aérea;
- é percebida como doação ou custo adicional, em vez de experiência de produto.

Isso reduz a adesão e limita o valor ambiental e empresarial da iniciativa.

---

# 2. Solução

O GreenFlight inclui a compensação diretamente no checkout.

Fluxo principal:

```text
Passageiro compra passagem
        ↓
Sistema identifica voo e rota
        ↓
Calcula emissão estimada de CO₂
        ↓
Oferece compensação no checkout
        ↓
Passageiro informa preferência ambiental
        ↓
TiDB Vector Search encontra projetos compatíveis
        ↓
Amazon Bedrock explica/recomenda o melhor projeto
        ↓
Passageiro confirma compensação
        ↓
Green Points são creditados
        ↓
Dados alimentam Dashboard ESG
```

---

# 3. Proposta de valor

## 3.1 Para o passageiro

O passageiro recebe:

- estimativa do impacto de carbono da viagem;
- possibilidade de compensação em poucos cliques;
- recomendação personalizada de projeto ambiental;
- transparência sobre o destino da contribuição;
- Green Points;
- benefícios futuros;
- histórico de impacto ambiental;
- experiência de compra mais alinhada com sustentabilidade.

## 3.2 Para a companhia aérea

A companhia passa a capturar dados sobre:

- percentual de passageiros que compensam carbono;
- toneladas de CO₂ compensadas;
- valor destinado a projetos ambientais;
- projetos mais escolhidos;
- adesão por rota;
- adesão por aeroporto;
- adesão por perfil de passageiro;
- recorrência;
- Green Points distribuídos;
- Green Points utilizados;
- indicadores ESG;
- comportamento ambiental dos passageiros.

---

# 4. Loop de negócio

```text
Passageiro
    ↓
Compensação
    ↓
Green Points
    ↓
Benefício
    ↓
Maior engajamento
    ↓
Maior recorrência
    ↓
Mais dados
    ↓
Melhores recomendações
    ↓
Maior adesão
```

Do lado da companhia:

```text
Mais adesão
    ↓
Mais recursos destinados a projetos ambientais
    ↓
Mais indicadores ESG
    ↓
Mais transparência
    ↓
Melhor percepção de marca
    ↓
Maior capacidade de demonstrar iniciativas ambientais
```

A aplicação não deve afirmar que compensação de carbono provoca diretamente valorização das ações da companhia.

A tese mais defensável é:

> melhores métricas ambientais + transparência + engajamento podem contribuir para reputação, diferenciação, relacionamento com investidores, narrativa ESG e fidelização.

---

# 5. Arquitetura geral

```text
                         ┌─────────────────────┐
                         │      FRONTEND       │
                         │   React + Vite      │
                         │                     │
                         │ Checkout da viagem  │
                         │ Carbon Impact       │
                         │ Green Rewards       │
                         └──────────┬──────────┘
                                    │
                                    │ REST API
                                    ▼
                         ┌─────────────────────┐
                         │       BACKEND       │
                         │   Node.js/NestJS    │
                         │                     │
                         │ Flights             │
                         │ Carbon Calculation  │
                         │ Rewards             │
                         │ AI                  │
                         └──────┬───────┬──────┘
                                │       │
                    SQL         │       │ Bedrock
                                │       │
                                ▼       ▼
                       ┌────────────┐ ┌─────────────┐
                       │    TiDB    │ │   AWS       │
                       │   Cloud    │ │  Bedrock    │
                       │            │ │             │
                       │ Flights    │ │ Claude      │
                       │ Passengers │ │ Embeddings  │
                       │ Bookings   │ └─────────────┘
                       │ Carbon     │
                       │ Rewards    │
                       │ Projects   │
                       └────────────┘
```

---

# 6. Frontend

## Stack recomendado

```text
React
Vite
TypeScript
Tailwind CSS
Axios
React Query (opcional)
```

Para o hackathon, o objetivo é reduzir complexidade.

Não é necessário construir um portal completo de companhia aérea.

O MVP pode ter apenas três experiências principais:

1. Checkout;
2. Compensação;
3. Green Rewards.

Uma quarta tela, o Dashboard ESG, entra se houver tempo.

---

# 7. Tela 1 — Checkout

Exemplo:

```text
✈️ SUA VIAGEM

São Paulo (GRU)
       ↓
Frankfurt (FRA)
       ↓
Londres (LHR)

Passagem             R$ 4.280
Bagagem              R$   180
─────────────────────────────
Total                 R$ 4.460


🌱 TORNE SUA VIAGEM MAIS VERDE

Sua viagem emitirá aproximadamente:

        1.240 kg
          CO₂

[ ] Compensar minha emissão

R$ 12,40

        +100 Green Points

[ Continuar ]
```

Essa deve ser a principal tela da demonstração.

---

# 8. Tela 2 — Escolha do projeto ambiental

Ao selecionar a compensação:

```text
┌─────────────────────────────────────┐
│ COMPENSE SUA VIAGEM                 │
│                                     │
│ Emissão estimada                    │
│                                     │
│          1.240 kg CO₂               │
│                                     │
│ Valor da compensação                │
│          R$ 12,40                   │
│                                     │
│ Projeto recomendado pela IA         │
│                                     │
│ Amazon Reforestation                │
│                                     │
│ "Este projeto corresponde à sua     │
│ preferência por reflorestamento     │
│ realizado no Brasil."               │
│                                     │
│ +100 Green Points                   │
│                                     │
│ [ Compensar viagem ]                │
└─────────────────────────────────────┘
```

Campo opcional:

```text
Que tipo de projeto você gostaria de apoiar?

[ Quero ajudar florestas brasileiras              ]
```

Esse texto será utilizado na busca vetorial.

---

# 9. Tela 3 — Green Rewards

Após a confirmação:

```text
        VIAGEM MAIS VERDE

        +100 Green Points

        Total: 850 pontos

────────────────────────────

Você está a 150 pontos de:

Upgrade de categoria

────────────────────────────

Impacto acumulado:

4.820 kg CO₂ compensados

7 viagens compensadas
```

---

# 10. Green Rewards

Exemplo de mecânica:

```text
500 pontos
→ desconto em bagagem

1.000 pontos
→ prioridade de embarque

2.000 pontos
→ lounge / upgrade / voucher
```

No hackathon, esses benefícios podem ser simulados.

O mecanismo central é:

```text
Compensação
    ↓
Pontos
    ↓
Benefício
    ↓
Recorrência
```

---

# 11. Dashboard da companhia aérea

Exemplo:

```text
GREENFLIGHT — ESG DASHBOARD

Carbon Offset Adoption
74%

CO₂ Compensado
159.200 toneladas

Passageiros participantes
128.430

Projetos ambientais
24

Green Points distribuídos
8.200.000
```

Outras métricas:

```text
Adesão por rota
Adesão por aeroporto
Adesão por faixa de preço
CO₂ por rota
Valor arrecadado
Projetos mais escolhidos
Passageiros recorrentes
Taxa de utilização dos Green Points
Conversão da oferta de compensação
Ticket médio de compensação
```

---

# 12. Backend

## Stack recomendado

```text
Node.js
NestJS
TypeScript
mysql2
AWS SDK
```

Estrutura sugerida:

```text
src/
│
├── flights/
│   ├── flights.controller.ts
│   ├── flights.service.ts
│   └── flights.repository.ts
│
├── carbon/
│   ├── carbon.controller.ts
│   ├── carbon.service.ts
│   └── carbon.repository.ts
│
├── rewards/
│   ├── rewards.controller.ts
│   └── rewards.service.ts
│
├── ai/
│   ├── ai.controller.ts
│   └── ai.service.ts
│
├── projects/
│   ├── projects.controller.ts
│   └── projects.service.ts
│
├── analytics/
│   ├── analytics.controller.ts
│   └── analytics.service.ts
│
└── database/
    └── database.service.ts
```

---

# 13. Responsabilidades do backend

O backend deve realizar:

```text
1. Buscar booking
2. Buscar passageiro
3. Buscar voo
4. Buscar aeroportos
5. Estimar CO₂
6. Calcular preço da compensação
7. Consultar projetos ambientais
8. Realizar Vector Search
9. Chamar Amazon Bedrock
10. Registrar compensação
11. Distribuir Green Points
12. Atualizar wallet do passageiro
13. Alimentar analytics
```

---

# 14. APIs

## 14.1 Buscar viagem

```http
GET /api/bookings/:id
```

Resposta:

```json
{
  "bookingId": "ABC123",
  "passenger": {
    "id": 456,
    "name": "Paul"
  },
  "flights": [
    {
      "flight": "LA8080",
      "origin": "GRU",
      "destination": "FRA"
    },
    {
      "flight": "LH123",
      "origin": "FRA",
      "destination": "LHR"
    }
  ]
}
```

---

## 14.2 Calcular carbono

```http
POST /api/carbon/calculate
```

Request:

```json
{
  "flightId": 123,
  "passengerId": 456
}
```

Resposta:

```json
{
  "co2Kg": 1240,
  "offsetPrice": 12.40,
  "greenPoints": 100
}
```

---

## 14.3 Buscar projetos

```http
GET /api/carbon/projects
```

Exemplo:

```http
GET /api/carbon/projects?preference=reflorestamento+brasil
```

---

## 14.4 Recomendar projeto

```http
POST /api/carbon/projects/recommend
```

Request:

```json
{
  "preference": "Quero ajudar florestas brasileiras"
}
```

Resposta:

```json
{
  "projectId": 12,
  "name": "Amazon Reforestation",
  "reason": "Projeto mais alinhado à preferência por reflorestamento no Brasil."
}
```

---

## 14.5 Fazer compensação

```http
POST /api/carbon/offset
```

Request:

```json
{
  "bookingId": "ABC123",
  "projectId": 12,
  "amount": 12.40
}
```

Resposta:

```json
{
  "success": true,
  "offsetId": 837,
  "greenPoints": 100
}
```

---

## 14.6 Recomendação por IA

```http
POST /api/ai/recommendation
```

Request:

```json
{
  "bookingId": "ABC123",
  "preference": "Quero apoiar reflorestamento no Brasil"
}
```

---

# 15. Armazenamento — TiDB

O banco original pode continuar contendo as tabelas fornecidas pelo AirportDB.

Estrutura conceitual:

```text
airportdb
│
├── flight
├── flightschedule
├── booking
├── passenger
├── airport
├── weatherdata
│
├── carbon_project
├── carbon_offset
├── green_reward
└── green_wallet
```

A recomendação é não alterar as tabelas originais do dataset.

Criar tabelas adicionais para o GreenFlight.

---

# 16. Tabela `carbon_project`

```sql
CREATE TABLE carbon_project (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    country VARCHAR(100),
    project_type VARCHAR(100),
    price_per_ton DECIMAL(10,2),
    embedding VECTOR(1024)
);
```

Campos:

```text
id
name
description
country
project_type
price_per_ton
embedding
```

Exemplo:

```text
1
Amazon Reforestation
Projeto de reflorestamento e recuperação florestal
Brazil
REFORESTATION
10.00
[vector]
```

---

# 17. Tabela `carbon_offset`

```sql
CREATE TABLE carbon_offset (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    booking_id BIGINT NOT NULL,
    passenger_id BIGINT NOT NULL,
    project_id BIGINT NOT NULL,
    co2_kg DECIMAL(12,2),
    amount DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# 18. Tabela `green_reward`

```sql
CREATE TABLE green_reward (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    passenger_id BIGINT NOT NULL,
    offset_id BIGINT,
    points INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# 19. Tabela `green_wallet`

```sql
CREATE TABLE green_wallet (
    passenger_id BIGINT PRIMARY KEY,
    total_points INT DEFAULT 0,
    lifetime_points INT DEFAULT 0,
    total_co2_offset DECIMAL(14,2) DEFAULT 0
);
```

---

# 20. Modelo relacional

```text
Passenger
   │
   ├──────────────┐
   │              │
   ▼              ▼
Booking      Green Wallet
   │
   ▼
Flight
   │
   ▼
Carbon Offset
   │
   ├──────────────┐
   ▼              ▼
Carbon Project  Green Reward
```

---

# 21. Cálculo de CO₂

Para o MVP, o cálculo pode ser simplificado.

Exemplo conceitual:

```text
CO₂ estimado =
distância do voo
×
fator médio de emissão
```

Ou:

```text
emission_kg =
distance_km × emission_factor
```

Exemplo de código:

```javascript
const emissionKg = distanceKm * 0.115;
```

O fator acima é apenas ilustrativo para o MVP.

Para uma aplicação real, o cálculo deveria considerar:

- modelo da aeronave;
- combustível;
- ocupação;
- classe;
- distância;
- taxiamento;
- metodologia de cálculo;
- fatores de emissão;
- radiative forcing;
- provider dos créditos.

---

# 22. Distância entre aeroportos

Se o dataset possuir latitude e longitude, a distância pode ser calculada com Haversine.

```text
Airport A
latitude / longitude
        ↓
Haversine
        ↓
Airport B
latitude / longitude
        ↓
distância em km
```

Fórmula conceitual:

```text
a =
sin²(Δφ/2) +
cos φ1 × cos φ2 × sin²(Δλ/2)

c =
2 × atan2(√a, √(1-a))

distance =
R × c
```

Onde:

```text
R ≈ 6371 km
```

---

# 23. Preço da compensação

Exemplo:

```text
CO₂ da viagem
1,24 toneladas

Preço do crédito
R$ 10 / tonelada

Valor da compensação
R$ 12,40
```

Fórmula:

```text
offset_price =
(co2_kg / 1000)
× carbon_credit_price
```

---

# 24. TiDB Vector Search

Um dos diferenciais da aplicação é permitir que o passageiro descreva o impacto ambiental que deseja apoiar.

Exemplo:

```text
"Quero apoiar recuperação de florestas brasileiras."
```

A frase pode ser convertida em embedding e comparada com os projetos ambientais.

Consulta conceitual:

```sql
SELECT
    id,
    name,
    description,
    country,
    project_type
FROM carbon_project
ORDER BY VEC_COSINE_DISTANCE(
    embedding,
    EMBED_TEXT(
       'tidbcloud_free/amazon/titan-embed-text-v2',
       'Quero ajudar florestas brasileiras'
    )
)
LIMIT 3;
```

Resultado esperado:

```text
1. Amazon Reforestation
2. Atlantic Forest Recovery
3. Brazilian Biodiversity Corridor
```

---

# 25. Papel do Amazon Bedrock

O Bedrock não precisa calcular valores determinísticos.

O backend deve calcular:

- CO₂;
- preço;
- pontos;
- disponibilidade;
- ranking inicial por similaridade.

O Bedrock deve atuar em:

- recomendação;
- explicação;
- personalização;
- geração de texto;
- interpretação da preferência do passageiro.

Fluxo:

```text
Backend
   ↓
Vector Search
   ↓
Top 3 projetos
   ↓
Bedrock
   ↓
Recomendação explicada
```

---

# 26. Exemplo de prompt para Bedrock

```text
You are an environmental project recommendation assistant
for an airline carbon-offset program.

Passenger preference:

"Quero projetos de reflorestamento no Brasil."

Available projects:

1. Amazon Reforestation
Country: Brazil
Type: Reforestation

2. Solar Energy Northeast
Country: Brazil
Type: Renewable Energy

3. Forest Conservation Peru
Country: Peru
Type: Conservation

Recommend the project most aligned with the passenger's
preference.

Respond in Portuguese.

Return:

- recommended_project
- short_reason
```

---

# 27. Resposta esperada da IA

```json
{
  "recommended_project": "Amazon Reforestation",
  "short_reason": "É o projeto que melhor corresponde à preferência por reflorestamento localizado no Brasil."
}
```

---

# 28. Arquitetura AWS

Arquitetura mínima:

```text
AWS
│
├── EC2
│    ├── nginx
│    ├── frontend
│    └── backend
│
├── Bedrock
│    └── Claude
│
└── S3
     └── datasets / arquivos
```

---

# 29. Deploy

Na EC2:

```text
EC2
│
├── nginx
│
├── /frontend
│
└── /backend
```

Fluxo:

```text
Internet
   ↓
Nginx
   ↓
React
   ↓
NestJS
   ↓
TiDB Cloud
   ↓
Amazon Bedrock
```

---

# 30. Variáveis de ambiente

Exemplo:

```env
PORT=3000

TIDB_HOST=
TIDB_PORT=4000
TIDB_USER=
TIDB_PASSWORD=
TIDB_DATABASE=airportdb

AWS_REGION=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

BEDROCK_MODEL_ID=
```

Nunca versionar credenciais reais no GitHub.

Adicionar ao `.gitignore`:

```text
.env
.env.local
node_modules/
dist/
```

---

# 31. Fluxo técnico completo

```text
PASSAGEIRO
    │
    ▼
React / Checkout
    │
    ▼
NestJS API
    │
    ├───────────────► TiDB
    │                   │
    │                   ├── Booking
    │                   ├── Passenger
    │                   ├── Flight
    │                   ├── Airport
    │                   ├── Carbon Projects
    │                   └── Green Rewards
    │
    ▼
Carbon Calculator
    │
    ▼
CO₂ estimado
    │
    ▼
Preço da compensação
    │
    ▼
Preferência do passageiro
    │
    ▼
TiDB Vector Search
    │
    ▼
Top projetos
    │
    ▼
Amazon Bedrock
    │
    ▼
Explicação/recomendação
    │
    ▼
Usuário confirma
    │
    ▼
carbon_offset
    │
    ▼
green_reward
    │
    ▼
green_wallet
    │
    ▼
Dashboard ESG
```

---

# 32. MVP obrigatório

O MVP deve proteger um único loop:

```text
Checkout
    ↓
Calcular CO₂
    ↓
Mostrar compensação
    ↓
Selecionar/recomendar projeto
    ↓
Confirmar
    ↓
Adicionar Green Points
```

Se esse fluxo estiver funcionando ponta a ponta, o projeto já é demonstrável.

---

# 33. Prioridade de implementação

## Prioridade 1 — Essencial

```text
Checkout
Carbon calculation
TiDB connection
Carbon project
Carbon offset
Green Points
```

## Prioridade 2 — Diferencial

```text
Vector Search
Bedrock recommendation
```

## Prioridade 3 — Demo visual

```text
Dashboard ESG
Histórico do passageiro
Gamificação
```

## Prioridade 4 — Nice to have

```text
Ranking
Badges
Animações
Analytics avançado
Comparação de rotas
```

---

# 34. Divisão de trabalho — time de 5 pessoas

| Pessoa | Responsabilidade |
|---|---|
| Pessoa 1 | Frontend / Checkout |
| Pessoa 2 | Backend / APIs |
| Pessoa 3 | TiDB / SQL / Dataset |
| Pessoa 4 | Bedrock + Vector Search |
| Pessoa 5 | Integração + Dashboard + Pitch |

---

# 35. Estratégia de implementação

## Pessoa 1 — Frontend

Responsável por:

```text
Checkout
Modal de compensação
Tela Green Rewards
Dashboard opcional
```

Pode trabalhar inicialmente com mocks.

---

## Pessoa 2 — Backend

Responsável por:

```text
NestJS
Controllers
Services
APIs
Carbon calculator
Integração final
```

---

## Pessoa 3 — TiDB

Responsável por:

```text
Conexão
SQL
Tabelas GreenFlight
Queries
AirportDB
Vector columns
Seed dos projetos ambientais
```

---

## Pessoa 4 — IA

Responsável por:

```text
Amazon Bedrock
Prompt
Vector Search
Recomendação
Resposta estruturada
```

---

## Pessoa 5 — Integração e pitch

Responsável por:

```text
Dashboard
Testes
Deploy
README
Pitch
Demo
Backup da demo
```

---

# 36. Dados mockados para projetos ambientais

Exemplo:

```json
[
  {
    "name": "Amazon Reforestation",
    "country": "Brazil",
    "type": "REFORESTATION",
    "description": "Recuperação de áreas degradadas e reflorestamento."
  },
  {
    "name": "Atlantic Forest Recovery",
    "country": "Brazil",
    "type": "REFORESTATION",
    "description": "Recuperação de áreas da Mata Atlântica."
  },
  {
    "name": "Solar Energy Northeast",
    "country": "Brazil",
    "type": "RENEWABLE_ENERGY",
    "description": "Expansão de geração solar."
  },
  {
    "name": "Forest Conservation Peru",
    "country": "Peru",
    "type": "CONSERVATION",
    "description": "Conservação de áreas florestais."
  }
]
```

---

# 37. Diferencial da solução

A solução não é apenas:

```text
"Quer pagar R$ 10 para compensar carbono?"
```

Ela transforma o checkout em:

```text
Impacto calculado
        +
Escolha personalizada
        +
Projeto ambiental
        +
IA
        +
Recompensa
        +
Dados ESG
```

Isso cria uma proposta mais forte para o usuário e para a companhia aérea.

---

# 38. Posicionamento

## Frase central

> **O passageiro viaja. A empresa cresce. E o impacto ambiental é transformado em ação mensurável.**

Alternativa:

> **GreenFlight transforma compensação de carbono em uma experiência de produto.**

Alternativa mais direta:

> **Sustentabilidade integrada ao checkout, não escondida em um relatório ESG.**

---

# 39. Pitch de 30 segundos

> Hoje, comprar uma passagem é simples, mas entender e compensar o impacto ambiental da viagem não é.  
> O GreenFlight integra a compensação diretamente ao checkout. Calculamos a emissão estimada do voo, usamos TiDB Vector Search para encontrar projetos ambientais alinhados à preferência do passageiro e Amazon Bedrock para explicar a melhor recomendação.  
> Ao compensar, o passageiro recebe Green Points e benefícios. Para a companhia aérea, cada escolha gera dados ambientais e indicadores ESG mensuráveis.

---

# 40. Pitch de 2 minutos

## 0:00–0:20 — Problema

> Comprar uma passagem leva segundos. Compensar o impacto ambiental ainda é complexo, pouco transparente e pouco incentivado.

## 0:20–0:45 — Checkout

Mostrar:

```text
Seu voo emitirá aproximadamente:
1.240 kg CO₂

Compensar por R$ 12,40
+100 Green Points
```

## 0:45–1:10 — IA + Vector Search

Passageiro escreve:

```text
"Quero ajudar florestas brasileiras."
```

Aplicação retorna:

```text
Amazon Reforestation
Projeto recomendado para você.
```

Explicar:

> A busca semântica acontece no TiDB e o Bedrock transforma o resultado em uma recomendação compreensível.

## 1:10–1:30 — Rewards

Usuário confirma:

```text
+100 Green Points
```

Mostrar:

```text
850 pontos
150 pontos até o próximo benefício
```

## 1:30–1:50 — Companhia aérea

Mostrar dashboard:

```text
74% de adesão
159K toneladas compensadas
128K passageiros participantes
```

## 1:50–2:00 — Fechamento

> GreenFlight transforma sustentabilidade em uma experiência de produto para o passageiro e em dados de negócio para a companhia aérea.

---

# 41. Perguntas que a banca pode fazer

## "Como vocês calculam o carbono?"

Resposta:

> Para o MVP utilizamos uma estimativa baseada em distância e fator médio de emissão. Em produção, o motor pode incorporar modelo da aeronave, ocupação, classe, combustível e metodologias oficiais.

## "Vocês vendem créditos de carbono?"

Resposta:

> No MVP simulamos a associação da compensação a projetos ambientais. Em produção, a solução poderia integrar provedores certificados de créditos.

## "Onde entra a IA?"

Resposta:

> A IA interpreta a intenção do passageiro e explica a recomendação. O TiDB Vector Search localiza semanticamente os projetos mais relevantes e o Bedrock produz a recomendação final.

## "Por que usar TiDB?"

Resposta:

> Porque precisamos combinar dados relacionais de voos, passageiros, bookings e compensações com busca vetorial sobre projetos ambientais em uma única plataforma.

## "Qual o valor para a companhia aérea?"

Resposta:

> A companhia aumenta o engajamento com iniciativas ambientais, captura métricas ESG, conhece as preferências dos passageiros e cria um novo loop de fidelidade através dos Green Points.

---

# 42. Roadmap pós-hackathon

## Fase 1

```text
Carbon checkout
Green Points
Projeto recomendado
Dashboard básico
```

## Fase 2

```text
Integração com provedores de créditos
Certificados
Wallet ambiental
Histórico detalhado
```

## Fase 3

```text
Personalização por passageiro
Recomendação preditiva
Dynamic incentives
Segmentação ESG
```

## Fase 4

```text
Marketplace de projetos
Corporate travel
APIs B2B
Relatórios ESG automatizados
```

---

# 43. Oportunidades futuras

A arquitetura pode evoluir para:

### Dynamic Green Incentives

A companhia pode variar a recompensa de acordo com:

- rota;
- horário;
- demanda;
- emissão estimada;
- perfil do passageiro;
- projeto;
- campanha ESG.

Exemplo:

```text
GRU → FRA

Compense hoje:
+250 Green Points
```

---

# 44. Personalização futura

O sistema pode aprender preferências:

```text
Passageiro A
→ prefere reflorestamento

Passageiro B
→ prefere energia renovável

Passageiro C
→ prefere biodiversidade
```

Em compras futuras, o checkout pode automaticamente priorizar projetos relevantes.

---

# 45. Modelos analíticos futuros

Com volume suficiente de dados, podem ser aplicados:

- propensity models;
- uplift modeling;
- collaborative filtering;
- contextual bandits;
- survival analysis;
- customer lifetime value;
- clustering de passageiros;
- recommendation systems;
- causal inference;
- Bayesian optimization;
- reinforcement learning para incentivos.

Exemplo de problema:

```text
Qual benefício aumenta mais a probabilidade
de compensação para cada tipo de passageiro?
```

Isso transforma Green Rewards em uma plataforma de otimização de comportamento, e não apenas em um programa fixo de pontos.

---

# 46. Métricas principais

## North Star Metric

Uma possível North Star:

```text
Toneladas de CO₂ compensadas por 1.000 passageiros
```

ou:

```text
Carbon Offset Adoption Rate
```

## Métricas secundárias

```text
Offset conversion rate
CO₂ compensated
Average offset value
Green Points issued
Green Points redeemed
Repeat offset rate
Project selection rate
AI recommendation acceptance rate
Revenue per passenger
Retention of participants
```

---

# 47. Eventos para analytics

O frontend pode gerar eventos:

```text
checkout_opened
carbon_offer_viewed
carbon_offset_selected
project_preference_entered
project_recommended
project_selected
carbon_offset_confirmed
green_points_awarded
reward_viewed
reward_redeemed
```

Isso permite medir o funil:

```text
Checkout
   ↓
Oferta visualizada
   ↓
Offset selecionado
   ↓
Projeto selecionado
   ↓
Offset confirmado
```

---

# 48. Exemplo de KPI funnel

```text
10.000 checkouts
    ↓
9.200 viram a oferta
    ↓
3.000 selecionaram compensação
    ↓
2.500 escolheram projeto
    ↓
2.200 confirmaram

Conversion Rate = 22%
```

---

# 49. Segurança e integridade

Para uma implementação real:

- nunca armazenar segredo AWS no frontend;
- usar IAM Roles;
- manter credenciais somente no backend;
- validar inputs;
- parametrizar queries SQL;
- evitar SQL injection;
- usar HTTPS;
- auditar compensações;
- registrar transações;
- associar cada crédito a um projeto verificável;
- prevenir dupla contabilização;
- manter trilha de auditoria.

---

# 50. Estrutura sugerida do repositório

```text
greenflight/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── hooks/
│   └── package.json
│
├── backend/
│   ├── src/
│   │   ├── flights/
│   │   ├── carbon/
│   │   ├── rewards/
│   │   ├── projects/
│   │   ├── ai/
│   │   ├── analytics/
│   │   └── database/
│   └── package.json
│
├── database/
│   ├── schema.sql
│   └── seed.sql
│
├── docs/
│   └── architecture.md
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

# 51. MVP final recomendado

A demonstração ideal deve conseguir executar:

```text
1. Abrir checkout
2. Carregar voo
3. Calcular CO₂
4. Mostrar preço da compensação
5. Usuário escrever preferência ambiental
6. TiDB Vector Search retornar projetos
7. Bedrock recomendar um projeto
8. Usuário confirmar
9. Registrar carbon_offset
10. Adicionar Green Points
11. Mostrar confirmação
12. Mostrar Dashboard ESG
```

Esse é o loop completo.

---

# 52. Resumo executivo

GreenFlight transforma a compensação de carbono em uma camada integrada à experiência de compra de uma passagem aérea.

A arquitetura proposta é:

```text
Frontend
React + Vite + TypeScript
        ↓
Backend
Node.js + NestJS
        ↓
TiDB Cloud
Dados relacionais + Vector Search
        ↓
Amazon Bedrock
Recomendação e explicação
        ↓
AWS EC2
Deploy
```

A aplicação entrega três benefícios simultâneos:

```text
PASSAGEIRO
→ conveniência + recompensa

MEIO AMBIENTE
→ financiamento de projetos

COMPANHIA AÉREA
→ dados + engajamento + indicadores ESG
```

O foco do hackathon deve ser construir um único loop funcional e demonstrável:

> **Checkout → CO₂ → Compensação → Projeto recomendado → Green Points → Dashboard.**

Esse fluxo é suficiente para comunicar claramente o valor técnico e empresarial da solução.

---

# 53. Tagline

> **GreenFlight — turn every flight into measurable climate action.**

Ou:

> **GreenFlight — sustentabilidade integrada à jornada, do checkout ao impacto.**

