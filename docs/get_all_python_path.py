import os
import shutil
import logging

__author__ = "Guanjie Wang"
__email__ = "wangguanjie@buaa.edu.cn"
__date__ = " /8/2018"

path_exid = ['build', '__pycache__']
dir_exid = path_exid

gogal_suffix = '.html'
other_exid = ['.ows', '.py', '.qss', '.tab', '.info', '.js', '.txt', '.log', '.css']
_file_exid = ['.pyc', '.pyd', '.pyx']
c_exid = ['.c', '.cpp', '.h']
pic_exid = ['.svg', '.png', '.jpg', '.ico', '.DS_Store', '.xlsx', '.gz']
file_exid = other_exid + c_exid + pic_exid + _file_exid


class GetAllPyFiles:
    def __init__(self, fn_dir, rped_name='Orange', gogal_name='Alkemiet'):
        """
        要替换名字的话需要输入参数，否则不需要任何参数
        :param rped_name: 被替换的名字
        :param gogal_name: 替换后的名字
        """
        self.log = log_test('ROWA', './rowa.log')
        self.nopy_now_path, self.valid_now_path = [], []
        self.nopy_gogal_path, self.valid_gogal_path = [], []
        self.picture_now_path, self.picture_gogal_path = [], []
        self.rped_name = rped_name
        self.gogal_name = gogal_name
        self.path = os.walk(fn_dir)
        self.vf_num, self.tf_num, self.vd_num, self.td_num = 0, 0, 0, 0

    def ex_all_nopython_path(self, pri=False, mv_olddir_to_new_dir=True):
        """
        寻找当前目录下所有的python文件, 非python文件，*.pyc(d,x)文件 以及图片文件
        还可以移动文件夹到指定目录中
        :param pri: 是否打印路径信息
        :param mv_olddir_to_new_dir: 是否复制到新路径下，并创建新目录
        :return: None
        """
        for nowpath, nowdir, file in self.path:
            _pexid = [i in nowpath for i in path_exid]
            if any(_pexid):
                continue
            else:
                if pri:
                    print(nowpath)
                if mv_olddir_to_new_dir:
                    gogal_path = nowpath.replace(self.rped_name, self.gogal_name, -1)
                    self.check_path(gogal_path)
                else:
                    gogal_path = nowpath

                for nd in nowdir:
                    self.td_num += 1
                    _dexid = [i in nd for i in dir_exid]
                    if any(_dexid):
                        continue
                    else:
                        self.vd_num += 1
                        if pri:
                            print('    ', nd)
                        if mv_olddir_to_new_dir:
                            __nd = os.path.join(gogal_path, nd)
                            self.check_path(__nd)
                            self.log.warning('Make Dir: %s' % __nd)
                        else:
                            pass

                for m in file:
                    if mv_olddir_to_new_dir:
                        gm = m.replace(self.rped_name, self.gogal_name, -1)
                    else:
                        gm = m
                    self.tf_num += 1
                    __nowpath = os.path.join(nowpath, m)
                    __gogalpath = os.path.join(gogal_path, gm)

                    if gogal_suffix not in m:
                        if any([pp in m for pp in pic_exid]):
                            self.picture_now_path.append(__nowpath)
                            self.picture_gogal_path.append(__gogalpath)
                        else:
                            self.nopy_now_path.append(__nowpath)
                            self.nopy_gogal_path.append(__gogalpath)
                    else:
                        if any([i in m for i in _file_exid]):
                            # exinclude  *.pyc *.pyx *.pyd
                            continue
                        else:
                            self.vf_num += 1
                            self.valid_now_path.append(__nowpath)
                            self.valid_gogal_path.append(__gogalpath)
                            if pri:
                                print('        ', m)
        self.__push_info()

    def __push_info(self):
        print('total files: %d,\n'
              'valid python files: %d,\n'
              'picture files: %d,\n'
              'other files: %d,\n'
              'total dir: %d,\n'
              'valid dir: %d ' % (self.tf_num, self.vf_num, len(self.picture_now_path), len(self.nopy_now_path),
                                  self.td_num, self.vd_num))

    @staticmethod
    def check_path(path):
        """
        检查当前面录是否存在，不存在的话新建，存在的话无所作为
        :param path:
        :return:
        """
        if not os.path.isdir(path):
            os.mkdir(path)
        else:
            pass

    def auto_run(self, nopy=True, valid=True, picture=True, mv_olddir_to_new_dir=True):
        """
        自动将一个Module改成其他名字，并保持文件夹结构不变
        将所有python脚本中导入模块替换掉
        :param nopy: 是否替换非python脚本中的关键字
        :param valid: 是否替换python脚本中的关键字
        :param picture: 是否复制目录中的图片文件
        :param mv_olddir_to_new_dir: 在搜素过程中是否新建目录替换，如果否的话则会覆盖当前目录下的脚本
        :return: None
        """
        rpfi = OperateFile(rped=self.rped_name, gogal=self.gogal_name, log=self.log)
        self.ex_all_nopython_path(mv_olddir_to_new_dir=mv_olddir_to_new_dir)
        tmp_read, tmp_write = [], []
        if nopy:
            if len(self.nopy_gogal_path) > 0:
                tmp_read.extend(self.nopy_now_path)
                tmp_write.extend(self.nopy_gogal_path)
        if valid:
            if len(self.valid_gogal_path) > 0:
                tmp_read.extend(self.valid_now_path)
                tmp_write.extend(self.valid_gogal_path)

        assert len(tmp_read) == len(tmp_write)
        for i, fn in enumerate(tmp_read):
            rpfi.rp_file(fn, tmp_write[i])

        if picture:
            for i, fn in enumerate(self.picture_now_path):
                rpfi.cp_file(fn, self.picture_gogal_path[i])


