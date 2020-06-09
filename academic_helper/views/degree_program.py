from django.shortcuts import render
from django.http import HttpResponse

from academic_helper.views.basic import ExtendedViewMixin
from academic_helper.models.degree_program import *


class AllDegreePrograms(ExtendedViewMixin):
    model = DegreeProgram
    template_name = "study_plan/all_study_plans.html"

    @property
    def title(self) -> str:
        return "All Study Plans Beta"


class UserDegreeProgram(ExtendedViewMixin):
    model = DegreeProgram
    template_name = "study_plan/user_study_plan.html"

    @property
    def title(self) -> str:
        return "User Study Plan Beta"



