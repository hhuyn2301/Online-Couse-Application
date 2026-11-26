from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    name = models.CharField(max_length=200)
    description = models.TextField()
    content = models.TextField()
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']


class Question(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    grade = models.PositiveIntegerField(default=10)
    question_text = models.TextField()
    is_exam = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text[:50]

    def is_get_score(self, selected_ids):
        correct = set(self.choices.filter(is_correct=True).values_list('id', flat=True))
        chosen = set(self.choices.filter(id__in=selected_ids).values_list('id', flat=True))
        return bool(correct) and correct == chosen

    class Meta:
        ordering = ['order']


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

    class Meta:
        ordering = ['order']


class Submission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='submissions', null=True, blank=True)
    enrollment = models.ForeignKey('Enrollment', on_delete=models.CASCADE, related_name='submissions', null=True, blank=True)
    choices = models.ManyToManyField(Choice, blank=True)
    answers = models.JSONField(default=dict)
    score = models.FloatField(default=0)
    total_questions = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_passed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.username} - Submission {self.pk}"

    class Meta:
        ordering = ['-submitted_at']

class Learner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learner_profile')

    def __str__(self):
        return self.user.username


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile')

    def __str__(self):
        return self.user.username


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'course'], name='unique_user_course_enrollment')
        ]

    def __str__(self):
        return f"{self.user.username} - {self.course.name}"
