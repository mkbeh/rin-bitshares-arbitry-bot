import src

from setuptools import setup, find_packages
from Cython.Build import cythonize
from Cython.Distutils import build_ext


def readme():
    with open('src/README.md') as f:
        return f.read()


setup(
    name='Rin',
    author='mkbeh',
    description='Bitshares arbitry bot.',
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        'License :: MIT License',
        'Programming Language :: Python :: 3.7',
      ],
    version=src.__version__,
    license='MIT',
    platforms=['Linux'],
    install_requires=[
        'aiofiles==0.4.0',
        'aiohttp==3.5.4',
        'beautifulsoup4==4.7.1',
        'Cython==0.29.3',
        'lxml==4.3.0',
        'websockets==7.0',
        'markdown',
        'uvloop',
        'numpy',
    ],
    include_package_data=True,
    packages=find_packages(),
    package_data={
        'src': ['*.md', 'LICENSE']
    },
    entry_points={
        'console_scripts':
            ['rin = src.rin:main']
    },
    zip_save=False,
    ext_modules=cythonize(['src/*/*.pyx'], annotate=True),
    cmdclass={'build_ext': build_ext},
)
