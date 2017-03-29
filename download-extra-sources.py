"""
download-extra-sources.py

This script can be used to download extra source repositories listed in a recipe meta.yaml file.
They must be listed in the 'extra' section, as shown in the example below.

##
## meta.yaml:
##

package:
  name: multisrc-example
  version: "0.1"

source:
  fn: llvm-3.8.0.src.tar.xz
  url: http://llvm.org/releases/3.8.0/llvm-3.8.0.src.tar.xz
  md5: 07a7a74f3c6bd65de4702bf941b511a0

extra:
  sources:
    cfe:
      fn: cfe-3.8.0.src.tar.xz
      url: http://llvm.org/releases/3.8.0/cfe-3.8.0.src.tar.xz
      md5: cc99e7019bb74e6459e80863606250c5



Run this script from build.sh, using conda's *root* interpreter, as shown here.

##
## build.sh
##
CONDA_PYTHON=$(conda info --root)/bin/python
${CONDA_PYTHON} ${RECIPE_DIR}/download-extra-sources.py

# ... build commands go here ...
"""
from __future__ import print_function

import os
from conda_build import source
from conda_build import config
from conda_build.metadata import MetaData

def split_path(path):
    bits = []
    while path != '/':
        path, tail = os.path.split(path)
        bits.append(tail)
    bits.append(path)
    bits.reverse()
    return bits


def main():
    print()
    print("Getting extra source packages.")
    config.verbose = True
    cwd = os.getcwd()
    bits = split_path(cwd)

    croot = os.path.join(*bits[:-3])
    build_id = bits[-3]

    # Need an extra directory in work_dir so conda extract the package to the
    # same level as the existing one.
    multi_pkg = os.path.join(*bits[:-1], 'multi-pkg')
    if not os.path.exists(multi_pkg):
        os.makedirs(multi_pkg)

    # Get the extra_source section of the metadata.
    recipe_dir = os.environ["RECIPE_DIR"]
    metadata = MetaData(recipe_dir)
    extra_sources_sections = metadata.get_section('extra')['sources']

    for name, source_section in extra_sources_sections.items():
        print("Extra source: %s" % name)
        print("-"*75)
        # Create a fake metadata which contains the extra source_section.
        newmetadata = metadata.copy()
        newmetadata.meta['source'] = source_section
        newconfig = config.get_or_merge_config(
            newmetadata.config, croot=croot, build_id=build_id)
        newconfig.verbose = True

        # Download+extract source.
        source.provide(newmetadata, newconfig)
        print("-"*75)

    print("Extra source packages download and extracted!")
    print()


if __name__ == "__main__":
    main()
