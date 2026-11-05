from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Course, Enrollment, Question, Choice, Submission

class ExamFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='learner', password='test-pass')
        self.course = Course.objects.create(name='Learning Django', description='A Django course')
        Enrollment.objects.create(user=self.user, course=self.course)
        self.question = Question.objects.create(course=self.course, content='Is Django a Python framework?', grade=100)
        self.yes = Choice.objects.create(question=self.question, content='Yes', is_correct=True)
        self.no = Choice.objects.create(question=self.question, content='No', is_correct=False)
        self.client.force_login(self.user)

    def test_correct_submission_shows_success(self):
        response = self.client.post(reverse('onlinecourse:submit', args=[self.course.id]), {'choice': [self.yes.id]}, follow=True)
        self.assertContains(response, 'Congratulations')
        self.assertContains(response, '100 out of 100')
        self.assertEqual(Submission.objects.count(), 1)

    def test_wrong_extra_choice_does_not_pass(self):
        response = self.client.post(reverse('onlinecourse:submit', args=[self.course.id]), {'choice': [self.yes.id, self.no.id]}, follow=True)
        self.assertNotContains(response, 'Congratulations')
        self.assertContains(response, '0 out of 100')

    def test_results_are_private_to_submitter(self):
        submission = Submission.objects.create(enrollment=Enrollment.objects.get(user=self.user, course=self.course))
        self.client.force_login(User.objects.create_user(username='other', password='test-pass'))
        response = self.client.get(reverse('onlinecourse:show_exam_result', args=[self.course.id, submission.id]))
        self.assertEqual(response.status_code, 404)

