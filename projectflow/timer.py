"""
Module timer - Suivi du temps et timer intégré.

Ce module gère :
- Timer Pomodoro
- Suivi des sessions de travail
- Statistiques de productivité
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json


class Session:
    """Représente une session de travail."""

    def __init__(self, projet_id: str = None, type_session: str = "travail"):
        self.id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.projet_id = projet_id
        self.type_session = type_session  # "travail", "pause", "pause_longue"
        self.debut = None
        self.fin = None
        self.duree_secondes = 0
        self.complete = False
        self.notes = ""

    def demarrer(self):
        """Démarre la session."""
        self.debut = datetime.now()

    def arreter(self):
        """Arrête la session."""
        self.fin = datetime.now()
        if self.debut:
            self.duree_secondes = (self.fin - self.debut).total_seconds()
        self.complete = True

    @property
    def duree_minutes(self) -> float:
        return self.duree_secondes / 60

    @property
    def duree_formatee(self) -> str:
        minutes = int(self.duree_secondes // 60)
        secondes = int(self.duree_secondes % 60)
        return f"{minutes:02d}:{secondes:02d}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "projet_id": self.projet_id,
            "type_session": self.type_session,
            "debut": self.debut.isoformat() if self.debut else None,
            "fin": self.fin.isoformat() if self.fin else None,
            "duree_secondes": self.duree_secondes,
            "complete": self.complete,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Session':
        session = cls(
            projet_id=data.get("projet_id"),
            type_session=data.get("type_session", "travail")
        )
        session.id = data.get("id", session.id)
        session.debut = datetime.fromisoformat(data["debut"]) if data.get("debut") else None
        session.fin = datetime.fromisoformat(data["fin"]) if data.get("fin") else None
        session.duree_secondes = data.get("duree_secondes", 0)
        session.complete = data.get("complete", False)
        session.notes = data.get("notes", "")
        return session


class PomodoroTimer:
    """Timer Pomodoro avec gestion des cycles."""

    # Durées par défaut (en minutes)
    DUREE_TRAVAIL = 25
    DUREE_PAUSE = 5
    DUREE_PAUSE_LONGUE = 15
    CYCLES_AVANT_PAUSE_LONGUE = 4

    def __init__(self):
        self.session_actuelle = None
        self.est_en_cours = False
        self.temps_restant = 0
        self.cycle_actuel = 1
        self.cycles_completes = 0
        self.sessions_historique = []
        self.projet_id_actuel = None

        # Callbacks
        self.on_tick = None  # Appelé chaque seconde
        self.on_complete = None  # Appelé à la fin d'une session
        self.on_cycle_complete = None  # Appelé à la fin d'un cycle complet

    def demarrer_travail(self, projet_id: str = None):
        """Démarre une session de travail."""
        self.projet_id_actuel = projet_id
        self.session_actuelle = Session(projet_id, "travail")
        self.session_actuelle.demarrer()
        self.temps_restant = self.DUREE_TRAVAIL * 60
        self.est_en_cours = True

    def demarrer_pause(self):
        """Démarre une pause."""
        # Déterminer si pause courte ou longue
        if self.cycles_completes > 0 and self.cycles_completes % self.CYCLES_AVANT_PAUSE_LONGUE == 0:
            type_pause = "pause_longue"
            duree = self.DUREE_PAUSE_LONGUE
        else:
            type_pause = "pause"
            duree = self.DUREE_PAUSE

        self.session_actuelle = Session(self.projet_id_actuel, type_pause)
        self.session_actuelle.demarrer()
        self.temps_restant = duree * 60
        self.est_en_cours = True

    def tick(self):
        """Appelé chaque seconde pour mettre à jour le timer."""
        if not self.est_en_cours or self.temps_restant <= 0:
            return

        self.temps_restant -= 1

        if self.on_tick:
            self.on_tick(self.temps_restant, self.temps_formate)

        if self.temps_restant <= 0:
            self._terminer_session()

    def _terminer_session(self):
        """Termine la session actuelle."""
        if self.session_actuelle:
            self.session_actuelle.arreter()
            self.sessions_historique.append(self.session_actuelle)

            if self.session_actuelle.type_session == "travail":
                self.cycles_completes += 1
                if self.on_cycle_complete:
                    self.on_cycle_complete(self.cycles_completes)

            if self.on_complete:
                self.on_complete(self.session_actuelle)

        self.session_actuelle = None
        self.est_en_cours = False

    def pause(self):
        """Met le timer en pause."""
        self.est_en_cours = False

    def reprendre(self):
        """Reprend le timer."""
        if self.session_actuelle and self.temps_restant > 0:
            self.est_en_cours = True

    def arreter(self):
        """Arrête complètement le timer."""
        if self.session_actuelle:
            self.session_actuelle.arreter()
            if self.session_actuelle.duree_secondes > 60:  # Au moins 1 minute
                self.sessions_historique.append(self.session_actuelle)

        self.session_actuelle = None
        self.est_en_cours = False
        self.temps_restant = 0

    def reinitialiser(self):
        """Réinitialise le timer."""
        self.arreter()
        self.cycle_actuel = 1
        self.cycles_completes = 0

    @property
    def temps_formate(self) -> str:
        """Retourne le temps restant formaté MM:SS."""
        minutes = int(self.temps_restant // 60)
        secondes = int(self.temps_restant % 60)
        return f"{minutes:02d}:{secondes:02d}"

    @property
    def progression(self) -> float:
        """Retourne la progression de la session actuelle (0-1)."""
        if not self.session_actuelle:
            return 0

        if self.session_actuelle.type_session == "travail":
            duree_totale = self.DUREE_TRAVAIL * 60
        elif self.session_actuelle.type_session == "pause_longue":
            duree_totale = self.DUREE_PAUSE_LONGUE * 60
        else:
            duree_totale = self.DUREE_PAUSE * 60

        return 1 - (self.temps_restant / duree_totale)


class TimeTracker:
    """Suivi du temps de travail et statistiques."""

    def __init__(self):
        self.sessions: List[Session] = []
        self.pomodoro = PomodoroTimer()

    def ajouter_session(self, session: Session):
        """Ajoute une session à l'historique."""
        self.sessions.append(session)

    def obtenir_sessions_jour(self, date: datetime = None) -> List[Session]:
        """Retourne les sessions d'un jour donné."""
        if date is None:
            date = datetime.now()

        return [
            s for s in self.sessions
            if s.debut and s.debut.date() == date.date()
        ]

    def obtenir_sessions_semaine(self, date: datetime = None) -> List[Session]:
        """Retourne les sessions de la semaine."""
        if date is None:
            date = datetime.now()

        debut_semaine = date - timedelta(days=date.weekday())

        return [
            s for s in self.sessions
            if s.debut and s.debut.date() >= debut_semaine.date()
        ]

    def obtenir_sessions_projet(self, projet_id: str) -> List[Session]:
        """Retourne les sessions d'un projet."""
        return [s for s in self.sessions if s.projet_id == projet_id]

    def calculer_temps_total(self, sessions: List[Session] = None) -> float:
        """Calcule le temps total en heures."""
        if sessions is None:
            sessions = self.sessions

        travail_sessions = [s for s in sessions if s.type_session == "travail"]
        total_secondes = sum(s.duree_secondes for s in travail_sessions)
        return total_secondes / 3600

    def calculer_statistiques_semaine(self) -> dict:
        """Calcule les statistiques de la semaine."""
        sessions_semaine = self.obtenir_sessions_semaine()
        sessions_travail = [s for s in sessions_semaine if s.type_session == "travail"]

        # Temps par jour
        temps_par_jour = {}
        jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

        for s in sessions_travail:
            if s.debut:
                jour = jours[s.debut.weekday()]
                temps_par_jour[jour] = temps_par_jour.get(jour, 0) + s.duree_secondes / 3600

        return {
            "temps_total": self.calculer_temps_total(sessions_travail),
            "sessions_count": len(sessions_travail),
            "temps_moyen_session": (
                sum(s.duree_secondes for s in sessions_travail) / len(sessions_travail) / 60
                if sessions_travail else 0
            ),
            "temps_par_jour": temps_par_jour,
            "jour_plus_productif": max(temps_par_jour, key=temps_par_jour.get) if temps_par_jour else None,
            "pomodoros_completes": len([s for s in sessions_travail if s.complete])
        }

    def calculer_statistiques_projet(self, projet_id: str) -> dict:
        """Calcule les statistiques d'un projet."""
        sessions_projet = self.obtenir_sessions_projet(projet_id)
        sessions_travail = [s for s in sessions_projet if s.type_session == "travail"]

        return {
            "temps_total": self.calculer_temps_total(sessions_travail),
            "sessions_count": len(sessions_travail),
            "premiere_session": min((s.debut for s in sessions_travail if s.debut), default=None),
            "derniere_session": max((s.fin for s in sessions_travail if s.fin), default=None)
        }

    def to_dict(self) -> dict:
        return {
            "sessions": [s.to_dict() for s in self.sessions[-500:]],  # Garder les 500 dernières
            "pomodoro": {
                "cycles_completes": self.pomodoro.cycles_completes,
                "duree_travail": self.pomodoro.DUREE_TRAVAIL,
                "duree_pause": self.pomodoro.DUREE_PAUSE,
                "duree_pause_longue": self.pomodoro.DUREE_PAUSE_LONGUE
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TimeTracker':
        tracker = cls()
        for session_data in data.get("sessions", []):
            tracker.sessions.append(Session.from_dict(session_data))

        pomo_data = data.get("pomodoro", {})
        tracker.pomodoro.cycles_completes = pomo_data.get("cycles_completes", 0)
        tracker.pomodoro.DUREE_TRAVAIL = pomo_data.get("duree_travail", 25)
        tracker.pomodoro.DUREE_PAUSE = pomo_data.get("duree_pause", 5)
        tracker.pomodoro.DUREE_PAUSE_LONGUE = pomo_data.get("duree_pause_longue", 15)

        return tracker


def formater_duree(secondes: float) -> str:
    """Formate une durée en heures et minutes."""
    heures = int(secondes // 3600)
    minutes = int((secondes % 3600) // 60)

    if heures > 0:
        return f"{heures}h {minutes}min"
    return f"{minutes}min"
