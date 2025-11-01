* Setup for Slicer related development with python

** Conda environment

We use the python 3.10, create a conda environment

```shell
conda create -n slicer-env-py310 python=3.10\
```

Just add numpy as an additional package 

```shell
pip install numpy matplotlib
```

** Example

The script can achieve a comparison analysis using as inputs the seedplan files

```shell
python compareResults_3Studies.py --compare /mnt/localstore3/H001/001-M-30/Mediplan3D/seedplan.xml /mnt/localstore3/H002/001-M-30/Mediplan3D/seedplan.xml  /mnt/localstore3/H003/001-M-30/Mediplan3D/seedplan.xml 

python compareResults_3Studies.py --compare /mnt/localstore3/H001/002-F-36/Mediplan3D/seedplan.xml /mnt/localstore3/H002/002-F-36/Mediplan3D/seedplan.xml  /mnt/localstore3/H003/002-F-36/Mediplan3D/seedplan.xml

# all others are generated in the same way
```


