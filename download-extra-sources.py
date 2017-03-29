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

class SpecialConfig(config.Config):
    """Allow overriding the work_dir property."""

    @property
    def work_dir(self):
        return self._work_dir


def split_path(path):
    bits = []
    while path != '/':
        path, tail = os.path.split(path)
        bits.append(tail)
    bits.append(path)
    bits.reverse()
    return bits


def has_only_one_dir(path):
    """
    Conda has this weird thing where if the workdir is only a single directory,
    it'll change into it and use that as the workdir.
    """
    lst = [fn for fn in os.listdir(path) if not fn.startswith('.')]
    if len(lst) != 1:
        return ''
    dir_path = os.path.join(path, lst[0])
    if not os.path.isdir(dir_path):
        return ''
    return dir_path


def main():
    print()
    print("Getting extra source packages.")
    # Force verbose mode
    config.verbose = True
    cwd = os.getcwd()

    # Get the metadata for the recipe
    recipe_dir = os.environ["RECIPE_DIR"]
    metadata = MetaData(recipe_dir)
    print(metadata.name())
    print("-"*75)
    print('       cwd:', cwd)

    # Figure out the work_dir
    # Look upwards for a directory with the name 'work'.
    # FIXME: Why does metadata.config.work_dir not return the correct
    # directory?
    bits = split_path(cwd)
    dirname = []
    while bits and bits[-1] != 'work':
        dirname.insert(0, bits.pop(-1))
    dirname = os.path.join(*dirname, '')

    work_dir = bits.pop(-1)
    assert work_dir == 'work'

    build_id = bits.pop(-1)
    croot = os.path.join(*bits)

    work_dir = os.path.join(croot, build_id, 'work')
    if has_only_one_dir(work_dir):
        real_work_dir = work_dir
    else:
        real_work_dir = os.path.join(croot, build_id)

    print('  work dir:', real_work_dir)
    print('conda root:', croot)
    print('  build id:', build_id)
    print('   src dir:', dirname)

    extra_sources_sections = metadata.get_section('extra')['sources']
    for name, source_section in extra_sources_sections.items():
        print()
        print("Extra source: %s" % name)
        print("-"*75)
        # Create a fake metadata which contains the extra source_section.
        newmetadata = metadata.copy()
        newmetadata.meta['source'] = source_section

        if has_only_one_dir(work_dir):
            extra_work_dir = real_work_dir
        else:
            extra_work_dir = os.path.join(real_work_dir, name)

        newmetadata.config.__class__ = SpecialConfig
        newmetadata.config._work_dir = extra_work_dir
        print("Work Directory:", newmetadata.config.work_dir)

        # Download+extract source.
        source.provide(newmetadata, newmetadata.config)

        print("-"*75)

    print()
    print("Extra source packages download and extracted!")
    print()
    print("Work Directory contents (%s)" % real_work_dir)
    print("-"*75)
    print(os.listdir(real_work_dir))
    print()


if __name__ == "__main__":
    main()
