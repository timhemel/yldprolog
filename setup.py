import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name="yldprolog",
    version="0.1.0",
    description='A rewrite of Yield Prolog for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Tim Hemel",
    author_email="yldprolog@timit.nl",
    # url='TODO',
    # project_urls= { },
    license='GNU Affero General Public License v3',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent"
    ],
    keywords=['prolog'],
    packages=setuptools.find_packages(include=['yldprolog'], exclude=['test']),
    entry_points={
        'console_scripts': ['yldpc=yldprolog.compiler:main']
    },
    python_requires='>=3.6',
)

