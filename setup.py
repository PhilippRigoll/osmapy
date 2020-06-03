import setuptools

setuptools.setup(name="POSM",
                 author="Philipp Rigoll",
                 version="0.1.5",
                 author_email="philipp@rigoll.de",
                 url="https://github.com/PhilippRigoll/POSM",
                 packages=setuptools.find_packages(),
                 include_package_data=True,
                 install_requires=[
                     "numpy",
                     "Pillow",
                     "PyYAML",
                     "PySide2",
                     "easydict",
                     "lxml",
                     "requests",
                     "gpxpy"
                 ],
                 python_requires=">=3.6",
                 entry_points={
                     "console_scripts": ["POSM=POSM.main:main"]
                 })
