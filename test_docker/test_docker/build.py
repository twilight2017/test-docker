"""实现构建过程设计"""
import shutil
import os
import subprocess
from loguru import logger
from test_docker.test_docker.project import Project


def build(project: Project, tmp_dir: str, use_cache=False)
    # 1.检查必要文件
    project.check_files()
    # 2.把项目移到暂时文件夹下
    shutil.copytree(project.project_dir, tmp_dir)
    # 3.复制项目目录的dockerfile到暂时目录的dockerfile中
    new_dockerfile_path = os.path.join(tmp_dir, 'Dockerfile')
    shutil.copy(project.dockerfile_path, new_dockerfile_path)

    # 4.write entrypoint
    with open(new_dockerfile_path, 'a') as fp:
        fp.write(f'\nCMD {project.entrypoint}')

    # 5.设置cache_option
    cache_option = ''if use_cache  else '--no-cache'

    # 6.准备docker args
    docker_cmd = f'docker build . --progress plain {cache_option} --tag{project.name}:{project.git_repo.head.object.hexsha}'
    docker_cmd += project.docker_args
    logger.info(f"Docker command: {docker_cmd}")
    subprocess.call(docker_cmd, shell=True, cwd=tmp_dir, bufsize=1)
    # 7.调用子进程执行build过程