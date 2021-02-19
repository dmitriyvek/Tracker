import os
import importlib

from pkg_resources import parse_requirements
from setuptools import find_packages, setup


module_name = 'tracker'

# The module may not be installed yet (or a different version is installed), so
# need to load __init__.py using importlib.
spec = importlib.util.spec_from_file_location(
    module_name, os.path.join(module_name, '__init__.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def load_requirements(fname: str) -> list:
    requirements = []
    with open(fname, 'r') as fp:
        for req in parse_requirements(fp.read()):
            extras = '[{}]'.format(','.join(req.extras)) if req.extras else ''
            requirements.append(
                '{}{}{}'.format(req.name, extras, req.specifier)
            )
    return requirements


setup(
    name=module_name,
    version=module.__version__,
    author=module.__author__,
    author_email=module.__email__,
    license=module.__license__,
    description=module.__doc__,
    long_description=open('../README.md').read(),
    url='https://github.com/dmitriyvek/Tracker',
    platforms='all',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: Russian',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython'
    ],
    python_requires='>=3.8',
    packages=find_packages(exclude=['tests']),
    install_requires=load_requirements('requirements.txt'),
    extras_require={'dev': load_requirements('requirements.dev.txt')},
    entry_points={
        'console_scripts': [
            '{0}-api = {0}.api.__main__:main'.format(module_name),
            '{0}-migrate = {0}.db.__main__:main'.format(module_name),
            'init-db-data = {0}.db.init_db_data:init_db_data'.format(
                module_name)
        ]
    },
    include_package_data=True
)
