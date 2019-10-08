import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name="yldprolog",
    version="1.0.0",
    description='A rewrite of Yield Prolog for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Tim Hemel",
    author_email="yldprolog@timit.nl",
    project_urls= {
        'Source': 'https://github.com/timhemel/yldprolog'
    },
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
    install_requires=[
        'antlr4-python3-runtime>=4.7.2'
    ]
)

