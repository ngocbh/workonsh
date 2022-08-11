from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

PROJECT_URLS = {
    'Bug Tracker': 'https://github.com/ngocbh/workonsh/issues',
    'Documentation': 'https://github.com/ngocbh/workonsh/README.md',
    'Source Code': 'https://github.com/ngocbh/workonsh'
}


install_requires = ['click']

setup(name='workonsh',
      description='Work on a server',
      author='Ngoc Bui',
      long_description=long_description,
      long_description_content_type="text/markdown",
      project_urls=PROJECT_URLS,
      author_email='ngocbh.pt@gmail.com',
      version='0.0.2',
      entry_points='''
        [console_scripts]
        workonsh=workonsh.main:main
      ''',
      packages=find_packages(),
      install_requires=install_requires,
      python_requires='>=3.6')
