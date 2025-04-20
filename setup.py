import io
from os.path import abspath, dirname, join
from setuptools import find_packages, setup


HERE = dirname(abspath(__file__))
LOAD_TEXT = lambda name: io.open(join(HERE, name), encoding='UTF-8').read()
DESCRIPTION = '\n\n'.join(LOAD_TEXT(_) for _ in [
    'README.rst'
])

setup(
  name = 'cgnlib',      
  packages = ['cgnlib'], 
  version = '0.1.6', 
  license='MIT', 
  description = 'CGNLib, a Python library, enhances GN by allowing experimentation with different centrality metric. This flexibility can improve community detection results.',
  long_description=DESCRIPTION,
  author = 'chinnapongpsu',                 
  author_email = 'chinnapong.a@psu.ac.th',     
  url = 'https://github.com/chinnapongpsu/cgnlib',  
  download_url = 'https://github.com/chinnapongpsu/cgnlib/archive/refs/tags/0.1.6.zip',  
  keywords = [
    'cgn',
    "Community Detection"
    "Community",
    "Detection"
    "Girvan-Newman" 
    "Centrality Metrics"
              ],
  install_requires=[          
          'networkx',
          'igraph',
          'netcenlib',
          'matplotlib'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',     
    'Intended Audience :: Education',     
    'Topic :: Utilities',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
  ],
)