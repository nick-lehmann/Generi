 🐳 Generi
===========

Generi lets you create huge set of dockerfiles from a template, build and tag all of them and optionally push them to a repository of your choice. By using matrix builds, it's a breeze to build a huge variety of images for your application.

```eval_rst
.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   usage/usage
   usage/optimisation
```

🐍 Installation
===============

```bash
$ pip install generi
```

Or if you prefer an alternative package manager.

```bash
$ poetry add generi
$ pipenv install generi
```

✈️ Quickstart
=============

`Generi` can be configured using a simple yaml file that defines your matrix build. 

*schema.yaml*

```yaml
parameters:
  python_version:
    - 2.7
    - 3.5
    - 3.6
    - 3.7
  operating_system:
    - buster
    - alpine

template: templates
output: "output/{{ python_version }}/{{ operating_system }}"
image: "nicklehmann/myapplication:py{{ python_version }}-{{ operating_system }}"

registry:
  username: nicklehmann
```

*templates/Dockerfile*

```dockerfile
FROM python:{{ python_version }}-{{ operating_system }}

COPY main.py main.py

CMD ["python", "main.py"]
```

First, render your dockerfiles by running

```bash
$ generi write schema.yaml
```

After that, build and optionally push your image.

```bash
$ generi build schema.yaml
$ generi push schema.yaml
```

Indices
=======

```eval_rst
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```
