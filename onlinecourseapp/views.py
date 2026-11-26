from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import Course, Enrollment, Question, Choice, Submission


def course_questions(course):
    return Question.objects.filter(
        Q(course=course) | Q(lesson__course=course),
        is_exam=True
    ).distinct().prefetch_related('choices')


@login_required
def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, 'course_details_bootstrap.html', {
        'course': course,
        'lessons': course.lessons.all(),
        'questions': course_questions(course)
    })


@login_required
@require_http_methods(['GET', 'POST'])
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    questions = course_questions(course)
    if request.method == 'GET':
        return render(request, 'submit_exam.html', {
            'course': course, 'questions': questions,
        })

    enrollment, _ = Enrollment.objects.get_or_create(user=request.user, course=course)
    question_list = list(questions)
    selected_ids = set()
    answers = {}
    score = 0
    for question in question_list:
        posted = request.POST.getlist(f'question_{question.pk}')
        posted += request.POST.getlist(f'choice_{question.pk}')
        try:
            ids = {int(value) for value in posted}
        except (ValueError, TypeError):
            ids = set()
        valid = set(question.choices.filter(pk__in=ids).values_list('pk', flat=True))
        selected_ids.update(valid)
        correct = question.is_get_score(valid)
        score += question.grade if correct else 0
        answers[str(question.pk)] = {
            'choice_ids': sorted(valid), 'is_correct': correct
        }

    total_grade = sum(q.grade for q in question_list)
    percentage = (score / total_grade * 100) if total_grade else 0
    submission = Submission.objects.create(
        student=request.user, enrollment=enrollment,
        lesson=None, answers=answers, score=score,
        total_questions=len(question_list), is_passed=percentage >= 70
    )
    submission.choices.set(Choice.objects.filter(pk__in=selected_ids))
    return redirect('show_exam_result', course_id=course.pk,
                    submission_id=submission.pk)


@login_required
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(
        Submission, pk=submission_id, student=request.user,
        enrollment__course=course
    )
    selected_ids = list(submission.choices.values_list('pk', flat=True))
    questions = list(course_questions(course))
    total_grade = sum(q.grade for q in questions)
    grade = round(submission.score / total_grade * 100, 2) if total_grade else 0
    question_results = []
    for question in questions:
        chosen = [c for c in question.choices.all() if c.pk in selected_ids]
        question_results.append({
            'question': question,
            'selected_choices': chosen,
            'correct_choices': [c for c in question.choices.all() if c.is_correct],
            'is_correct': question.is_get_score(selected_ids),
        })
    return render(request, 'exam_result_bootstrap.html', {
        'course': course,
        'submission': submission,
        'selected_ids': selected_ids,
        'grade': grade,
        'question_results': question_results,
        'total_grade': total_grade,
    })


def index(request):
    return render(request, 'index.html', {'courses': Course.objects.all()})
