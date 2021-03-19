import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="usb-rfid-reader-cybrnode",
    version="0.0.1",
    author="Huzaifah Asif",
    author_email="huzaifah.asif.b@gmail.com",
    description="Package for reading input from USB RFID Readers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cybrnode/usb-rfid-reader",
    project_urls={
        "Bug Tracker": "https://github.com/cybrnode/usb-rfid-reader/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)