import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def get_version():
    with open("microecon/__init__.py", "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return eval(line.split("=")[-1].strip())

setuptools.setup(
    name='microecon',
    version=get_version(),
	description='A package for undergraduate microeconomics.',
    long_description=long_description,  # This is the new line
    long_description_content_type="text/markdown",  # This is the new line
    url='https://github.com/alexanderthclark/Intro-Microeconomics',
    author='Alexander Clark',
    install_requires=['matplotlib','numpy'],
    author_email='',
    packages=setuptools.find_packages(),
    zip_safe=False,
)