from distutils.core import setup
import py2exe

setup(console=[{
            "script": "downloader.py",
            "icon_resources": [(1, "icon.ico")]
        }])