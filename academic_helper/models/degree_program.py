from typing import Iterable

from django.db import models

from academic_helper.models import Base, Course, CoursistUser


class StudyBlock(Base):
    name: str = models.CharField(max_length=50)
    courses: Iterable[Course] = models.ManyToManyField(Course)
    min_credits: int = models.IntegerField()

    def __str__(self):
        return f"{self.name}"


class CompletedCourse(Base):
    user: CoursistUser = models.ForeignKey(CoursistUser, on_delete=models.CASCADE)
    course: Course = models.ForeignKey(Course, on_delete=models.CASCADE)
    block: StudyBlock = models.ForeignKey(StudyBlock, on_delete=models.CASCADE)
    grade: int = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ["user", "course"]

    def __str__(self):
        return f"{self.user} - {self.course}"


class DegreeProgram(Base):
    name: str = models.CharField(max_length=50)
    code: int = models.IntegerField()
    blocks = models.ManyToManyField(StudyBlock)
    credits: int = models.IntegerField()

    def __str__(self):
        return f"{self.id} - {self.name}"
