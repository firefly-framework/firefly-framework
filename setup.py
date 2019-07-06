import setuptools
from setuptools.command.develop import develop
from setuptools.command.install import install

with open("README.md", "r") as fh:
    long_description = fh.read()


# class PostDevelopCommand(develop):
#     def run(self):
#         import firefly as ff
#         ff.container.kernel.install_extension()
#         develop.run(self)
#
#
# class PostInstallCommand(install):
#     def run(self):
#         import firefly as ff
#         ff.container.kernel.install_extension()
#         install.run(self)


setuptools.setup(
    name='firefly-framework',
    version='0.1',
    author="JD Williams",
    author_email="me@jdwilliams.xyz",
    description="A dependency injection framework for python",
    long_description=long_description,
    # long_description_content_type="text/markdown",
    url="https://github.com/firefly19/python-framework",
    entry_points={
        'console_scripts': ['firefly=firefly.api.cli:main']
    },
    install_requires=[
        'aiohttp>=3.5.4',
        'aiohttp-cors>=0.7.0',
        'asyncio>=3.4.3',
        'dirsync>=2.2.3',
        'inflection>=0.3.1',
        'python-dotenv>=0.10.3',
        'pyyaml>=5.1.1',
        'terminaltables>=3.1.0',
        'firefly-dependency-injection>=0.1',
    ],
    packages=setuptools.PEP420PackageFinder.find('src'),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ]
    # cmdclass={
    #     'develop': PostDevelopCommand,
    #     'install': PostInstallCommand,
    # }
)
