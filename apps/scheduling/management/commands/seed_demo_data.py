import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.scheduling.models import (
    Anamnesis,
    Appointment,
    BehavioralGoal,
    BehavioralRecord,
    Patient,
    Therapist,
)

DEMO_DOMAIN = "vitalis.demo"
DEMO_PASSWORD = "Demo123!"
SESSION_NOTES = [
    "Sessão produtiva, boa adesão às atividades propostas.",
    "Início de sessão com resistência, melhora após atividade preferida.",
    "Generalização observada em novo contexto.",
    "Necessário mais suporte físico nas tentativas iniciais.",
    "Ótima resposta a reforçador social.",
]

THERAPISTS = [
    {"name": "Dra. Camila Duarte", "email": f"camila.duarte@{DEMO_DOMAIN}", "superuser": True},
    {"name": "Rafael Nogueira", "email": f"rafael.nogueira@{DEMO_DOMAIN}", "superuser": False},
    {"name": "Ana Beatriz Lima", "email": f"ana.lima@{DEMO_DOMAIN}", "superuser": False},
]

PATIENTS = [
    {
        "name": "Miguel Alves",
        "birth_date": "2019-04-12",
        "responsible_name": "Fernanda Alves",
        "responsible_relationship": "Mãe",
        "diagnosis": "TEA Nível 2 (CID F84.0)",
        "chief_complaint": "Atraso de linguagem e dificuldade de responder ao ser chamado.",
        "goals": [
            ("Responder ao nome em até 3s", BehavioralGoal.MeasurementType.PERCENTAGE, 30, 85),
            ("Crises de birra por sessão", BehavioralGoal.MeasurementType.FREQUENCY, 9, 2),
        ],
    },
    {
        "name": "Laura Ferreira",
        "birth_date": "2020-08-03",
        "responsible_name": "Patrícia Ferreira",
        "responsible_relationship": "Mãe",
        "diagnosis": "TEA Nível 1 (CID F84.0)",
        "chief_complaint": "Dificuldade de manter contato visual e brincar com pares.",
        "goals": [
            ("Contato visual espontâneo", BehavioralGoal.MeasurementType.PERCENTAGE, 25, 70),
            ("Atenção sustentada em atividade dirigida (min)", BehavioralGoal.MeasurementType.DURATION, 4, 15),
        ],
    },
    {
        "name": "Heitor Souza",
        "birth_date": "2017-11-20",
        "responsible_name": "Juliana Souza",
        "responsible_relationship": "Mãe",
        "diagnosis": "TEA Nível 2 (CID F84.0)",
        "chief_complaint": "Dificuldade em seguir instruções simples e desregulação frequente.",
        "goals": [
            ("Seguir instrução de 1 passo", BehavioralGoal.MeasurementType.PERCENTAGE, 40, 90),
            ("Nível de regulação emocional (1-5)", BehavioralGoal.MeasurementType.INTENSITY, 2, Decimal("4.5")),
        ],
    },
    {
        "name": "Valentina Castro",
        "birth_date": "2021-02-14",
        "responsible_name": "Camila Castro",
        "responsible_relationship": "Mãe",
        "diagnosis": "TEA Nível 3 (CID F84.0)",
        "chief_complaint": "Comunicação não-verbal, estereotipias motoras frequentes.",
        "goals": [
            ("Comunicação funcional com figura (PECS)", BehavioralGoal.MeasurementType.PERCENTAGE, 15, 60),
            ("Estereotipias motoras por sessão", BehavioralGoal.MeasurementType.FREQUENCY, 12, 5),
        ],
    },
    {
        "name": "Davi Martins",
        "birth_date": "2018-06-30",
        "responsible_name": "Tatiane Martins",
        "responsible_relationship": "Mãe",
        "diagnosis": "TEA Nível 1 (CID F84.0)",
        "chief_complaint": "Dificuldade de brincar de forma compartilhada com outras crianças.",
        "goals": [
            ("Brincar compartilhado com par", BehavioralGoal.MeasurementType.PERCENTAGE, 20, 65),
            ("Atenção sustentada em atividade dirigida (min)", BehavioralGoal.MeasurementType.DURATION, 6, 20),
        ],
    },
    {
        "name": "Isabela Rocha",
        "birth_date": "2016-09-09",
        "responsible_name": "Débora Rocha",
        "responsible_relationship": "Mãe",
        "diagnosis": "TEA Nível 1 (CID F84.0)",
        "chief_complaint": "Isolamento social e dificuldade de iniciar interações.",
        "goals": [
            ("Iniciar interação social", BehavioralGoal.MeasurementType.PERCENTAGE, 35, 80),
            ("Nível de regulação emocional (1-5)", BehavioralGoal.MeasurementType.INTENSITY, Decimal("2.5"), Decimal("4.5")),
        ],
    },
]

_ANAMNESIS_DEFAULTS = {
    "medical_history": "Gestação e parto sem intercorrências relevantes.",
    "family_history": "Sem outros casos de TEA na família.",
    "developmental_milestones": "Marcos motores dentro do esperado; atraso na fala.",
    "communication_profile": "Comunicação verbal emergente, uso pontual de gestos.",
    "sensory_profile": "Hipersensibilidade auditiva a sons altos e inesperados.",
    "behaviors_of_concern": "Estereotipias motoras leves, resistência a mudanças de rotina.",
    "feeding_notes": "Seletividade alimentar moderada.",
    "sleep_notes": "Sono regular, sem queixas relevantes.",
    "current_medications": "Nenhuma no momento.",
    "previous_therapies": "Fonoaudiologia em andamento (1x/semana).",
    "school_info": "Matriculado(a) em escola regular, com apoio de mediador(a).",
    "family_expectations": "Ampliar comunicação funcional e autonomia nas rotinas diárias.",
    "additional_notes": "Família bastante engajada nas orientações do plano terapêutico.",
}


