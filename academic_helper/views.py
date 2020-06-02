import re

from allauth.account.views import LoginView as SuperLoginView, SignupView as SuperSignupView
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView

from academic_helper.logic.shnaton_parser import ShnatonParser
from academic_helper.models import CoursistUser
from academic_helper.models.class_schedule import ClassSchedule
from academic_helper.models.course import Course
from academic_helper.models.course_occurrence import CourseClass, ClassGroup
from academic_helper.utils.logger import log


def index(request):
    return render(request, "index.html")


class ExtendedViewMixin(TemplateView):
    @property
    def title(self) -> str:
        base_name = self.__class__.__name__
        base_name = base_name.replace("View", "")
        return re.sub(r"(.)([A-Z])", "\\1 \\2", base_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        return context

    def post(self, request: WSGIRequest):
        pass

    @property
    def user(self) -> CoursistUser:
        return self.request.user


class AjaxView(ExtendedViewMixin):
    template_name = "ajax.html"

    @property
    def title(self):
        return "Ajax"

    def post(self, request: WSGIRequest, *args, **kwargs):
        log.info("We are in POST")
        if request.is_ajax():
            value = "Hi " + request.POST["value"]
            log.info(f"User sent {value} via Ajax")
            return JsonResponse({"success": True, "value": value})
        else:
            value = request.POST["post-text"]
            log.info(f"User sent {value} via POST")
            return self.render_to_response(context={"value": value})


class CourseDetailsView(DetailView, ExtendedViewMixin):
    model = Course
    template_name = "course-details.html"

    @property
    def title(self) -> str:
        return f"Course {self.object.course_number}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["semester_rating_description"] = "כמה קשה היה הקורס במהלך הסמסטר? כמה עמוסים היו שיעורי הבית? (1-קשה " \
                                                 "5-קל)"
        context["semester_rating_title"] = "קושי במהלך הסמסטר"
        context["exams_rating_description"] = "כמה קשה היתה הבחינה/פרוייקט גמר? (1-קשה 5-קל)"
        context["exams_rating_title"] = "בחינות"
        context["interest_rating_description"] = "כמה מעניין היה הקורס? כמה כיף? (1-לא מעניין 5-מעניין)"
        context["interest_rating_title"] = "עניין"
        return context

    @property
    def object(self):
        query = Course.objects.filter(course_number=self.kwargs["course_number"])
        return get_object_or_404(query)


# class CourseSearchForm(forms.Form):
#     free_text: forms.CharField(max_length=50)
#     faculty: forms.CharField(max_length=50)


class CoursesView(ExtendedViewMixin, ListView):
    model = Course
    template_name = "courses.html"

    @property
    def title(self) -> str:
        return "All Courses"

    @property
    def object_list(self):
        return Course.objects.all()

    def post(self, request: WSGIRequest):
        if not request.is_ajax():
            raise NotImplementedError()
        text = request.POST["free_text"]
        queryset = Course.find_by(text)
        result = [c.as_dict for c in queryset]
        for course in result:
            course["url"] = reverse("course-details", args=[course["course_number"]])
        return JsonResponse({"courses": result})


class AboutView(ExtendedViewMixin):
    template_name = "about.html"


class LoginView(SuperLoginView):
    template_name = "login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["signup_url"] = reverse("signup")
        return context


class SignupView(SuperSignupView):
    template_name = "signup.html"


class ScheduleView(ExtendedViewMixin):
    template_name = "schedule.html"

    @property
    def title(self) -> str:
        return "Schedule Planner"

    def search(self, search_val: str):
        courses = Course.objects.filter(
            Q(name__icontains=search_val) | Q(course_number__icontains=search_val)
        ).order_by("course_number")[:10]
        serialized = [c.as_dict for c in courses]
        return JsonResponse({"status": "success", "courses": serialized}, json_dumps_params={"ensure_ascii": False})

    def add_choice_to_user(self, choice):
        log.info(f"add_choice_to_user with choice={choice}")
        if self.user.is_anonymous:
            log.warning("add_choice_to_user called but user is_anonymous")
            return JsonResponse({"status": "error", "message": "User not logged in"})
        choice_group = ClassGroup.objects.get(pk=choice)
        existing = ClassSchedule.objects.filter(user=self.user, group__class_type=choice_group.class_type).first()
        if existing:
            log.info(f"add_choice_to_user replacing existing {existing}")
            existing.delete()
        schedule = ClassSchedule(user=self.user, group=choice_group)
        schedule.save()
        log.info(f"add_choice_to_user added {schedule}")
        return JsonResponse({"status": "success"})

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return
        if "search_val" in request.POST:
            search_val = request.POST["search_val"]
            return self.search(search_val)
        if "group_choice" in request.POST:
            choice = request.POST["choice"]
            return self.add_choice_to_user(choice)
        else:
            return HttpResponseBadRequest()


class SearchView(View):
    """
    View which searched and fetches the course by its number.
    If the course doesn't exist locally, we try to fetch it from Shnaton and
    add it to our database.
    """

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()

        if "search_val" not in request.POST:
            return HttpResponseBadRequest()

        search_val = request.POST["search_val"]
        if not search_val.isdigit():
            return HttpResponseBadRequest()

        course = Course.objects.filter(course_number=search_val).last()
        if course is None:
            # try fetching the course from Shnaton
            course = ShnatonParser.fetch_course(search_val)
            if course is None:
                return JsonResponse({"status": "error", "msg": "Course not found"})
        return JsonResponse({"status": "success", "course": course.as_dict})


class FetchClassesView(View):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()
        if "search_val" not in request.POST:
            return HttpResponseBadRequest()
        search_val = request.POST["search_val"]
        if not search_val.isdigit():
            return HttpResponseBadRequest()
        course = Course.objects.filter(course_number=search_val).last()
        if not course:
            return JsonResponse({"status": "error", "msg": "Course not found"})
        groups = ClassGroup.objects.filter(occurrence__course=course).order_by("class_type", "mark").all()
        serialized = [g.as_dict for g in groups]
        for group in serialized:
            classes = CourseClass.objects.filter(group_id=group["id"]).all()
            group["classes"] = [c.as_dict for c in classes]
        return JsonResponse({"status": "success", "groups": serialized})