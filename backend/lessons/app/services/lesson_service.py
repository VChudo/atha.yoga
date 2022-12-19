from functools import cached_property
from typing import Optional

from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied

from core.app.utils.util import setup_resource_attributes
from core.models import User, UserRoles
from lessons.app.repositories.lesson_repository import LessonRepository
from core.models import User
from lessons.app.repositories.lesson_repository import LessonRepository, TicketRepository
from lessons.app.repositories.schedule_repository import ScheduleRepository
from lessons.app.services.types import LessonCreateData, LessonUpdateData
from lessons.models import Lesson, Schedule
from lessons.app.services.types import LessonCreateData
from lessons.models import Lesson, Schedule, Ticket
from lessons.seeders.lesson_seeder import LessonSeeder


class LessonCreator:
    repos = LessonRepository()
    schedule_repos = ScheduleRepository()

    def __init__(self, data: LessonCreateData, user: User):
        self._data = data
        self._user = user

    @cached_property
    def lesson(self) -> Lesson:
        lesson = Lesson()
        lesson.name = self._data["name"]
        lesson.description = self._data["description"]
        lesson.lesson_type = self._data["lesson_type"]
        lesson.link = self._data["link"]
        lesson.link_info = self._data["link_info"]
        lesson.level = self._data["level"]
        lesson.duration = self._data["duration"]
        lesson.repeat_editing = self._data["repeat_editing"]
        lesson.start_datetime = self._data["start_datetime"]
        lesson.deadline_date = self._data["deadline_date"]
        lesson.payment = self._data["payment"]
        lesson.price = self._data["price"]
        lesson.complexity = self._data["complexity"]
        lesson.teacher = self._user
        return lesson

    def _create_schedule(self) -> None:
        if not self._data["schedule"]:
            return
        schedule_to_create = []
        for item in self._data["schedule"]:
            schedule = Schedule()
            schedule.lesson = self.lesson
            schedule.weekday = item["weekday"]
            schedule.start_time = item["start_time"]
            schedule_to_create.append(schedule)
        self.schedule_repos.bulk_create(objs=schedule_to_create)

    def create(self) -> Lesson:
        if not self._user.has_role(UserRoles.TEACHER):
            raise PermissionDenied("User must be teacher for create lessons")
        self.repos.store(lesson=self.lesson)
        self._create_schedule()
        return self.lesson


class LessonUpdator:
    repository = LessonRepository()

    def __init__(self, user: User, pk: int, data: LessonUpdateData):
        self._pk = pk
        self._user = user
        self._data = data

    def update(self) -> Lesson:
        lesson = self.repository.find_by_id_teacher(
            id_=self._pk, teacher_id=self._user.id
        )
        if not lesson:
            raise NotFound(f"Undefined lesson with pk {self._pk}")
        setup_resource_attributes(
            instance=lesson, validated_data=self._data, fields=list(self._data.keys())
        )
        return lesson


class FavoriteLessonsWork:
    repository = LessonRepository()

    def __init__(self, user: User, lesson_id: int):
        self.user = user
        self.lesson_id = lesson_id

    @cached_property
    def lesson(self) -> Lesson:
        lesson = self.repository.find_by_id(id_=self.lesson_id)
        if not lesson:
            raise NotFound(f"Undefined lesson with id {self.lesson_id}")
        return lesson

    def add(self) -> Lesson:
        if self.lesson in self.repository.find_user_favorite_lessons(user=self.user):
            raise ValidationError(
                f"Lesson with id {self.lesson_id} already in favorites"
            )
        self.repository.add_user_favorite_lesson(user=self.user, lesson=self.lesson)
        return self.lesson

    def remove(self) -> Lesson:
        if self.lesson not in self.repository.find_user_favorite_lessons(
                user=self.user
        ):
            raise NotFound(f"Undefined lesson with id {self.lesson_id} in favorites")
        self.repository.remove_user_favorite_lesson(user=self.user, lesson=self.lesson)
        return self.lesson


class TicketService:
    repositories = TicketRepository()

    def create_ticket(self, lesson_id: int, user: User, amount: int):
        ticket = Ticket()
        lesson = LessonRepository().find_by_id(id_=lesson_id)
        if not lesson:
            raise NotFound("Lesson not found")
        ticket.lesson = lesson
        ticket.user = user
        ticket.amount = amount
        return ticket

    def buy_ticket(self, lesson_id: int, user: User, amount: int) -> Ticket:
        ticket = self.repositories.ticket_for_lesson(lesson_id=lesson_id, user=user)
        if not ticket:
            ticket = self.create_ticket(lesson_id=lesson_id, user=user, amount=amount)
            self.repositories.store(ticket=ticket)
            return ticket

        ticket.amount = int(ticket.amount) + int(amount)
        self.repositories.store(ticket=ticket)
        return ticket

    def participant(self, schedule_id: int, user: User) -> Ticket:
        scheduled_lesson = ScheduleRepository().find(id_=schedule_id)

        ticket = self.repositories.ticket_for_lesson(lesson_id=scheduled_lesson.lesson.id, user=user)
        if not ticket:
            raise NotFound("You dont have ticket for this lesson")
        ticket.amount = int(ticket.amount) - 1
        if ticket.amount == 0:
            self.repositories.destroy(ticket=ticket)
        self.repositories.store(ticket=ticket)

        scheduled_lesson.participants.add(user)
        return ticket
