import setuptools

setuptools.setup(name="POSM",
                 author="Philipp Rigoll",
                 version="0.1",
                 author_email="philipp@rigoll.de",
                 packages=setuptools.find_packages(),
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
                 entry_points={
                     "console_scripts": ["POSM=POSM.main:main"]
                 })
