#!/bin/sh

software_base=/workfs/hxmt/lizhengheng/software

# gcc 5.4.0
# echo " - gcc 5.4.0"
export PATH=$software_base/gcc-5.4.0/bin:$PATH
export LD_LIBRARY_PATH=$software_base/gcc-5.4.0/lib:$software_base/gcc-5.4.0/lib64:$LD_LIBRARY_PATH
export FC=$software_base/gcc-5.4.0/bin/gfortran
export CC=$software_base/gcc-5.4.0/bin/gcc
export CXX=$software_base/gcc-5.4.0/bin/g++

# python 2.7.12
# echo " - python 2.7.12"
export PATH=$software_base/python-2.7.12/bin:$PATH
export LD_LIBRARY_PATH=$software_base/python-2.7.12/lib:$LD_LIBRARY_PATH

# python 3.6.1
# echo " - python 3.6.1"
export PATH=$software_base/python-3.6.1/bin:$PATH
export LD_LIBRARY_PATH=$software_base/python-3.6.1/lib:$LD_LIBRARY_PATH

