from setuptools import setup

version = '0.1.4.dev0'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
    ])

install_requires = [
    'matplotlib',
    'Pillow',
    'scipy',
    'setuptools',
    ],

tests_require = [
    'nose',
    'coverage',
    ]

setup(name='gislib',
      version=version,
      description="TODO",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[],
      keywords=[],
      author='TODO',
      author_email='TODO@nelen-schuurmans.nl',
      url='',
      license='GPL',
      packages=['gislib'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points={
          'console_scripts': [
              'pyramid = gislib.scripts.pyramid:main',
              'store = gislib.scripts.store:main',
          ]},
      )
