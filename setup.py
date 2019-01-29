from setuptools import setup, find_packages


# TODO Add
#   1) license
#   2) version
#   3) install requirements
#   4) cython extensions compile


setup(
    name='Rin',
    author='mkbeh',
    description='Bitshares arbitry bot.',
    packages=find_packages(),
    package_data={
        'src': ['*.md', 'LICENSE']
    },
    entry_points={
        'console_scripts':
            ['rin = src.rin:main']
    }
)
