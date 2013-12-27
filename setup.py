from setuptools import setup, find_packages
from captcha import pillow_required, get_version as get_captcha_version

install_requires = [
    'setuptools',
    'six >=1.2.0',
    'Django >= 1.4'
]

if pillow_required():
    install_requires.append('Pillow >=2.2.2')

setup(
    name='django-simple-captcha',
    version=get_captcha_version(),
    description='A very simple, yet powerful, Django captcha application',
    author='Marco Bonetti',
    author_email='mbonetti@gmail.com',
    url='https://github.com/mbi/django-simple-captcha',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Security',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires
)
