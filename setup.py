import setuptools

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setuptools.setup(
    include_package_data = True,
    install_requires=requirements
)
