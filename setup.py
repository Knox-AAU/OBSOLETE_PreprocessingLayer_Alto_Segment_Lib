import setuptools

with open('README.md') as rm:
    long_description = rm.read()

setuptools.setup(
    name='alto-segment-lib',
    version='0.0.1',
    author='knox-17',
    author_email='tglo18@student.aau.dk',
    description='Library capable of extracting segments from ALTO Xml.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://git.its.aau.dk/Knox/alto-segment-lib.git',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)