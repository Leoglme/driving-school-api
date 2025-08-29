from pathlib import Path
import sys
from datetime import datetime, timedelta
import random
import click
from faker import Faker
from flask import current_app

# Ajouter le chemin racine au sys.path pour importer les modules
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

from app import db, create_app
from app.models.Meet import Meet
from app.models.User import User
from app.enums.role import Role

app = create_app()
fake = Faker()


# RUN CLI COMMAND: python app/seeders/meet.py --count=100
@click.command()
@click.option('--count', default=100, help='Number of meets to be generated')
def add_meets(count):
    with app.app_context():
        # Récupérer les utilisateurs avec les rôles Student et Instructor
        students = User.query.filter_by(role=Role.Student.value, active=True).all()
        instructors = User.query.filter(
            (User.role == Role.Instructor.value) | (User.role == Role.Secretary.value) | (
                    User.role == Role.Admin.value),
            User.active == True
        ).all()

        if not students or not instructors:
            current_app.logger.error("Erreur : Aucun étudiant ou instructeur trouvé dans la base de données.")
            return click.echo("Erreur : Aucun étudiant ou instructeur trouvé dans la base de données.")

        # Définir la période : 2 mois avant et 1 an après la date actuelle
        current_date = datetime.now()
        start_date = current_date - timedelta(days=60)  # 2 mois avant
        end_date = current_date + timedelta(days=365)  # 1 an après

        # Calculer le nombre total de semaines
        total_days = (end_date - start_date).days
        total_weeks = total_days // 7
        meets_per_week = 3
        total_meets = total_weeks * meets_per_week

        # Ajuster le count si nécessaire
        count = min(count, total_meets)

        meets_added = 0
        current_week_start = start_date

        while meets_added < count and current_week_start < end_date:
            # Générer 3 rendez-vous par semaine
            for _ in range(meets_per_week):
                if meets_added >= count:
                    break

                # Choisir un jour aléatoire dans la semaine
                day_offset = random.randint(0, 4)  # Lundi à vendredi
                meet_date = current_week_start + timedelta(days=day_offset)

                # Choisir une heure de début entre 8h et 17h
                start_hour = random.randint(8, 16)
                start_time = meet_date.replace(hour=start_hour, minute=0, second=0, microsecond=0)

                # Durée du rendez-vous : 1 ou 2 heures
                duration_hours = random.choice([1, 2])
                end_time = start_time + timedelta(hours=duration_hours)

                # Sélectionner un étudiant et un instructeur aléatoires
                student = random.choice(students)
                instructor = random.choice(instructors)

                # Vérifier les heures disponibles pour l'étudiant
                driving_time = student.driving_time
                if driving_time and driving_time.hours_total - driving_time.hours_done < duration_hours:
                    current_app.logger.warning(f"Étudiant {student.email} n'a plus assez d'heures disponibles.")
                    continue

                # Créer le rendez-vous
                meet = Meet(
                    title=f"Leçon de conduite - {student.first_name}",
                    start=start_time,
                    end=end_time,
                    all_day=False,
                    chef=instructor.id,
                    user=student.id
                )
                db.session.add(meet)

                # Mettre à jour les heures de conduite de l'étudiant
                if driving_time:
                    driving_time.hours_done += duration_hours
                    db.session.add(driving_time)

                meets_added += 1
                current_app.logger.info(f"Rendez-vous créé : {meet.title} le {meet.start} pour {student.email}")

            # Passer à la semaine suivante
            current_week_start += timedelta(days=7)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return click.echo(f"{meets_added} rendez-vous ont été ajoutés avec succès à la base de données.")


if __name__ == '__main__':
    add_meets()
