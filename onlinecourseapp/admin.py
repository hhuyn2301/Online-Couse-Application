from django.contrib import admin
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission, Enrollment


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ('question_text', 'grade', 'is_exam', 'order')


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 2
    fields = ('choice_text', 'is_correct', 'order')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    inlines = (LessonInline,)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('name',)
    inlines = (QuestionInline,)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'grade', 'course', 'lesson', 'is_exam')
    search_fields = ('question_text',)
    list_filter = ('course', 'is_exam')
    inlines = (ChoiceInline,)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'enrollment', 'score', 'is_passed', 'submitted_at')
    readonly_fields = ('student', 'enrollment', 'answers', 'score', 'total_questions', 'is_passed', 'submitted_at')


admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Choice)
admin.site.register(Enrollment)
