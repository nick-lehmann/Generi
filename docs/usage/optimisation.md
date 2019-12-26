Build optimisation
==================

Docker uses a cache mechanism to speed up image builds. In order to create a fast and efficient build pipeline, it is essential to understand how the cache works. This [section](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#leverage-build-cache) in the official guide about best practices gives a good overview. 

Since most computer have more than one CPU core, `Generi` builds more than one image at a time. When using matrix builds, it is very likely that very similar images get built at the same time. In this case, it is very likely that the same layers gets built multiple times which is inefficient and slow. 

Therefore, `Generi` tries to spread out similar images across the build process. Very different images should be built first to populate the docker cache, making the next builds very fast.

Image you use the following example dockerfile as a template for your matrix build.

```yaml
FROM python:{{ python_version }}-alpine
# ...
RUN apk add openssl-dev=={{ openssl_version }}
# ...
RUN pip install your_package=={{ package_version }}
```

In this example you have a python application that has a native dependency on `openssl`. You want to build images for many python versions, against multiple versions of `openssl` and with different versions of your package. The `Generi` config file for your matrix build could look like this.

```yaml
parameters:
  python_version:
    - 3.5
    - 3.6
    - 3.7
    - 3.8
  openssl_version:
    - 1.1.1d-r3
    - 1.1.1d-r2
  package_version:
    - 0.10.0
    - 1.0
```

First, `Generi` will create a parameter matrix that contains all possible combinations of the parameter your provided. The first two combinations may then look like this:

```json
[{
    "python_version": "3.5",
    "openssl_version": "1.1.1d-r3",
    "package_version": "0.10.0"
}, {
    "python_version": "3.5",
    "openssl_version": "1.1.1d-r3",
    "package_version": "1.0"
}]
```

If you compare these parameter combinations with the Dockerfile from above you can see that the rendered Dockerfile will be the same, except for the last line where you install your python package. Building those two images in parallel does not make much sense as most of the layers will be built twice. For that reason, `Generi` will start by building the images with different python versions, because there will be no common layer between those images.

