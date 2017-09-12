try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(name='adtwist',
      version='1.0.0',
      description='Allow use of alarmdecoded with twisted',
      author='John-Mark Gurney',
      author_email='jmg@funkthat.com',
      url='https://github.com/jmgurney/adtwist',
      py_modules=['adtwist'],
      install_requires=[
          'alarmdecoder',
          'mock',
          'twisted',
          'pyserial',
          ],
      tests_require=[
          'coverage',
          ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Framework :: Twisted',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          #'Operating System :: MacOS :: MacOS X',
          #'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Home Automation',
          'Topic :: Security',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
     )
