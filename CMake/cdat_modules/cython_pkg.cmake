set(CYTHON_MAJOR 0)
set(CYTHON_MINOR 22)
set(CYTHON_PATCH )
set(CYTHON_VERSION ${CYTHON_MAJOR}.${CYTHON_MINOR})
set(CYTHON_URL ${LLNL_URL} )
set(CYTHON_GZ Cython-${CYTHON_VERSION}.tar.gz)
set(CYTHON_MD5 e67b03e8b3667c8e4e7c774ef2e2b638)
set(CYTHON_SOURCE ${CYTHON_URL}/${CYTHON_GZ})

add_cdat_package_dependent(Cython "" "" OFF "CDAT_BUILD_LEAN" OFF)