class Command(BaseCommand):
    help = "Popula o banco com dados demonstrativos (terapeutas, pacientes, anamneses, objetivos e coleta de dados)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Remove os dados demonstrativos existentes (domínio @vitalis.demo) antes de recriar.",
        )

    def handle(self, *args, **options):
        random.seed(42)

        if options["reset"]:
            self._reset()
        elif Patient.objects.filter(email__endswith=f"@{DEMO_DOMAIN}").exists():
            self.stdout.write(self.style.WARNING(
                "Dados demonstrativos já existem. Use --reset para recriar do zero."
            ))
            return

        therapists = [self._create_therapist(data) for data in THERAPISTS]
        for index, patient_data in enumerate(PATIENTS):
            therapist = therapists[index % len(therapists)]
            patient = self._create_patient(patient_data)
            self._create_anamnesis(patient, patient_data)
            appointments = self._create_appointments(patient, therapist, index)
            for title, measurement_type, start, end in patient_data["goals"]:
                goal = self._create_goal(patient, title, measurement_type)
                self._create_records(goal, appointments, start, end)

        self.stdout.write(self.style.SUCCESS(
            f"Seed concluído: {len(therapists)} terapeuta(s), {len(PATIENTS)} paciente(s) "
            f"com anamnese, objetivos comportamentais e histórico de coleta."
        ))
        self.stdout.write(f"Login demo: {THERAPISTS[0]['email']} / {DEMO_PASSWORD}")

    def _reset(self):
        deleted_patients, _ = Patient.objects.filter(email__endswith=f"@{DEMO_DOMAIN}").delete()
        Therapist.objects.filter(email__endswith=f"@{DEMO_DOMAIN}").delete()
        self.stdout.write(f"Dados demonstrativos anteriores removidos ({deleted_patients} registro(s) em cascata).")

    def _create_therapist(self, data):
        therapist, created = Therapist.objects.get_or_create(
            email=data["email"], defaults={"name": data["name"]}
        )
        if created:
            if data["superuser"]:
                therapist.is_staff = True
                therapist.is_superuser = True
            therapist.set_password(DEMO_PASSWORD)
            therapist.save()
        return therapist

    def _create_patient(self, data):
        patient, _ = Patient.objects.get_or_create(
            name=data["name"],
            defaults={
                "email": f"{data['name'].lower().replace(' ', '.')}@{DEMO_DOMAIN}",
                "birth_date": data["birth_date"],
            },
        )
        return patient

    def _create_anamnesis(self, patient, data):
        Anamnesis.objects.get_or_create(
            patient=patient,
            defaults={
                "responsible_name": data["responsible_name"],
                "responsible_relationship": data["responsible_relationship"],
                "responsible_phone": "(11) 9" + "".join(str(random.randint(0, 9)) for _ in range(8)),
                "chief_complaint": data["chief_complaint"],
                "diagnosis": data["diagnosis"],
                "diagnosis_date": "2024-02-10",
                "diagnosing_professional": "Dr. Eduardo Prado - Neuropediatra",
                **_ANAMNESIS_DEFAULTS,
            },
        )

    def _create_appointments(self, patient, therapist, patient_index):
        now = timezone.now()
        hour = 9 + patient_index
        appointments = []
        for week in range(8, 0, -1):
            session_dt = (now - timedelta(weeks=week)).replace(
                hour=hour, minute=0, second=0, microsecond=0
            )
            status = Appointment.Status.COMPLETED
            if week == 3 and patient_index == 0:
                status = Appointment.Status.CANCELED
            appointment, created = Appointment.objects.get_or_create(
                patient=patient,
                therapist=therapist,
                session_datetime=session_dt,
                defaults={"status": status, "notes": random.choice(SESSION_NOTES)},
            )
            if status != Appointment.Status.CANCELED:
                appointments.append(appointment)

        for week_ahead in (1, 2):
            session_dt = (now + timedelta(weeks=week_ahead)).replace(
                hour=hour, minute=0, second=0, microsecond=0
            )
            status = Appointment.Status.RESCHEDULED if (week_ahead == 1 and patient_index == 1) else Appointment.Status.SCHEDULED
            Appointment.objects.get_or_create(
                patient=patient,
                therapist=therapist,
                session_datetime=session_dt,
                defaults={"status": status},
            )

        return appointments

    def _create_goal(self, patient, title, measurement_type):
        goal, _ = BehavioralGoal.objects.get_or_create(
            patient=patient,
            title=title,
            defaults={"measurement_type": measurement_type, "is_active": True},
        )
        return goal

    def _create_records(self, goal, appointments, start, end):
        start = Decimal(str(start))
        end = Decimal(str(end))
        total = len(appointments)
        for index, appointment in enumerate(appointments):
            fraction = Decimal(index) / Decimal(total - 1) if total > 1 else Decimal(1)
            jitter = Decimal(str(round(random.uniform(-0.05, 0.05), 3)))
            trend = start + (end - start) * (fraction + jitter)

            defaults = {"notes": random.choice(SESSION_NOTES)}
            if goal.measurement_type == BehavioralGoal.MeasurementType.PERCENTAGE:
                trials_total = 10
                trials_correct = max(0, min(trials_total, round(trend / 100 * trials_total)))
                defaults.update({"trials_correct": trials_correct, "trials_total": trials_total})
            else:
                decimals = 1
                value = max(Decimal("0"), round(trend, decimals))
                defaults.update({"value": value})

            BehavioralRecord.objects.get_or_create(
                appointment=appointment, goal=goal, defaults=defaults
            )
