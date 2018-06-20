from setuptools import setup, find_packages
from setuptools.command.test import test as test_command
from captcha import get_version as get_captcha_version
import sys


class Tox(test_command):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        test_command.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        test_command.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)


install_requires = [
    'six >=1.2.0',
    'Django >= 1.8',
    'Pillow >=2.2.2,!=5.1.0',
    'django-ranged-response == 0.2.0'
]
EXTRAS_REQUIRE = {
    'test': ('testfixtures', ),
}


with open('README.rst') as readme:
    long_description = readme.read()

setup(
    name='django-simple-captcha',
    version=get_captcha_version(),
    description='A very simple, yet powerful, Django captcha application',
    long_description=long_description,
    author='Marco Bonetti',
    author_email='mbonetti@gmail.com',
    url='https://github.com/mbi/django-simple-captcha',
    license='MIT',
    packages=find_packages(exclude=['testproject', 'testproject.*']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Security',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require=EXTRAS_REQUIRE,
    tests_require=['tox'],
    cmdclass={'test': Tox},
)
