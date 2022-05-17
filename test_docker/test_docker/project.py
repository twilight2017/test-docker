""" project类设计 """
import pathlib
import toml
import git
import re
import shutil
from tempfile import mkdtemp
import os
from test_docker.test_docker.exceptions import InvaildConfiguration, InvalidRepo
from typing import Union, Optional, Any, List, Tuple

_project_templates_dir = pathlib.Path(__file__).parent.parent / 'tempaltes'
_scheme_matcher = re.compile('^(git|https|http):')


# TODO: get_key(conf_dict: dict, key, required_type: type=str, allow_none=True) -> Optinoal[Any]:
def get_key(toml_dict: dict, key: str, required_type: type = str, allow_none=True) -> Optional[Any]:
    keys = key.split('.')
    inner_dict = toml_dict
    key_missing = InvaildConfiguration(f'config key {key} is missing')
    while len(keys) > 1:
        inner_dict = inner_dict.get(keys.pop(0))
        if not isinstance(inner_dict, dict):
            raise key_missing
    value = inner_dict.get(keys[0])
    if not allow_none and value is None:
        raise key_missing

    if value is not None and not isinstance(value, required_type
                                            ):
        raise InvaildConfiguration(f'Config "{key} must be of type "{required_type.__name__}" ')

    return value


class Project:
    # TODO:def __init__(conf:dict/path)
    def __init__(self, conf_dict: Union[pathlib.Path, dict]):
        # 1.git暂时仓库
        self.git_temp_dir = None
        # 2.git 仓库
        self.git_repo = None
        # 以下内容都从conf_dict中读取
        if isinstance(conf_dict, pathlib.Path):
            conf_dict = toml.load(conf_dict)  # 如果是以路径名称给出的，则使用toml包进行加载
        # 3.项目名称
        self.name = get_key(conf_dict, 'name', allow_none=False)
        # 4.项目文件夹
        self.project_dir = get_key(conf_dict, 'project_dir', allow_none=False)
        # 5.dockerfile 文件路径
        self.dockerfile_path = get_key(conf_dict, 'dockerfile_path', allow_none=False)
        # 6.入口参数
        self.entrypoint = get_key(conf_dict, 'entrypoint', allow_none=False)
        # 7.必要文件
        self.required_files = get_key(conf_dict, 'required_files', required_type=list)
        # 8.docker参数
        self.docker_args = get_key(conf_dict, 'docker_args') or ''

        # 判断是否能得到项目的git仓库
        try:
            self.get_project_repo()
        except git.exc.InvaildRepositoryError:
            raise InvalidRepo(f"{self.project_dir} is not a valid git repo.") from None

    # TODO get_project_repo
    def get_project_repo(self):
        # 按url地址进行处理
        if not _scheme_matcher.match(str(self.project_dir)):
            # project_dir is a local path
            if not os.path.exists(self.project_dir):
                raise InvalidRepo(f"{self.project_dir} is not a valid git repo .")
            self.git_repo = git.Repo(self.project_dir)
            return
        # project_dir is an url path
        self.git_temp_dir = mkdtemp()
        # 把url指向的仓库文件复制到临时文件夹下
        self.git_repo = git.Repo.clone_from(self.project_dir, self.git_temp_dir)

    # TODO:检查必要文件是否包含
    def check_files(self):
        # 通过项目路径得到确定的项目地址
        project_dir = pathlib.Path(self.project_dir)
        for file in self.required_files:
            path = project_dir / file
            if not path.exists():
                raise InvaildConfiguration(f'required file {file} is not found')

    # TODO: 删除临时文件夹
    def __del__(self):
        if self.git_temp_dir:
            shutil.rmtree(self.git_temp_dir)


# TODO:列出所有可选择的模板文件 list_project_templates()->List[str]
def list_project_template() -> List[str]:
    conf_files = pathlib.Path(_project_templates_dir).glob('*.toml')
    return [conf.stem for conf in conf_files]


# TODO 得到指定的模板文件 get_project_tempalte(template_name: str) -> tuple
#  需要同时传回toml文件和dockerfile文件，因为一个template_name同时对应.toml和dockerfile
def get_project_template(template_name: str) -> Tuple:
    if not template_name:
        return None, None
    templates_dir = pathlib.Path(_project_templates_dir)
    toml_path = templates_dir / f'{template_name}.toml'
    if not toml_path.exists():
        raise InvaildConfiguration(f'Project template "{template_name}" does not exist')
    dockerfile_path = templates_dir / f'{template_name}.dockerfile'
    if not dockerfile_path.exists():
        dockerfile_path = None
    return toml_path, dockerfile_path
