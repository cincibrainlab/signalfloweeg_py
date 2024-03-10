from setuptools import setup, find_packages

setup(
    name='signalfloweeg',
    version='0.1.0',
    description='A Python module for EEG signal processing and analysis',
    author='Ernie Pedapati',
    author_email='ernest.pedapati@cchmc.org',
    url='https://github.com/cincibrainlab/signalfloweeg',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'mne',
        # Add more dependencies here
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)


