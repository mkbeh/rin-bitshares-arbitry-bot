import src

from setuptools import setup, find_packages


# TODO Add
#   1) cython compile

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
)
