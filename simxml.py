import xml.etree.ElementTree as ET
import gzip
from datetime import datetime
import platform
import uuid
import os
import numpy as np
import xml.dom.minidom
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimXML:
    def __init__(self, CI):
        self.__ID = None
        self.__xml = {}
        self.__setup_namespaces()
        self.__setup_directories()
        self.__tex = {
            'dir': '/Users/jiang/Work Space/Project Confidence Region/notes/tex',
            'CR_data': 'CR_data.tex',
        }
        self.__verbose = True
        self.__CI = CI

    def __setup_namespaces(self):
        self.__xml['ns'] = {
            '':   'http://www.uchicago.edu/cROC/sim',
            'i':  'http://www.uchicago.edu/cROC/sim/info',
            'g':  'http://www.uchicago.edu/cROC/sim/glossary',
            's':  'http://www.uchicago.edu/cROC/sim/summary/statistics',
            'sp': 'http://www.uchicago.edu/cROC/sim/summary/statistics/population',
            'se': 'http://www.uchicago.edu/cROC/sim/summary/statistics/empirical',
            'p':  'http://www.uchicago.edu/cROC/sim/plot',
            'd':  'http://www.uchicago.edu/cROC/sim/data',
            'dp': 'http://www.uchicago.edu/cROC/sim/data/population',
            'dt': 'http://www.uchicago.edu/cROC/sim/data/trial',
            'dc': 'http://www.uchicago.edu/cROC/sim/data/contour',
        }
        for k, v in self.__xml['ns'].items():
            ET.register_namespace(k, v)
        ET.register_namespace('', 'http://www.uchicago.edu/cROC/sim')

    def __setup_directories(self):
        hostname = platform.node()
        if hostname == 'Yuleis-MacBook-Pro-3.local':
            self.__xml['dir'] = '/Users/jiang/Downloads/ThinLinc'
        elif hostname == 'midway3-0101.rcc.local':
            self.__xml['dir'] = '/home/yjiang/thindrives/ThinLinc'
        else:
            self.__xml['dir'] = './'

    def __load_xml(self, file=''):
        """
        Open xml file and return the XML root.

        Parameters
        ----------
        file : str, optional
            xml file name. The default is ''.

        Raises
        ------
        Exception
            If file cannot be read.

        Returns
        -------
        The xml main branch elements.
        """
        if file:
            try:
                logger.info(f'Opening {file}')
                try:
                    self.__xml['root'] = ET.parse(gzip.open(file, 'r')).getroot()
                except:
                    self.__xml['root'] = ET.parse(open(file, 'r')).getroot()
                logger.info(f'Read {file}')
            except Exception as e:
                logger.error(f'Fail to open database file: {file}')
                raise e
        else:
            logger.error('Please specify file to read')
            raise Exception('No file specified')
        return self.__xml

    def __write_xml(self, file, gz=True):
        self.__update_saved_time()
        if file:
            try:
                if gz:
                    with gzip.open(f"{file}.gz", 'wb') as f:
                        ET.ElementTree(self.__xml['root']).write(f, encoding="us-ascii", xml_declaration=True, method="xml")
                else:
                    with open(file, 'w') as f:
                        ET.ElementTree(self.__xml['root']).write(f, encoding="us-ascii", xml_declaration=True, method="xml")
                self.__xml['last'] = 0
                if self.__verbose:
                    logger.info(f"Write XML file: {file}")
            except Exception as e:
                logger.error(f"Fail to write XML file: {file}")
                raise e
        else:
            logger.error('No xml file name given to write')
            raise Exception('No file specified')

    def __update_saved_time(self):
        self.__xml['info'].findall('.//i:saved', self.__xml['ns'])[0].text = f"{datetime.now()}"

    def __new_xml(self):
        self.__ID = None
        self.__ID_gen()
        ns = f'{{{self.__xml["ns"][""]}}}'
        self.__xml['root'] = ET.Element("root")
        self.__xml['info'] = ET.SubElement(self.__xml['root'], f"{ns}Info")
        self.__xml['glos'] = ET.SubElement(self.__xml['root'], f"{ns}Glossary")
        self.__xml['summ'] = ET.SubElement(self.__xml['root'], f"{ns}DataSummary")
        self.__xml['plot'] = ET.SubElement(self.__xml['root'], f"{ns}DataForPlot")
        self.__xml['data'] = ET.SubElement(self.__xml['root'], f"{ns}Data")

    def __ID_gen(self):
        if self.__ID is None:
            self.__ID = uuid.uuid1()

    def __info_get(self, title_short, title_full, description):
        ns = f'{{{self.__xml["ns"]["i"]}}}'
        self.__xml['uuid'] = ET.SubElement(self.__xml['info'], f"{ns}ID")
        self.__xml['uuid'].set('type', 'uuid1')
        self.__xml['uuid'].text = f"{self.__ID}"
        ET.SubElement(self.__xml['info'], f"{ns}study_title_short").text = title_short
        ET.SubElement(self.__xml['info'], f"{ns}study_title_full").text = title_full
        ET.SubElement(self.__xml['info'], f"{ns}study_description").text = description
        ET.SubElement(self.__xml['info'], f"{ns}created").text = f"{datetime.now()}"
        ET.SubElement(self.__xml['info'], f"{ns}saved")
        try:
            ET.SubElement(self.__xml['info'], f"{ns}by").text = f"{os.getlogin()}"
        except:
            pass
        src = ET.SubElement(self.__xml['info'], f"{ns}with_src")
        src.text = f"{__file__}"
        ET.SubElement(src, f"{ns}src_date").text = f"{datetime.fromtimestamp(os.path.getmtime(__file__))}"
        ET.SubElement(src, f"{ns}src_dir").text = f"{os.path.dirname(__file__)}"
        ET.SubElement(self.__xml['info'], f"{ns}work_dir").text = f"{os.getcwd()}"
        host = ET.SubElement(self.__xml['info'], f"{ns}host")
        self.__add_host_info(host, ns)
        py = ET.SubElement(self.__xml['info'], f"{ns}python")
        self.__add_python_info(py, ns)

    def __add_host_info(self, host, ns):
        ET.SubElement(host, f"{ns}host_node").text = f"{platform.node()}"
        ET.SubElement(host, f"{ns}host_system").text = f"{platform.system()}"
        ET.SubElement(host, f"{ns}host_release").text = f"{platform.release()}"
        ET.SubElement(host, f"{ns}host_version").text = f"{platform.version()}"
        ET.SubElement(host, f"{ns}host_machine").text = f"{platform.machine()}"
        ET.SubElement(host, f"{ns}host_processor").text = f"{platform.processor()}"
        ET.SubElement(host, f"{ns}host_architecture").text = f"{platform.architecture()}"

    def __add_python_info(self, py, ns):
        ET.SubElement(py, f"{ns}python_version").text = f"{platform.python_version()}"
        ET.SubElement(py, f"{ns}python_build").text = f"{platform.python_build()}"
        ET.SubElement(py, f"{ns}python_compiler").text = f"{platform.python_compiler()}"
        ET.SubElement(py, f"{ns}python_branch").text = f"{platform.python_branch()}"
        ET.SubElement(py, f"{ns}python_revision").text = f"{platform.python_revision()}"
        ET.SubElement(py, f"{ns}python_implementation").text = f"{platform.python_implementation()}"

    def __glossary_entry(self, xpath, tag, shorttag, text):
        ns = f'{{{self.__xml["ns"]["g"]}}}'
        e = ET.SubElement(self.__xml['glos'].findall(f"g:{xpath}", self.__xml['ns'])[0], f"{ns}{shorttag}")
        e.set('tag', tag)
        e.text = text

    def __glossary_make(self):
        self.__glossary_make_root()
        self.__glossary_make_info()

    def __glossary_make_root(self):
        ns = f'{{{self.__xml["ns"]["g"]}}}'
        entries = [
            {'Info': 'Information of date, time, user, executable source file, directories, host computer, and python environment'},
            {'Glossary': 'Explanation of tags'},
            {'DataSummary': 'Summary results of the simulation results'},
            {'DataForPlot': 'Data for generating summary plots of the simulation results'},
            {'Data': 'Simulation raw data'},
        ]
        for entry in entries:
            for k, v in entry.items():
                e = ET.SubElement(self.__xml['glos'], f"{ns}{k}")
                e.set('tag', k)
                e.text = v

    def __glossary_make_info(self):
        entries = [
            {'ID': 'Unique file ID, and also serves as the file name'},
            {'study_title_short': 'Short study title for identification purpose'},
            {'study_title_full': 'Full descriptive study title'},
            {'study_description': 'Additional description of the study'},
            {'created': 'Date and time data in this file began to be created'},
            {'saved': 'Date and time data in this file were saved'},
            {'by': 'The login user name who created this file'},
            {'with_src': 'The executable source file that was used to create data in this file'},
            {'src_date': 'Date and time of the executable source file that created data in this file'},
            {'src_dir': 'Directory of the executable source file that created data in this file'},
            {'work_dir': 'Directory in which the executable source file was run to create data in this file'},
            {'host': 'Information of the host computer'},
            {'host_node': 'The host computer network name'},
            {'host_system': 'The host computer system/OS name'},
            {'host_release': 'The host computer system release'},
            {'host_version': 'The host computer system release version'},
            {'host_machine': 'The host computer machine type'},
            {'host_processor': 'The host computer (real) processor name'},
            {'host_architecture': 'The host computer executable (Python interpreter binary) architecture information'},
            {'python': 'Information of the Python interpreter'},
            {'python_version': 'Python version'},
            {'python_build': 'Python build number and date'},
            {'python_compiler': 'Python compiler used to create data in this file'},
            {'python_branch': 'Python implementation SCM branch'},
            {'python_revision': 'Python implementation SCM revision'},
            {'python_implementation': 'Python implementation'},
        ]
        for entry in entries:
            for k, v in entry.items():
                self.__glossary_entry('Info', f"i:{k}", 'i', v)

    def __glossary_make_data_sim_CI(self):
        ci_entries = [
            {'experiment': 'A standalone simulation experiment'},
            {'ID': 'Unique experiment ID'},
        ]
        dp_entries = [
            {'population': 'The assumed population values'},
            {'n': 'The total number of cases'},
            {'p': 'The binomial proportion of success'},
            {'p_var': 'The variance of the binomial proportion of success'},
            {'p_sd': 'The standard deviation of the binomial proportion of success'},
            {'trials': 'The total number of repeated independent experimental trials'},
            {'dx': 'The cell width for integration in p'},
            {'distribution': 'Probability distribution functions'},
            {'k': 'Number of successes'},
            {'x': 'Proportion of successes, i.e., k/n'},
            {'pm': 'Probability mass (density)'},
            {'cp': 'Cumulative probability'},
        ]
        dt_entries = [
            {'trial': 'An independent simulation experimental trial'},
            {'seq': 'The sequential trial number'},
            {'emp': 'The empirical number of successes'},
            {'mle': 'The maximum-likelihood estimate of p, the binomial proportion of success'},
            {'CI99L': 'The left bound of the estimated 99%CI'},
            {'CI99R': 'The right bound of the estimated 99%CI'},
            {'CI99i': '1 = the estimated 99%CI encloses the population value, p, 0 = otherwise'},
            {'CI95L': 'The left bound of the estimated 95%CI'},
            {'CI95R': 'The right bound of the estimated 95%CI'},
            {'CI95i': '1 = the estimated 95%CI encloses the population value, p, 0 = otherwise'},
            {'CI90L': 'The left bound of the estimated 90%CI'},
            {'CI90R': 'The right bound of the estimated 90%CI'},
            {'CI90i': '1 = the estimated 90%CI encloses the population value, p, 0 = otherwise'},
            {'CI80L': 'The left bound of the estimated 80%CI'},
            {'CI80R': 'The right bound of the estimated 80%CI'},
            {'CI80i': '1 = the estimated 80%CI encloses the population value, p, 0 = otherwise'},
        ]
        self.__add_glossary_entries(ci_entries, 'Data', 'd')
        self.__add_glossary_entries(dp_entries, 'Data', 'dp')
        self.__add_glossary_entries(dt_entries, 'Data', 'dt')

    def __add_glossary_entries(self, entries, xpath, ns):
        ns_full = f'{{{self.__xml["ns"][ns]}}}'
        for entry in entries:
            for k, v in entry.items():
                self.__glossary_entry(xpath, f"{ns}:{k}", ns, v)

    def __glossary_make_data_sim_CG(self):
        cg_entries = [
            {'experiment': 'A standalone simulation experiment'},
            {'ID': 'Unique experiment ID'},
        ]
        dp_entries = [
            {'population': 'The assumed population values'},
            {'n_neg': 'The total number of actually negative cases'},
            {'n_pos': 'The total number of actually positive cases'},
            {'FPF': 'The assumed population FPF value'},
            {'TPF': 'The assumed population TPF value'},
            {'FPF_var': 'The variance of the assumed population FPF value'},
            {'FPF_sd': 'The standard deviation of the assumed population FPF value'},
            {'TPF_var': 'The variance of the assumed population TPF value'},
            {'TPF_sd': 'The standard deviation of the assumed population TPF value'},
            {'trials': 'The total number of repeated independent experimental trials'},
            {'dx': 'The cell width for integration in FPF'},
            {'dy': 'The cell width for integration in TPF'},
            {'FP_distribution': 'FP probability distribution functions'},
            {'FP_k': 'Number of FP'},
            {'FP_x': 'FPF, i.e., FP_k/n_neg'},
            {'FP_pm': 'FPF probability mass (density)'},
            {'FP_cp': 'FPF cumulative probability'},
            {'TP_distribution': 'TP probability distribution functions'},
            {'TP_k': 'Number of TP'},
            {'TP_x': 'TPF, i.e., TP_k/n_pos'},
            {'TP_pm': 'TPF probability mass (density)'},
            {'TP_cp': 'TPF cumulative probability'},
        ]
        dt_entries = [
            {'trial': 'An independent simulation experimental trial'},
            {'seq': 'The sequential trial number'},
            {'emp_FP': 'The empirical number of FP'},
            {'emp_TP': 'The empirical number of TP'},
            {'mle_FPF': 'The maximum-likelihood estimate of FPF'},
            {'mle_TPF': 'The maximum-likelihood estimate of TPF'},
            {'CG99i': '1 = the estimated 99%CR encloses the population values (FPF, TPF), 0 = otherwise, -1 and -2 = errors'},
            {'CG99pts': '99%CR contour points (all points including the contour points are within the 99%CR)'},
            {'CG99pt': 'An individual point on the 99%CR contour, X = FPF, Y = TPF, P = binomial probability'},
            {'CIs99i': '1 = the estimated 99%CIs on FPF alone and on TPF alone (a rectangle) encloses the population values (FPF, TPF), 0 = otherwise'},
            {'FPF_CI99i': '1 = the estimated 99%CI on FPF alone encloses the population FPF value, 0 = otherwise'},
            {'FPF_CI99L': 'The left bound of the estimated 99%CI on FPF alone'},
            {'FPF_CI99R': 'The right bound of the estimated 99%CI on FPF alone'},
            {'TPF_CI99i': '1 = the estimated 99%CI on TPF alone encloses the population TPF value, 0 = otherwise'},
            {'TPF_CI99L': 'The left bound of the estimated 99%CI on TPF alone'},
            {'TPF_CI99R': 'The right bound of the estimated 99%CI on TPF alone'},
            {'CG95i': '1 = the estimated 95%CR encloses the population values (FPF, TPF), 0 = otherwise, -1 and -2 = errors'},
            {'CG95pts': '95%CR contour points (all points including the contour points are within the 95%CR)'},
            {'CG95pt': 'An individual point on the 95%CR contour, X = FPF, Y = TPF, P = binomial probability'},
            {'CIs95i': '1 = the estimated 95%CIs on FPF alone and on TPF alone (a rectangle) encloses the population values (FPF, TPF), 0 = otherwise'},
            {'FPF_CI95i': '1 = the estimated 95%CI on FPF alone encloses the population FPF value, 0 = otherwise'},
            {'FPF_CI95L': 'The left bound of the estimated 95%CI on FPF alone'},
            {'FPF_CI95R': 'The right bound of the estimated 95%CI on FPF alone'},
            {'TPF_CI95i': '1 = the estimated 95%CI on TPF alone encloses the population TPF value, 0 = otherwise'},
            {'TPF_CI95L': 'The left bound of the estimated 95%CI on TPF alone'},
            {'TPF_CI95R': 'The right bound of the estimated 95%CI on TPF alone'},
            {'CG90i': '1 = the estimated 90%CR encloses the population values (FPF, TPF), 0 = otherwise, -1 and -2 = errors'},
            {'CG90pts': '90%CR contour points (all points including the contour points are within the 90%CR)'},
            {'CG90pt': 'An individual point on the 90%CR contour, X = FPF, Y = TPF, P = binomial probability'},
            {'CIs90i': '1 = the estimated 90%CIs on FPF alone and on TPF alone (a rectangle) encloses the population values (FPF, TPF), 0 = otherwise'},
            {'FPF_CI90i': '1 = the estimated 90%CI on FPF alone encloses the population FPF value, 0 = otherwise'},
            {'FPF_CI90L': 'The left bound of the estimated 90%CI on FPF alone'},
            {'FPF_CI90R': 'The right bound of the estimated 90%CI on FPF alone'},
            {'TPF_CI90i': '1 = the estimated 90%CI on TPF alone encloses the population TPF value, 0 = otherwise'},
            {'TPF_CI90L': 'The left bound of the estimated 90%CI on TPF alone'},
            {'TPF_CI90R': 'The right bound of the estimated 90%CI on TPF alone'},
            {'CG80i': '1 = the estimated 80%CR encloses the population values (FPF, TPF), 0 = otherwise, -1 and -2 = errors'},
            {'CG80pts': '80%CR contour points (all points including the contour points are within the 80%CR)'},
            {'CG80pt': 'An individual point on the 80%CR contour, X = FPF, Y = TPF, P = binomial probability'},
            {'CIs80i': '1 = the estimated 80%CIs on FPF alone and on TPF alone (a rectangle) encloses the population values (FPF, TPF), 0 = otherwise'},
            {'FPF_CI80i': '1 = the estimated 80%CI on FPF alone encloses the population FPF value, 0 = otherwise'},
            {'FPF_CI80L': 'The left bound of the estimated 80%CI on FPF alone'},
            {'FPF_CI80R': 'The right bound of the estimated 80%CI on FPF alone'},
            {'TPF_CI80i': '1 = the estimated 80%CI on TPF alone encloses the population TPF value, 0 = otherwise'},
            {'TPF_CI80L': 'The left bound of the estimated 80%CI on TPF alone'},
            {'TPF_CI80R': 'The right bound of the estimated 80%CI on TPF alone'},
        ]
        self.__add_glossary_entries(cg_entries, 'Data', 'd')
        self.__add_glossary_entries(dp_entries, 'Data', 'dp')
        self.__add_glossary_entries(dt_entries, 'Data', 'dt')

    def __experiment_make(self):
        ns = f'{{{self.__xml["ns"]["d"]}}}'
        self.__xml['expt'] = ET.SubElement(self.__xml['data'], f"{ns}experiment")
        exp_id = ET.SubElement(self.__xml['expt'], f"{ns}ID")
        exp_id.set('type', 'uuid1')
        exp_id.text = f"{uuid.uuid1()}"

    def __experiment_population_make(self, data):
        ns = f'{{{self.__xml["ns"]["dp"]}}}'
        population = ET.SubElement(self.__xml['expt'], f"{ns}population")
        for k, v in data.items():
            if isinstance(v, str):
                ET.SubElement(population, f"{ns}{k}").text = v
            elif isinstance(v, list):
                for item in v:
                    elem = ET.SubElement(population, f"{ns}{k}")
                    if isinstance(item, dict):
                        for sub_k, sub_v in item.items():
                            ET.SubElement(elem, f"{ns}{sub_k}").text = sub_v

    def __experiment_trial_entry(self, time0='', data={}):
        ns = f'{{{self.__xml["ns"]["dt"]}}}'
        trial = ET.SubElement(self.__xml['expt'], f"{ns}trial")
        for k, v in data.items():
            if not isinstance(v, list):
                ET.SubElement(trial, f"{ns}{k}").text = v
            else:
                self.__experiment_trial_entry_list(trial, ns, k, v)
        if time0:
            trial.set('t0', time0)
        trial.set('t', f"{datetime.now()}")

    def __experiment_trial_entry_list(self, elm, ns, k, v):
        entry = ET.SubElement(elm, f"{ns}{k}")
        for item in v:
            for sub_k, sub_v in item.items():
                if not isinstance(sub_v, dict):
                    ET.SubElement(entry, f"{ns}{sub_k}").text = sub_v
                else:
                    sub_elem = ET.SubElement(entry, f"{ns}{sub_k}")
                    for attr_k, attr_v in sub_v.items():
                        sub_elem.set(attr_k, attr_v)

    def new(self, title_short='', title_full='', description=''):
        self.__new_xml()
        self.__info_get(title_short, title_full, description)
        self.__glossary_make()

    def glossary_make_data(self, exp=''):
        if exp == 'binomial CI':
            self.__glossary_make_data_sim_CI()
        elif exp == 'binomial CR':
            self.__glossary_make_data_sim_CG()

    def exp_init(self, data):
        self.__experiment_make()
        self.__experiment_population_make(data)

    def exp_trial(self, time0='', data={}):
        self.__experiment_trial_entry(time0, data)

    def summarize(self, file='', xml=True, sim=''):
        if sim == 'CI':
            self.__summarize_CI(file, xml)
        if sim == 'CG':
            self.__summarize_CG(file, xml)

    def write(self):
        self.__write_xml(file=os.path.join(self.__xml['dir'], f"{self.__ID}.xml"))