class OperateFile:
    def __init__(self, rped, gogal, log=None):
        """
        对文件的操作，包括替换文件中的名字 和 复制文件
        :param rped: 被替换的字符串
        :param gogal: 替换成的字符串
        :param log: 日志文件
        """
        self.rped_str = rped
        self.gogal_str = gogal
        self.log = log

    def rp_file(self, rfn, wfn=None):
        """
        替换文件中指定内容到指定目录
        :param rfn: 文件初始目录
        :param wfn: 文件替换完之后的目录，如果是None， 默认为初始目录
        :return: None
        """
        if not wfn:
            wfn = rfn

        rdata = self.open_one_file_and_log(fn=rfn, log=self.log)
        wdata = self.replace_one_file(data=rdata, rped=self.rped_str, gogal=self.gogal_str, log=self.log)
        self.write_one_file_and_log(fn=wfn, data=wdata, mode='w', log=self.log)

    def cp_file(self, nfn, gfn):
        """
        复制文件的操作
        :param nfn: 文件初始目录
        :param gfn: 文件终止目录
        :return: None
        """
        try:
            shutil.copy(nfn, gfn)
            self.log.info('CopyPicFr: %s' % nfn)
            self.log.info('CopyPicTo: %s' % gfn)
        except shutil.SameFileError:
            self.log.error("SameFileError: %s" % nfn)


    @staticmethod
    def open_one_file_and_log(fn, log=None):
        with open(fn, 'r', encoding='UTF8') as f:
            try:
                data = f.readlines()
            except UnicodeDecodeError:
                print(fn    )
                raise UnicodeDecodeError
        if log is not None:
            log.info('Starting : %s' % fn)
        return data

    @staticmethod
    def replace_one_file(data, rped="Orange", gogal='Alkemiet', log=None):
        f = []
        for i in data:
            if rped in i:
                replaced_line = i.replace(rped, gogal)
                if log is not None:
                    log.info('BReplaced:        %s' % i.replace('\n', ''))
                    log.info('ReplaceTo:        %s' % replaced_line)
                f.append(replaced_line)
            else:
                f.append(i)
        return f

    @staticmethod
    def write_one_file_and_log(fn, data, mode='w', log=None):
        with open(fn, mode=mode, encoding='UTF8') as f:
            if isinstance(data, str):
                f.write(data)
            elif isinstance(data, list) or isinstance(data, tuple):
                f.write(''.join(data))
            else:
                pass

        if log is not None:
            log.info('WriNewTo : %s' % fn)


def log_test(name=None, filename='./testlg.txt', mode='w'):
    if name is None:
        name = r'Replace Orange with Alkemie'
    tl = logging.getLogger(name)
    tl.setLevel(logging.INFO)
    fld = logging.FileHandler(filename=filename, mode=mode)
    # fmt = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    fmt = logging.Formatter('%(levelname)s: %(message)s')
    fld.setFormatter(fmt)
    tl.addHandler(fld)
    return tl


if __name__ == '__main__':
    # filen = os.path.join(os.getcwd(), 'orangecontrib')
    # gp = GetAllPyFiles(fn_dir=filen, rped_name='Orange', gogal_name='Alkemiet')
    #
    # filen = os.path.join(os.getcwd(), 'vasp')
    # gp = GetAllPyFiles(fn_dir=filen, rped_name='orangecontrib', gogal_name='Alkemiet')

    # filen = os.path.join(os.getcwd(), 'widgets')
    # gp = GetAllPyFiles(fn_dir=filen, rped_name='Alkemiet.vasp.widgets', gogal_name='Alkemiet.widgets.vasp')

    # gp.ex_all_nopython_path(pri=False, mv_olddir_to_new_dir=True)
    # filen = os.path.join(os.getcwd(), 'Orange')
    # gp = GetAllPyFiles(fn_dir=filen, rped_name='Orange', gogal_name='Alkemieth')

    # filen = os.path.join(os.getcwd(), 'canvas')
    # gp = GetAllPyFiles(fn_dir=filen, rped_name='canvas', gogal_name='akwmw')
    # filen = os.path.join(os.getcwd(), 'Alkemieth')
    # gp = GetAllPyFiles(fn_dir=filen, rped_name='canvas', gogal_name='akwmw')
    filen = os.getcwd()
    gp = GetAllPyFiles(fn_dir=filen, rped_name='_static', gogal_name='static')


    # filen = os.path.join(os.getcwd(), 'Alkemieth')
    # gp = GetAllPyFiles(fn_dir=filen, rped_name='Alkemieth3', gogal_name='Alkemieth')

    gp.auto_run(nopy=False, valid=True, picture=True, mv_olddir_to_new_dir=False)
    gp = GetAllPyFiles(fn_dir=filen, rped_name='_images', gogal_name='images')
    gp.auto_run(nopy=False, valid=True, picture=True, mv_olddir_to_new_dir=False)
    # fn = r'G:/alkemie-dev/Orange/tree.py'
    # replace_one_file(fn, log=log_test())