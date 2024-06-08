import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the requirements from the requirements.txt file
with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

def get_version():
    with open("freeride/__init__.py", "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return eval(line.split("=")[-1].strip())

setuptools.setup(
    name='freeride',
    version=get_version(),
	description='A package for undergraduate microeconomics.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/alexanderthclark/Intro-Microeconomics',
    author='Alexander Clark',
    install_requires=install_requires,
    author_email='',
    packages=setuptools.find_packages(),
    zip_safe=False,
)