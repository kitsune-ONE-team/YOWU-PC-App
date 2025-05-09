#!/usr/bin/env python3

# Copyright (c) 2025 kitsune.ONE team.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from setuptools import setup


setup(
    name='YOWU',
    version='0.1.0',
    description='YOWU Headphones App for PC',
    long_description='YOWU PC App to control the headphone lights',
    url='https://github.com/kitsune-ONE-team/YOWU-PC-App',
    download_url='https://github.com/kitsune-ONE-team/YOWU-PC-App',
    author='Yonnji',
    license='GPL3',
    install_requires=(
        'bleak>=0.22.1',
        'pygobject>=3.50.0',
    ),
    packages=(
        'yowu',
    ),
    entry_points={
        'console_scripts': (
            'yowu=yowu.__main__:main',
        ),
    },
)
