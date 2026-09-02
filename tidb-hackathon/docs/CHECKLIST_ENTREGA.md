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
| TiDB Cloud Starter em sa-east-1 | 10 | `backend/db.py` conecta com TLS; DDL automático | Feito 02/09 21:10–21:40: cluster `co2mpensa-ai` (sa-east-1), dump importado via `scripts/import_airportdb.py` (12 tabelas, 0 erros), app em modo TiDB. |
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
## Bedrock: por que "erro de credencial" quase sempre é região errada (análise do briefing)
O briefing avisa: a chave do time foi emitida para `ap-southeast-1`; apontar o cliente para `sa-east-1` (ou qualquer outra região) devolve **erro de autenticação ou acesso negado**, nunca uma mensagem de "região errada". Como o console e a EC2 estão em São Paulo, é natural alguém criar o cliente sem região e herdar `sa-east-1` do ambiente. O que fizemos para esse erro não existir aqui:

1. **Região fixa no código.** `backend/bedrock.py` cria o cliente com `region_name="ap-southeast-1"` explícito; `AWS_REGION` do `.env` não decide nada para o Bedrock. O S3 usa `sa-east-1` explícito pelo mesmo motivo (o prefixo do time está em São Paulo).
2. **Credenciais separadas.** A chave do documento veio como par `ACCESS_KEY_ID`/`SECRET_ACCESS_KEY`; guardamos em `BEDROCK_ACCESS_KEY_ID`/`BEDROCK_SECRET_ACCESS_KEY` e passamos só ao cliente do Bedrock. Se fosse `AWS_ACCESS_KEY_ID`, o boto3 usaria a chave (que só tem permissão de Bedrock) também para o S3 na EC2 e derrubaria a role da instância.
3. **Sintoma parecido que não é região.** Uma linha `AWS_BEARER_TOKEN_BEDROCK=` vazia no `.env` faz o boto3 (≥ 1.39) tentar autenticação bearer e falhar com `IncompleteSignatureException: Authorization header requires 'Credential'`. Parece erro de credencial, mas é a variável vazia. O código apaga a variável quando está vazia; o `.env.example` a deixa comentada.
4. **Autoteste antes da demo.** `./.venv/bin/python -c "import bedrock; print(bedrock.selftest())"` imprime região do cliente, modo de credencial, `AWS_REGION` do ambiente e a resposta do modelo. Se falhar, a mensagem já classifica: variável vazia, região/chave, ou modelo inexistente (`ValidationException`: Titan e Mistral não existem em Singapura).
5. **Se ainda negar com a região certa:** falta o formulário de primeiro uso dos modelos Anthropic no console do Bedrock da conta, ou a chave é de outro time. O desvio do briefing vale: qualquer outra API de LLM mantém os 60 pontos da Parte A.

Resultado verificado em 02/09: `OK Bedrock ap-southeast-1 · credencial: par de chaves do time`.