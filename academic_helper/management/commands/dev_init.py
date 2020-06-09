from django.core.management import BaseCommand

from academic_helper.logic.shnaton_parser import ShnatonParser
from academic_helper.models import Course, StudyBlock, DegreeProgram
from academic_helper.utils.logger import log

courses_to_fetch = [94640, 94625, 67504, 67101, 67392, 67829]  # Intro  # Crypto  # Impr

# blocks info - name, min_credits, [course_num1, ...]
unparsed_blocks = [
        ("Compulsory CS", 15, [67101, 67109, 67125]),
        ("Compulsory Math", 20, [80131, 80133, 80134]),
        ("Elective", 4, [67392, 67829])
    ]


def fetch_courses():
    log.info("Fetching courses")
    for course_number in courses_to_fetch:
        ShnatonParser.fetch_course(course_number)
    for block in unparsed_blocks:
        for course in block[2]:
            ShnatonParser.fetch_course(course)


def create_blocks():
    log.info("Creating blocks")
    study_blocks = []
    for unparsed_block in unparsed_blocks:
        # extract info
        name, min_credits, course_nums = unparsed_block
        # create block
        block = StudyBlock.objects.get_or_create(name=name, min_credits=min_credits)[0]
        # add courses to block
        for course_num in course_nums:
            course = Course.objects.get(course_number=course_num)
            block.courses.add(course)
        # add block to study blocks
        block.save()
        study_blocks.append(block)
    return study_blocks


def create_degree_program(blocks):
    log.info("Creating program")
    cs_plan = DegreeProgram.objects.get_or_create(name="Mock CS", code=1993, credits=39)[0]
    for block in blocks:
        cs_plan.blocks.add(block)
    cs_plan.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        fetch_courses()
        blocks = create_blocks()
        create_degree_program(blocks)
