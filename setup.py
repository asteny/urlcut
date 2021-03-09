from setuptools import find_packages, setup


__version__ = "0.1"
__author__ = "Pavel Sofrony <pavel@sofrony.ru>"


def load_requirements(fname: str):
    """ load requirements from a pip requirements file """
    with open(fname) as f:
        line_iter = (line.strip() for line in f.readlines())
        return [line for line in line_iter if line and line[0] != "#"]


setup(
    name="urlcut",
    version=__version__,
    author=__author__,
    author_email="pavel@sofrony.ru",
    license="MIT",
    description="Prometheus exporter for ssl certs",
    platforms="all",
    packages=find_packages(),
    install_requires=load_requirements("requirements.txt"),
    extras_require={"dev": load_requirements("requirements.dev.txt")},
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "urlcut = urlcut.main:main",
            "urlcut-db = urlcut.alembic.__main__:main",
        ],
    },
    include_package_data=True,
)
