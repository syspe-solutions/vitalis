# Vitalis

MVP Django para testar o agendamento de pacientes com terapeutas. Estrutura inspirada no
padrão do `proage-interno` (separação `core/` + `apps/`, `BaseModelAbstract` com UUID e
auditoria de criação/atualização, `ModelAdmin` customizado, serviço de e-mail transacional),
reduzida ao módulo de agendamento + notificação.

## Domínio

- **Paciente** (`apps/scheduling/models/patient.py`): nome, email, data de nascimento.
- **Terapeuta** (`apps/scheduling/models/therapist.py`): nome, email, senha — é também o
  usuário autenticável do sistema (`AUTH_USER_MODEL`), login por email.
- **Agendamento** (`apps/scheduling/models/appointment.py`): relaciona paciente + terapeuta +
  data/horário da sessão + status (`Agendado`, `Remarcado`, `Concluído`, `Cancelado`).
- **Notificação por e-mail** (`apps/notification/models.py`): registro de cada e-mail
  disparado (destinatário, template, status de entrega), com envio síncrono logo após o
  commit da transação (`apps/notification/services/email_service.py`).

O fluxo de cadastro de paciente/terapeuta e a tela de agendamento são públicos. Editar
livremente qualquer campo é feito pelo **superusuário** via Django Admin (`/admin/`); cancelar
também pode ser feito direto na tela de agendamento (botão só aparece logado como superusuário).

### Notificações

Ao marcar um agendamento, o Vitalis dispara automaticamente dois e-mails (via
`AppointmentNotificationService`): confirmação para o paciente e aviso para o terapeuta. Sem
`DJANGO_EMAIL_HOST` configurado, o backend de e-mail cai para **console** — os e-mails aparecem
no terminal do `runserver`, então dá para testar o disparo sem precisar de um servidor SMTP.
Toda tentativa fica registrada em `EmailNotification` (visível em `/admin/`), com status
`Pendente` / `Enviado` / `Falhou`. Falha no envio não impede o agendamento — só fica logada.

## Estrutura

```
core/                    settings, urls, wsgi/asgi
apps/
  common/                 BaseModelAbstract (UUID + auditoria) e BaseModelAdminAbstract
  notification/           EmailNotification + EmailService (envio síncrono, sem Celery)
    services/
    web/templates/notification/email/
  scheduling/             módulo de agendamento
    models/               patient.py, therapist.py, appointment.py
    services/             appointment_notification_service.py
    admin.py
    web/
      urls.py
      views/               home, patients, therapists, appointments
      templates/scheduling/
        appointments/list.html   tela de agendamento (calendário FullCalendar + lista + modais)
```

Banco de dados: **SQLite** (`db.sqlite3`, gerado localmente, fora do controle de versão).

## Como rodar

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser   # pede nome, email e senha do terapeuta/admin
uv run python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` para o fluxo de agendamento e `http://127.0.0.1:8000/admin/`
para o painel administrativo (login com o email/senha do superusuário criado acima). O mesmo
login também vale para o site — faça login em `/admin/login/` e o botão "Cancelar Agendamento"
passa a aparecer na tela `/agendamentos/`.

Para enviar e-mails de verdade (em vez do backend de console), preencha as variáveis
`DJANGO_EMAIL_*` no `.env` (veja `.env.example`).

## Rotas principais

| Rota                        | Descrição                                                          |
|------------------------------|---------------------------------------------------------------------|
| `/`                          | Painel com próximos agendamentos                                    |
| `/pacientes/`                 | Lista de pacientes                                                   |
| `/pacientes/novo/`            | Cadastro de paciente                                                 |
| `/terapeutas/`                | Lista de terapeutas                                                  |
| `/terapeutas/novo/`           | Cadastro de terapeuta (nome, email, senha)                          |
| `/agendamentos/`              | **Tela de agendamento**: calendário (semana/dia/mês) + lista + modal de criação/detalhe |
| `/agendamentos/novo/`         | Formulário de agendamento standalone (fallback sem JS)              |
| `/agendamentos/<id>/cancelar/`| Cancela um agendamento (somente superusuário logado)                |
| `/admin/`                     | Django Admin — editar qualquer campo, remarcar, cancelar em massa   |
