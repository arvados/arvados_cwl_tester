# -*- coding: utf-8 -*-
import sys
from pathlib import Path

from setuptools import setup

assert sys.version_info >= (3, 8, 0), "arvados-cwl-tester requires Python 3.8.0+"

CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))

def package(name, authors, **args):
    long_description = (CURRENT_DIR / "README.md").read_text(encoding="utf8")

    setup(
        name=name,
        long_description=long_description,
        long_description_content_type="text/markdown",
        author=", ".join(authors),
        setup_requires=["setuptools>=45", "wheel"],
        package_dir={"": "src"},
        py_modules=[name],
        packages=[name],
        include_package_data=True,
        zip_safe=False,
        **args
    )


package(
    name="arvados_cwl_tester",
    version="Beta",
    description="Framework for testing Common Workflow Language on Arvados",
    keywords=["cwl", "Common Workflow Language", "arvados", "python", "testing", "bioinformatics"],
    authors=[
        "Monika Krzyżanowska <monigenomi@gmail.com>",
        "Joanna Butkiewicz <joanna-butkiewicz>",
        "Agata Dziedzic <betula185>"
    ],
    classifiers=[
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.8",
    ],
    # url="https://arvados-cwltest.com/",
    project_urls={
        "Bug Tracker": "https://github.com/arvados/arvados-cwl-tester/issues",
        "Source Code": "https://github.com/arvados/arvados-cwl-tester",
    },
    install_requires=[
        "pytest==7.1.2",
        "PyYAML==5.4.1",
        "arvados-python-client==2.4.3",
        "arvados-cwl-runner==2.4.3",
        "pytest-parallel==0.1.1",
        "pytest==7.1.2",
    ],
    extras_require={
        "dev": [
            "black==22.6.0",
            "pre-commit",
            "isort==5.9.3"
        ]
    },
    python_requires="~=3.8",
)