'''
/*
 * Copyright 2016 Alexander Schmitt
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

from setuptools import setup, find_packages


with open("README.rst") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="thingload",
    version="0.0.1",
    description="Sample project to push the CPU load to AWS IoT",
    long_description=readme,
    author="Alexander Schmitt",
    author_email="alexander.al.schmitt@deutschebahn.com",
    url="https://github.com/ac-schmitt/thingload",
    license=license,
    packages=find_packages(exclude=("tests", "docs"))
)
