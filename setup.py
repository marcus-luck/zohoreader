from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='zohoreader',
      version='0.1',
      description='A simple reader for zoho projects API to get all projects, users and timereports',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
      ],
      keywords='zoho, API, zoho project',
      url='https://github.com/marcus-luck/zohoreader',
      author='Marcus Luck',
      author_email='marcus.luck@outlook.com',
      license='MIT',
      packages=['zohoreader'],
      zip_safe=False,
      install_requires=[
          'requests>=2.12.4',
          'python-dateutil>=2.7.2'
          ],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      include_package_data=True
      )
