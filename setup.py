import setuptools
from tld import VERSION

with open('README.markdown', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name="tld-task",
    version=VERSION,
    author="David Lowry-Duda",
    author_email="davidlowryduda@davidlowryduda.com",
    description=("tld is a tool for people who want to do things, "
                 "but who want a bit of flexibility."),
    long_description=long_description,
    long_description_content_type='text/markdown',
    py_modules=["tld"],
    url="https://github.com/davidlowryduda/tld",
    entry_points={
        'console_scripts': [
                'tld=tld:main',
            ],
    },
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ),
)
