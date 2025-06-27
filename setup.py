from setuptools import setup, find_packages

setup(
    name='collapsi',
    version='0.0.1',
    description='Collapsi simulation and Q-Learning',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=['networkx',
                      'numpy'
                      ]
)