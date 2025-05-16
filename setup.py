from setuptools import setup, find_packages
from setuptools import setup, find_packages

setup(
    name="kiss",
    version="0.1.0",
    packages=find_packages(),  # This will find 'app' and its submodules
    install_requires=[
        "click",
        "kubernetes",
        "tabulate",
    ],
    entry_points={
        "console_scripts": [
            "kiss=app.main:main",
        ],
    },
    author="Andrej Trusevic",
    author_email="andriktr@gmail.com",
    description="A Kubernetes CLI tool to process namespaces and labels.",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)