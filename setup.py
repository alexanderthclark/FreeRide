import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def get_version():
    with open("freeride/__init__.py", "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return eval(line.split("=")[-1].strip())

setuptools.setup(
    name='freeride',
    version=get_version(),
    description='Python package for introductory microeconomics education: supply/demand curves, market equilibrium, game theory, and policy analysis.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/alexanderthclark/FreeRide',
    project_urls={
        "Documentation": "https://alexanderthclark.github.io/FreeRide/",
        "Source Code": "https://github.com/alexanderthclark/FreeRide",
        "Bug Tracker": "https://github.com/alexanderthclark/FreeRide/issues",
        "Tutorials": "https://alexanderthclark.github.io/FreeRide/tutorials/quickstart.html",
    },
    author='Alexander Clark',
    author_email='',
    maintainer='Alexander Clark',
    license='MIT',
    install_requires=['matplotlib', 'numpy', 'IPython', 'bokeh'],
    packages=setuptools.find_packages(),
    python_requires='>=3.8',
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    keywords=[
        "microeconomics", "economics", "education", "supply-demand", 
        "market-equilibrium", "game-theory", "monopoly", "policy-analysis",
        "economics-education", "undergraduate", "econ-101", "economic-modeling",
        "visualization", "matplotlib", "jupyter", "teaching", "learning"
    ],
)
