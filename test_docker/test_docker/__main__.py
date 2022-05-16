"""函数入口点"""
import argparse
from tempfile import mkdtemp
import toml
import shutil
from loguru import logger


# TODO:用argparse包输入解析参数：参数包括：toml_path和是否使用cache
"""官方文档：argparse第一步就是创建一个ArgumentParser对象，该对象将包含将命令行解析成Python数据类型所需的全部信息"""
parser = argparse.ArgumentParser(prog="mdocker")
# 给一个ArgumentParser添加程序参数信息通过add_argument()方法完成
parser.add_argument('toml_path', help='Path to a TOML configuration file')
parser.add_argument('--use-cache', help='If set, "--no-cache" won\'t be passed to docker build.', action='store_true')

# TODO:声明日志存放文件
logger.add('logfile.txt')


# TODO:重写override_conf(conf_dict, key, new_value)
def override_conf(conf: dict, key: str, new_value: str):
    if key in conf and conf[key] != new_value:
        logger.info(f'Overriding conf key: {key} with new value:{new_value}.')
    conf[key] = new_value


# TODO: 入口函数
def cli():
    # 1.解析参数
    # ArgumentParser通过parse_args()方法解析参数
    args = parser.parse_args()
    # 2.读取配置
    conf = toml.load(args.toml_path)
    # 3.根据配置获取toml和dockerfile
    default_toml, default_dockerfile = get_project_tempale(get_key(conf, 'template'))  # 获得的只是模板文件的路径
    # 4.声明project实例
    default_conf = {}
    if default_toml:
        default_conf = toml.load(default_toml)
    if default_dockerfile:
        default_conf['dockerfile'] = str(default_dockerfile)  # 字典中的'dockerfile键存放dockerfile路径值'
    for k, v in conf.items():
        override_conf(default_conf, k, v)

    # 5.构建
    # 5.1 创建临时文件夹
    tmp_dir = mkdtemp()
    # 5.1用try-cache实现build过程
    try:
        project = Project(default_conf)
        build(project, tmp_dir, args.use_cahche)  # 需要传入是否使用cache的参数
    except TDockerError as e:
        sys.exit(str(e))
    finally:
        shutil.rmtree(tmp_dir)




