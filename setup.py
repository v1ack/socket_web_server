import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='socket_web_server',
    version='0.1',
    author='v1ack',
    author_email='kirilkin12@gmail.com',
    description='Simple socket async http server',
    long_description=long_description,
    install_requires=['aiomisc', 'configargparse', 'pathlib'],
    entry_points={
        "console_scripts": [
            "socket_web_server = socket_web_server.__main__:main",
        ]
    },
    packages=setuptools.find_packages(),
    python_requires='>=3.7'
)