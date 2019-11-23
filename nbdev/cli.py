#AUTOGENERATED! DO NOT EDIT! File to edit: dev/05_cli.ipynb (unless otherwise specified).

__all__ = ['nbdev_build_lib', 'nbdev_update_lib', 'nbdev_diff_nbs', 'num_cpus', 'ProcessPoolExecutor', 'parallel',
           'nbdev_test_nbs', 'make_sidebar', 'convert_one', 'convert_all', 'nbdev_build_docs']

#Cell
from .imports import *
from .export import *
from .sync import *
from .export2html import *
from .test import *
from fastscript.fastscript import call_parse, Param

#Cell
@call_parse
def nbdev_build_lib(fname:Param("A notebook name or glob to convert", str)=None):
    notebook2script(fname=fname)

#Cell
@call_parse
def nbdev_update_lib(fname:Param("A notebook name or glob to convert", str)=None):
    script2notebook(fname=fname)

#Cell
@call_parse
def nbdev_diff_nbs(): diff_nb_script()

#Cell
from multiprocessing import Process, Queue
import concurrent

#Cell
def num_cpus():
    "Get number of cpus"
    try:                   return len(os.sched_getaffinity(0))
    except AttributeError: return os.cpu_count()

#Cell
class ProcessPoolExecutor(concurrent.futures.ProcessPoolExecutor):
    "Like `concurrent.futures.ProcessPoolExecutor` but handles 0 `max_workers`."
    def __init__(self, max_workers=None, on_exc=print, **kwargs):
        self.not_parallel = max_workers==0
        self.on_exc = on_exc
        if self.not_parallel: max_workers=1
        super().__init__(max_workers, **kwargs)

    def map(self, f, items, *args, **kwargs):
        g = partial(f, *args, **kwargs)
        if self.not_parallel: return map(g, items)
        try: return super().map(g, items)
        except Exception as e: self.on_exc(e)

#Cell
def parallel(f, items, *args, n_workers=None, **kwargs):
    "Applies `func` in parallel to `items`, using `n_workers`"
    if n_workers is None: n_workers = min(16, num_cpus())
    with ProcessPoolExecutor(n_workers) as ex:
        r = ex.map(f,items, *args, **kwargs)
        return list(r)

#Cell
def _test_one(fname, flags=None):
    time.sleep(random.random())
    print(f"testing: {fname}")
    try: test_nb(fname, flags=flags)
    except Exception as e: print(e)

#Cell
@call_parse
def nbdev_test_nbs(fname:Param("A notebook name or glob to convert", str)=None,
                   flags:Param("Space separated list of flags", str)=None):
    if flags is not None: flags = flags.split(' ')
    if fname is None:
        files = [f for f in Config().nbs_path.glob('*.ipynb') if not f.name.startswith('_')]
    else: files = glob.glob(fname)

    # make sure we are inside the notebook folder of the project
    os.chdir(Config().nbs_path)
    parallel(_test_one, files, flags=flags)

#Cell
import time,random,warnings

#Cell
def _leaf(k,v):
    url = 'external_url' if "http" in v else 'url'
    if url=='url': v=v+'.html'
    return {'title':k, url:v, 'output':'web,pdf'}

#Cell
_k_names = ['folders', 'folderitems', 'subfolders', 'subfolderitems']
def _side_dict(title, data, level=0):
    k_name = _k_names[level]
    level += 1
    res = [(_side_dict(k, v, level) if isinstance(v,dict) else _leaf(k,v))
        for k,v in data.items()]
    return ({k_name:res} if not title
            else res if title.startswith('empty')
            else {'title': title, 'output':'web', k_name: res})

#Cell
def make_sidebar():
    "Making sidebar for the doc website"
    if not (Config().doc_path/'sidebar.json').exists():
        warnings.warn("No data for the sidebar available")
        sidebar_d = {}
    else: sidebar_d = json.load(open(Config().doc_path/'sidebar.json', 'r'))
    res = _side_dict('Sidebar', sidebar_d)
    res = {'entries': [res]}
    res_s = yaml.dump(res, default_flow_style=False)
    res_s = res_s.replace('- subfolders:', '  subfolders:').replace(' - - ', '   - ')
    res_s = f"""
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# Instead edit {Config().doc_path/'sidebar.json'}
"""+res_s
    open(Config().doc_path/'_data/sidebars/home_sidebar.yml', 'w').write(res_s)

#Cell
def convert_one(fname):
    time.sleep(random.random())
    print(f"converting: {fname}")
    try: convert_nb(fname)
    except Exception as e: print(e)

#Cell
def convert_all(fname=None, force_all=False):
    "Convert all notebooks matching `fname` to html files"
    if fname is None:
        files = [f for f in Config().nbs_path.glob('*.ipynb') if not f.name.startswith('_')]
    else: files = glob.glob(fname)
    if not force_all:
        # only rebuild modified files
        files,_files = [],files.copy()
        for fname in _files:
            fname_out = Config().doc_path/'.'.join(fname.with_suffix('.html').name.split('_')[1:])
            if not fname_out.exists() or os.path.getmtime(fname) >= os.path.getmtime(fname_out):
                files.append(fname)
    if len(files)==0: print("No notebooks were modified")
    parallel(convert_one, files)

#Cell
@call_parse
def nbdev_build_docs(fname:Param("A notebook name or glob to convert", str)=None,
         force_all:Param("Rebuild even notebooks that haven't changed", bool)=False):
    convert_all(fname=fname, force_all=force_all)
    make_sidebar()