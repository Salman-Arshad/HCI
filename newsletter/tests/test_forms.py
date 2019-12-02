from django.test import TestCase
from django.forms import ValidationError
from newsletter.forms import NewsUserForm

class TestNewsletterForm(TestCase):
    def test_newsletter_true_email_validity(self):
        data = {'email':'email@gmail.com'}
        form = NewsUserForm(data=data)
        self.assertTrue(form.is_valid)
    #check if form accepts invalid emails
    def test_newsletter_false_email_validity(self):
        data = {'email':'emailgmail@'}
        form = NewsUserForm(data=data)
        if not form.has_error :
            raise ValidationError('NEWSLETTER FORM ACCEPTED INVALID EMAIL')
    #check if form accepts null emails        
    def test_newsletter_accept_null_email(self):
        data = {'email':None}
        form = NewsUserForm(data=data)
        if not form.has_error:
            raise ValidationError('NEWSLETTER FORM ACCEPTED NULL EMAIL VALUE')
    def test_newsletter_accept_blank_email(self):
        data = {'email':''}
        form = NewsUserForm(data=data)
        if not form.has_error:
            raise ValidationError('NEWSLETTER FORM ACCEPTED BLANK EMAIL VALUE')