from setuptools import setup, find_packages

setup(
    name="kiss-cli",
    version="1.0.0",
    packages=find_packages(),  # Automatically finds the `kiss` package
    install_requires=[
        "click",
        "kubernetes",
    ],
    entry_points={
        "console_scripts": [
            "kiss=kiss.kiss:main", # Entry point for the CLI
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