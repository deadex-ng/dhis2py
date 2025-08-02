from setuptools import setup

setup(
    name='dhis2py',
    version='0.1.0',    
    description='A DHIS2 Python package',
    url='',
    author='Fumbani Banda',
    author_email='thisisfumba@gmail.com',
    license='BSD 2-clause',
    packages=['dhis2py'],
    install_requires=['requests 2.32.4',                     
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3.12.2',
    ],
)