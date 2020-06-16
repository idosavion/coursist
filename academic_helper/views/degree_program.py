from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest

from academic_helper.views.basic import ExtendedViewMixin
from academic_helper.models.degree_program import *


class AllDegreePrograms(ExtendedViewMixin):
    model = DegreeProgram
    template_name = "degree_program/all_degree_programs.html"

    @property
    def title(self) -> str:
        return "All Study Plans Beta"

    def search(self, search_val: str):
        programs = DegreeProgram.objects.filter(
            Q(name__icontains=search_val) | Q(code__icontains=search_val)
        ).order_by("code")[:10]
        serialized = [p.as_dict for p in programs]
        return JsonResponse({"status": "success", "programs": serialized}, json_dumps_params={"ensure_ascii": False})

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return
        if "search_val" in request.POST:
            search_val = request.POST["search_val"]
            return self.search(search_val)
        else:
            return HttpResponseBadRequest()


class UserDegreeProgram(ExtendedViewMixin):
    model = DegreeProgram
    template_name = "degree_program/user_degree_program.html"

    @property
    def title(self) -> str:
        return "User Study Plan Beta"



