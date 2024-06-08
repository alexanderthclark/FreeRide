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
	description='A package for undergraduate microeconomics.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/alexanderthclark/FreeRide',
    author='Alexander Clark',
    install_requires=['matplotlib', 'numpy', 'papermill', 'IPython', 'bokeh'],
    author_email='',
    packages=setuptools.find_packages(),
    zip_safe=False,
)