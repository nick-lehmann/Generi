import os
import subprocess
from invoke import task

try:
    from sphinx.cmd.build import build_main as sphinx_build
except ImportError:
    sphinx_build = None


@task()
def docs(context, image=False):
    """ Generate the documentation """
    if not sphinx_build:
        raise ValueError('''
            The sphinx build command is not available. 
            You have probably not installed sphinx in your environment
        ''')

    print('Start building docs')
    working_dir = os.getcwd()
    source_dir = os.path.join(working_dir, 'docs')
    target_dir = os.path.join(working_dir, 'dist/docs')

    sphinx_build(argv=[
        source_dir,
        target_dir
    ])

    if image:
        subprocess.run('docker build -t nicklehmann/generi_docs -f docs/Dockerfile .', shell=True)


@task()
def clear(context):
    context.run(
        'docker rmi -f $(docker images --filter=reference="*/my*" -q)',
        shell='/bin/ash'
    )
