set(NC4_MAJOR_SRC 4)
set(NC4_MINOR_SRC 4)
<<<<<<< HEAD
set(NC4_PATCH_SRC 0)
set(NC4_URL ${LLNL_URL})
set(NC4_GZ netcdf-c-${NC4_MAJOR_SRC}.${NC4_MINOR_SRC}.${NC4_PATCH_SRC}.tar.gz)
set(NC4_MD5 4e3d3b05ab53d0ae6036a1a0fe1506e5)
=======
set(NC4_PATCH_SRC 0-rc5)
set(NC4_URL ${LLNL_URL})
set(NC4_GZ netcdf-c-${NC4_MAJOR_SRC}.${NC4_MINOR_SRC}.${NC4_PATCH_SRC}.tar.gz)
set(NC4_MD5 a542254b7fc27258be9e8a11d74c97a0)
>>>>>>> Update to latest 4.4.0-rc5 source, and update archive name

set (nm NC4)
string(TOUPPER ${nm} uc_nm)
set(${uc_nm}_VERSION ${${nm}_MAJOR_SRC}.${${nm}_MINOR_SRC}.${${nm}_PATCH_SRC})
set(NETCDF_VERSION ${NC4_VERSION})
set(NETCDF_SOURCE ${NC4_URL}/${NC4_GZ})
set(NETCDF_MD5 ${NC4_MD5})

add_cdat_package(NetCDF "" "" ON)
