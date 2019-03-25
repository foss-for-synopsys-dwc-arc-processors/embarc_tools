#!/bin/sh
die() {
    echo " *** ERROR: " $*
    exit 1
}
# Check codestyle
pycodestyle embarc_tools --ignore=E501
pyflakes embarc_tools

# Install gnu toolchain
TOOLCHAIN="gnu"
TOOLCHAIN_VER="latest"
TOOLCHAIN_CACHE_FOLDER=".cache/toolchain"
ARC_DEV_GNU_ROOT="/u/arcgnu_verif/gnu_builds"
ARC_DEV_MW_ROOT="/u/relauto/.TOOLS_ROOT/ToolsCommon/MWDT_eng/"

if [ ! -d $TOOLCHAIN_CACHE_FOLDER ] ; then
    mkdir -p .cache/toolchain || die "Failed to create cache folder for toolchain"
fi

if [ "${TOOLCHAIN}" == "gnu" ] ; then
    ARC_DEV_TOOL_ROOT="${ARC_DEV_GNU_ROOT}/${TOOLCHAIN_VER}/elf32_le_linux"
else
    ARC_DEV_TOOL_ROOT="${ARC_DEV_MW_ROOT}/mwdt_${TOOLCHAIN_VER}/linux/ARC"
    if [ ! -d $ARC_DEV_TOOL_ROOT ] ; then
        ARC_DEV_TOOL_ROOT="${ARC_DEV_MW_ROOT}/${TOOLCHAIN_VER}/linux/ARC"
    fi
fi
[ "${TRAVIS}" == "true" ] && {
    if [ "${TOOLCHAIN}" == "gnu" ] ; then
        python .ci/toolchain.py -v $TOOLCHAIN_VER -c $TOOLCHAIN_CACHE_FOLDER  || die
        if [ -d $TOOLCHAIN_CACHE_FOLDER ] ; then
            if [ -d $TOOLCHAIN_CACHE_FOLDER/$TOOLCHAIN_VER ] ; then
                ARC_DEV_TOOL_ROOT="${TOOLCHAIN_CACHE_FOLDER}/${TOOLCHAIN_VER}"
            fi
        fi
    elif [ "${TOOLCHAIN}" == "mw" ] ; then
        die "Metaware toolchain is not supported in Travis CI now."
    else
        die "Toolchain ${TOOLCHAIN} not supported in travis ci"
    fi
}


if [ -d $ARC_DEV_TOOL_ROOT ] ; then
    bash .ci/linux_env_set_arc.sh -t $TOOLCHAIN -r $ARC_DEV_TOOL_ROOT || die
    [ ! -e "arctool.env" ] && die "arctool.env doesn't exist"
    source arctool.env || die
    rm -rf arctool.env || die
else
    die "The toolchain path does not exist "
fi

if [ "${TOOLCHAIN}" != "sphinx" ] ; then
    if [ "${TOOLCHAIN}" == "gnu" ] ; then
        arc-elf32-gcc -v || die "ARC GNU toolchain is not installed correctly"
    else
        ccac -v || die "MWDT toolchain is not installed correctly"
    fi
fi
# Start unittest
export PYTHONPATH=$PYTHONPATH:/home/travis/build/wangnuannuan/embarc_tools
python test/main.py
