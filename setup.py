from setuptools import setup, find_packages

setup(
    name='synchaev',
    version='0.1.0',
    author='Allan Niemerg, Harsh Raj',
    author_email='harsh777111raj@gmail.com',
    description='A project to simulate agent interaction with synthetic environments',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/UptownResearch/synchaev',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'langchain==0.0.275',
        'openai==0.28.0',
        'streamlit==1.29.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
