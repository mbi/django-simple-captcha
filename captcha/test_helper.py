from captcha.conf import settings as captcha_settings
from django.test.utils import TestContextDecorator

class ignore_captcha_errors(TestContextDecorator):
  """provides a class decorator/context manager to ignore captcha errors during a test.
  To be used as:
  from captcha.test_helper import ignore_captcha_errors
  class TestSomething(SimpleTestCase):
    @ignore_captcha_errors()
    def test_something(self):
       response  = self.client.post(my_url, {... 'captcha_0': 'whatever', 'captcha_1': 'passed'}, follow=True)

   or

   from captcha.test_helper import ignore_captcha_errors
   class TestSomething(SimpleTestCase):
   
     def test_something(self):
       with ignore_captcha_errors():
         response  = self.client.post(my_url, {... 'captcha_0': 'whatever', 'captcha_1': 'passed'}, follow=True)
  """
  def __init__(self):
		super().__init__()
		self.captcha_test_mode = captcha_settings.CAPTCHA_TEST_MODE

	def enable(self):
		captcha_settings.CAPTCHA_TEST_MODE = True

	def disable(self):
		captcha_settings.CAPTCHA_TEST_MODE = self.captcha_test_mode

	def decorate_class(self, cls):
		from django.test import SimpleTestCase
		if not issubclass(cls, SimpleTestCase):
			raise ValueError(
				"Only subclasses of Django SimpleTestCase can be decorated "
				"with ignore_captcha_errors"
			)
		self.captcha_test_mode = captcha_settings.CAPTCHA_TEST_MODE
		return cls
