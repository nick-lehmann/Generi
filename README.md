![Generi logo](/docs/images/icon.png?raw=true "Generi logo")

🐳 About
========

Generi is a tool to automatically create Dockerfiles and build images for a large combination of different factors. It is the right tool if you need to build many similar images with slightly different parameters. 

For example, say you are developing an app. You might want to build one docker image for python 2.7, 3.6, 3.8. And for each python version, you need one with a database included or not. And all that for each tag. If you have experienced a scenario like this, try out Generi.

🎇 Features
===========

- Configuration in yaml
- Specify different parameter to form a build matrix
- Generate Dockerfile for each combination
- Build all variations of your image with one command
- Push to the repository of your choice
- Everything customisable using [Jinja](https://jinja.palletsprojects.com/en/2.10.x/)

🛠️ Examples
===========

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
  version:
    - 1.0
    - 0.12.17

template: templates
output: "output/{{ python_version }}/{{ operating_system }}/{{ version }}"

tag: "nicklehmann/myapplication:py{{ python_version }}-{{ version }}-{{ operating_system }}"
```
