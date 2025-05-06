from setuptools import setup

setup(
    name='namesilo_api',
    version='0.1-1',
    description='A Python3 wrapper for namesilos API',
    url='https://github.com/dhoessl/python_namesilo_api',
    author="Dominic Hößl",
    author_email="dominichoessl@gmail.com",
    license="",
    packages=['namesilo_api'],
    install_requires=['requests'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
    ]
)
