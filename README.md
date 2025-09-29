# Verboo Feedback Assistant

Assistente de IA que coleta **feedbacks** de usuários e registra as respostas em uma tabela pública.  
A IA conversa com o usuário, coleta as informações e envia para o backend (Django), que **classifica** e **salva** o feedback.

## 🔗 Links públicos

- **IA (teste do avaliador):**  
  https://rita.verbeux.com.br/generative/5e274114-4504-4f1a-b15e-7e4edf83683d

- **Tabela de Feedbacks / Success (Render – plano free):**  
  https://verboo-test.onrender.com/feedbacks/success/  
  > ⚠️ Nota: este serviço está no **Render (free)** e pode estar **hibernando** quando você abrir.  
  > Se isso ocorrer, a página pode demorar alguns segundos para “acordar”. Abra o link e aguarde o carregamento.

---

## ✅ Rota de teste (super simples)

1. Abra a **IA**: https://rita.verbeux.com.br/generative/5e274114-4504-4f1a-b15e-7e4edf83683d  
2. Fale algo como: **“Quero fazer um feedback.”**  
   - Responda às perguntas que a IA fizer (mensagem, nome, e-mail, etc.).  
3. Abra a **Tabela de Feedbacks**: https://verboo-test.onrender.com/feedbacks/success/  
   - **Atualize a página** após enviar cada feedback para ver o novo registro.

> Dica: a listagem mostra contagem total e últimas entradas. Se você quiser ver o formulário manual do backend (sem IA), acesse:  
> `https://verboo-test.onrender.com/feedbacks/` → envie → confira em `/feedbacks/success/`.

---

## 🧱 Arquitetura (resumo)

- **Frontend de conversação (IA):** a conversa ocorre no link público acima.  
- **Backend (Django):** recebe os dados via **webhook** e salva os feedbacks.
- **Banco de Dados:** PostgreSQL (no Render) em produção.  
- **Página de sucesso:** lista os feedbacks e estatísticas.

### Principais endpoints

- **Formulário manual (opcional):** `GET /feedbacks/`  
- **Página de sucesso (lista):** `GET /feedbacks/success/`  
- **Webhook (IA → backend):** `POST /feedbacks/api/webhook/verboo/`  
  - `Content-Type: application/json`  
  - Campos aceitos:  
    ```json
    {
      "message": "string (obrigatório)",
      "name": "string",
      "email": "string",
      "franchise": "string",
      "classification": "elogio | reclamacao | compliment | complaint"
    }
    ```
  - O backend **normaliza** os valores; se `classification` não vier, o servidor faz o **fallback** para classificar.

---

## 🗂️ Estrutura do projeto (trecho)

```
.
├─ feedback_assistant/
│  ├─ settings.py            # Config por variáveis de ambiente (DEBUG, DATABASE_URL, etc.)
│  ├─ urls.py                # Inclui rotas do app `feedbacks`
│  └─ wsgi.py
├─ feedbacks/
│  ├─ templates/feedbacks/
│  │  ├─ feedback_form.html
│  │  └─ feedback_success.html
│  ├─ migrations/            # Migrações do Django
│  ├─ admin.py               # Admin do Django (visualização dos registros)
│  ├─ models.py              # Modelo Feedback
│  ├─ forms.py               # Formulário de envio manual (opcional)
│  ├─ utils.py               # Classificação e utilidades
│  ├─ views.py               # Views do form, success e webhook
│  └─ urls.py                # Rotas /feedbacks/..., /success/, /api/webhook/...
├─ manage.py
├─ requirements.txt
└─ Dockerfile (opcional, uso local)
```

### Modelo (resumo)
`Feedback(name, email, message, feedback_type, franchise, created_at)`  
- `feedback_type`: **compliment** | **complaint** (mapeado a partir de “elogio”, “reclamação”, etc.)  
- `created_at`: controle de ordem na listagem.

---

## 🧰 Requisitos

- **Produção (já rodando no Render):**
  - Django + Gunicorn
  - Postgres (DATABASE_URL)
  - WhiteNoise para estáticos
  - Variáveis de ambiente configuradas no Render (ver abaixo)

- **Execução local (opcional para dev):**
  - Python 3.12+
  - `pip`, `venv`
  - SQLite (padrão) ou Postgres (via `DATABASE_URL`)

---

## ▶️ Execução local (opcional)

```bash
# 1) criar venv e instalar deps
python -m venv .venv
# Windows: .\.venv\Scriptsctivate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt

# 2) (opcional) variáveis locais
# no padrão, roda com SQLite; se quiser Postgres, exporte DATABASE_URL

# 3) migrações e runserver
python manage.py migrate
python manage.py runserver

# 4) testar
# Form:       http://127.0.0.1:8000/feedbacks/
# Success:    http://127.0.0.1:8000/feedbacks/success/
# Webhook:    POST http://127.0.0.1:8000/feedbacks/api/webhook/verboo/
```

---

## 🌐 Deploy no Render (resumo)

1. **Web Service** (Runtime: **Python**)
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:**  
     `gunicorn feedback_assistant.wsgi:application --bind 0.0.0.0:$PORT`

2. **PostgreSQL** (Render → New → PostgreSQL)  
   - Copiar **External Database URL** (ou Internal, se preferir) em `DATABASE_URL`.

3. **Environment Variables** (no Web Service)
   - `SECRET_KEY` = (chave forte)
   - `DEBUG` = `0`
   - `DATABASE_URL` = `postgres://...` (do Postgres do Render)
   - `ALLOWED_HOSTS` = `verboo-test.onrender.com`
   - `CSRF_TRUSTED_ORIGINS` = `https://verboo-test.onrender.com`
   - `DB_SSL_REQUIRE` = `1`  (use `0` se for conectar via Internal URL)
   - `DB_CONN_MAX_AGE` = `600`
   - (opcionais) `LANGUAGE_CODE= en-us`, `TIME_ZONE= America/Fortaleza`

4. **Migrações/estáticos sem shell pago**  
   No **Start Command** (apenas no primeiro deploy ou quando necessário):
   ```bash
   python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn feedback_assistant.wsgi:application --bind 0.0.0.0:$PORT
   ```

---

## 🔍 Troubleshooting

- **Página de success em 500**: normalmente é falta de migração.  
  Garanta `DATABASE_URL` correto e rode `migrate` (vide Start Command acima).

- **Webhook 404/405**: confirme a rota **com barra final**  
  `/feedbacks/api/webhook/verboo/` e método **POST**.

- **403/400 no Render**: revise `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS` com **exatamente** o domínio `verboo-test.onrender.com`.

- **Serviço “hibernando”**: é comportamento do **plano free** do Render. Abra a URL e aguarde a aplicação inicializar.

---

## 🔒 Observações de segurança
- Não comitar **`db.sqlite3`** ao repositório (use `.gitignore`).  
- Armazenar **`SECRET_KEY`** e **`DATABASE_URL`** apenas em **variáveis de ambiente**.  
- Ao criar usuário admin para demonstração, utilize credenciais **de teste**.

---

## 📝 Licença
Projeto de teste técnico. Uso educacional/demonstração.
