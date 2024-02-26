#!/bin/bash

# Function to echo text in specified color using tput and printf
colored_echo() {
    local color=$1
    local text=$2

    # Define color codes using tput
    local black=$(tput setaf 0)
    local red=$(tput setaf 1)
    local green=$(tput setaf 2)
    local yellow=$(tput setaf 3)
    local blue=$(tput setaf 4)
    local magenta=$(tput setaf 5)
    local cyan=$(tput setaf 6)
    local white=$(tput setaf 7)
    local reset=$(tput sgr0)

    # Choose color based on input
    case $color in
        "black") color_code=$black ;;
        "red") color_code=$red ;;
        "green") color_code=$green ;;
        "yellow") color_code=$yellow ;;
        "blue") color_code=$blue ;;
        "magenta") color_code=$magenta ;;
        "cyan") color_code=$cyan ;;
        "white") color_code=$white ;;
        *) color_code=$reset ;; # Default to reset if no color match
    esac

    # Print the colored text
    printf "%b%s%b\n" "$color_code" "$text" "$reset"
}

colored_echo "green" "-------------- Installing Flexutils scripts --------------"

# Get the full path of the current script, resolving symlinks
SCRIPT_PATH=$(realpath "${BASH_SOURCE[0]}")
SCRIPT_DIR=$(dirname "SCRIPT_PATH")

# Get package version
VERSION=$(PYTHONPATH="$SCRIPT_DIR/" python -c "from flexutils_script import __version__; print(__version__)")

# Check flexutils environment is installed and remove it in case a new version is available
PREV_ENV_NAME=$(conda env list | grep "$search_word" | awk '{print $1}')
PREV_VERSION="${env_name##*-}"

if [ "PREV_VERSION" != "$VERSION" ] && [ ! -z "PREV_ENV_NAME" ]; then
    echo "Found Flexutils environment(s)"
    conda env remove -n $PREV_ENV_NAME
fi

# Source the conda.sh script
CONDA_PATH=$(which conda)
CONDA_PATH=$(realpath "CONDA_PATH")
CONDA_SH="${CONDA_PATH%/bin/conda}/etc/profile.d/conda.sh"
source "$CONDA_SH"

# Install new flexutils environment
conda env create flexutils-$VERSION -f $SCRIPT_DIR/requirements/flexutils_env.yml

# Install current package in Flexutils env
conda activate flexutils-$VERSION
pip install -e $SCRIPT_DIR

# Setup Tensorflow
mkdir -p $CONDA_PREFIX/etc/conda/activate.d
echo \'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/\\n\' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
echo \'export XLA_FLAGS=--xla_gpu_cuda_data_dir=$CONDA_PREFIX/lib/\\n\' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
mkdir -p $CONDA_PREFIX/lib/nvvm/libdevice
cp $CONDA_PREFIX/lib/libdevice.10.bc $CONDA_PREFIX/lib/nvvm/libdevice/

# Deactivate environment and finish installation
conda deactivate
colored_echo "green" "-------------- Installation finished succesfully --------------"
