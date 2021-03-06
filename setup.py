import setuptools

with open('README.md', 'r') as fh:
  long_description = fh.read()

setuptools.setup(
  name='mipsplusplus',
  version='0.0.1b4',
  author='Alex Socha',
  author_email='alex@alexsocha.com',
  description='A low-level programming language based on the MIPS architecture.',
  long_description=long_description,
  long_description_content_type='text/markdown',
  url='https://github.com/alexsocha/mipsplusplus',
  packages=setuptools.find_packages(),
  classifiers=(
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
  ),
)
