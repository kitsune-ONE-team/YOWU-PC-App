YOWU Headphones App for PC
==========================

YOWU PC App to control the headphones light.

This is not official App and not related to YOWU. It was inspired by [Yowu-CatCaller](https://github.com/FredYeye/Yowu-CatCaller)


Supported headphones
--------------------

* YOWU-SELKIRK-4
* YOWU-SELKIRK-4GS


Common usage
------------

* Pair and connect to the headphones.
* Start an app.


Usage on Windows
----------------

**Running from binary**

* Download the EXE file from releases. 
* Open it.

**Running and building from source**

Install [anaconda](https://www.anaconda.com) or [miniconda](https://docs.conda.io/en/latest/miniconda.html).

Create a new environment:
```conda env create -f yowu.yaml```

Activate the environment:
```conda activate yowu```

Run from source:
```python -m yowu```

Build from source:
```pyinstaller YOWU.spec```


Usage on Linux
--------------

**Installing and running from source**

Install or upgrade to the latest version:
```python -m pip install -U --user git+https://github.com/kitsune-ONE-team/YOWU-PC-App```

Run the installed version:
```yowu```


Requirements
------------

* [python](https://python.org)
* [pygobject](https://pygobject.gnome.org/)
* [gtk3](https://gtk.org)
* [bleak](https://github.com/hbldh/bleak)
