from setuptools import setup, find_packages
import urlcut as module

module_name = "urlcut"


def load_requirements(fname: str):
    """ load requirements from a pip requirements file """
    with open(fname) as f:
        line_iter = (line.strip() for line in f.readlines())
        return [line for line in line_iter if line and line[0] != "#"]


setup(
    name=module_name.replace("_", "-"),
    version=module.__version__,
    author=module.__author__,
    author_email=module.authors_email,
    license=module.__license__,
    description=module.package_info,
    platforms="all",
    packages=find_packages(exclude=["tests"]),
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
