from setuptools import setup

setup(name='clean_folder',
      version='0.0.1',
      description='Super sorter',
      url='https://github.com/Dmytro-Tarasenko/GoIT_Homeworks',
      author='Dmytro Tarasenko',
      author_email='flyingcircus@example.com',
      license='MIT',
      packages=['clean_folder'],
      entry_points={
          'console_scripts': ['clean-folder = clean_folder.clean:main']
      })
