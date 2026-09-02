# Checklist de entrega · time latam-hackathon-007

Mapeado do briefing "Ask the Airport" e do documento de credenciais. Ordem = ordem de execução. Quem faz: uma pessoa por linha.

## Antes de tudo (documento de credenciais)
- [ ] Login no console `https://tidb-latam-hackathon.signin.aws.amazon.com/console` com o usuário `latam-hackathon-007` e a senha temporária da tabela "AWS Account". Trocar a senha (14+ caracteres, maiúscula, minúscula, número, símbolo).
- [ ] **Cadastrar MFA** imediatamente (menu do usuário → Security credentials → Assign MFA device). Sem MFA a organização não libera a chave.
- [ ] A chave do Bedrock do time está na tabela "Bedrock API Keys", linha `latam-hackathon-007`, região `ap-southeast-1`. Vai para `BEDROCK_ACCESS_KEY_ID` e `BEDROCK_SECRET_ACCESS_KEY` no `backend/.env`. **Nunca em commit, README, screenshot ou Dockerfile.** Não compartilhar com outro time.
- [ ] O documento de credenciais lista todos os times: não o coloque no repositório nem em nenhuma pasta do projeto.

## Parte B · 40 pontos verificados no repositório
| Item | Pts | Status no código | O que o time ainda faz |
|---|---|---|---|
| TiDB Cloud Starter em sa-east-1 | 10 | `backend/db.py` conecta com TLS; DDL automático | Criar cluster Starter (AWS · São Paulo), **Import from S3** do dump pelo console, preencher `TIDB_HOST/USER/PASSWORD` no `.env`. Não restringir IP. |
| Busca vetorial (VECTOR + VEC_COSINE_DISTANCE ou EMBED_TEXT) | 8 | `carbon_project.embedding` e `eco_knowledge.emb` gerados por `EMBED_TEXT`; consulta em `backend/greenflight.py` e `backend/db.py`; referência `sql/setup_tidb.sql` | Rodar uma vez com TiDB e conferir no SQL Editor: `SELECT name FROM carbon_project ORDER BY VEC_COSINE_DISTANCE(embedding, EMBED_TEXT('tidbcloud_free/amazon/titan-embed-text-v2','florestas brasileiras')) LIMIT 3;` |
| Amazon Bedrock (ap-southeast-1) | 8 | `backend/bedrock.py`: Claude 3 Haiku (explicação e recomendação), Sonnet e Cohere disponíveis | Feito: chave do time no `.env` local, `bedrock.selftest()` respondeu OK em ap-southeast-1 |
| Publicado na AWS (EC2 sa-east-1) | 8 | `deploy.sh`, porta 8000, bind 0.0.0.0, `setsid nohup` | Session Manager → `bash deploy.sh` → anotar o IP público (muda a cada stop/start) no `SUBMISSION.md` |
| Construído com Kiro (.kiro/) | 6 | `.kiro/specs/greenflight/`, `.kiro/steering/`, `.kiro/hooks/`, `.kiro/settings/mcp.json` commitados | Abrir a pasta no Kiro e continuar por lá (as tarefas 8–11 do `tasks.md`) |

## Parte A · 60 pontos ao vivo
- Funciona (20): demo local já roda; com TiDB e Bedrock ligados fica completa.
- Inovação (15): carbono por assento com ocupação em tempo real + compensação com projeto escolhido por vetor + rewards.
- Valor de negócio (15): nomeie a usuária (Ana) e a companhia (dashboard ESG).
- Demo e pitch (10): roteiro em `docs/ARQUITETURA_GREENFLIGHT.md` seções 39–40; mostre, não descreva.

## Submissão (2:05 em diante)
- [x] Repositório **público** do time no GitHub: https://github.com/notreg-stack/greenflight-latam-hackathon-007 (a pasta `projects/latam-hackathon-007` do repositório principal não é usada, segundo `projects/README.md`).
- [ ] `SUBMISSION.md` na raiz, template exato, caixinhas só do que existe, "Onde olhar" com caminhos reais.
- [ ] `.env` fora do repo (`.gitignore` já cobre), `.env.example` dentro.
- [ ] Push de tudo **antes** de comentar. A organização forka no fechamento e o fork não sincroniza.
- [ ] Um comentário na issue "Entregas": Time · Repositório (público) · Demo (vídeo de 2 min ou URL no ar) · Pitch em uma linha.

## Se algo quebrar (tabela do briefing)
- `AccessDeniedException` no Bedrock → região não é `ap-southeast-1`, ou falta o formulário de primeiro uso dos modelos Anthropic no console do Bedrock.
- `ValidationException` modelo não suportado → use os IDs de `backend/bedrock.py`; Titan e Mistral não existem em Singapura.
- SSL no TiDB → `TIDB_SSL_CA=/etc/pki/tls/certs/ca-bundle.crt` na EC2.
- App não abre → bind 0.0.0.0, porta 8000; conferir IP público atual.
- Import lento → Import from S3 no console do TiDB Cloud.
- Sem tempo para publicar → rode local, grave o vídeo, submeta. Oito pontos não valem uma entrega perdida.
