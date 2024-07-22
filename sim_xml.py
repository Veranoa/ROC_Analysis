#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import gzip
from datetime import datetime
import platform
import uuid
import os
import numpy as np
import xml.dom.minidom


class sim_xml():
    def __init__(self, CI):
        self.__ID = None
        self.__xml = {}
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
            ET.register_namespace(f"{k}", f"{v}")
        ET.register_namespace('', 'http://www.uchicago.edu/cROC/sim')
        if platform.node() == 'Yuleis-MacBook-Pro-3.local':
            self.__xml['dir'] = '/Users/jiang/Downloads/ThinLinc'
        elif platform.node() == 'midway3-0101.rcc.local':
            self.__xml['dir'] = '/home/yjiang/thindrives/ThinLinc'
            self.__xml['dir'] = './' 
        else:
            self.__xml['dir'] = './' 
        self.__tex = {
            'dir': '/Users/jiang/Work Space/Project Confidence Region/notes/tex',
            'CR_data': 'CR_data.tex',
            }
        self.__verbose = True
        self.__CI = CI
        return
    
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
                print('  .. Opening {0}'.format(file))
                try:
                    self.__xml['root'] = ET.parse(gzip.open(file, 'r')).getroot()
                except:
                    self.__xml['root'] = ET.parse(open(file, 'r')).getroot()
                print('  .. Read {0}'.format(file))
            except:
                print(' .. Fail to open database file: {0}'.format(file))
                raise Exception
        else:
            print('Please specify file to read')
            raise Exception
        return self.__xml
    
    def __load_xml0(self, file=''):
        if file:
            try:
                self.__root = ET.parse(file).getroot()
                print(f"  .. Read XML file: {file}")
            except:
                raise f"Error: fail to read XML file: {file}"
        else:
            raise 'Error: no xml file name given to read'
        return
    
    def __write_xml(self, file, gz=True):
        self.__xml['info'].findall('.//i:saved', self.__xml['ns'])[0].text = f"{datetime.now()}"
        if file:
            try:
                if gz:
                    __f = gzip.open(f"{file}.gz", 'wb')
                else:
                    __f = file
                ET.ElementTree(self.__xml['root']).write(
                    __f, encoding="us-ascii", xml_declaration=True, method="xml")
                self.__xml['last'] = 0
                if self.__verbose:
                    print(f"  .. Write XML file: {file}")
            except:
                raise f"Error: fail to write XML file: {file}"
        else:
            raise 'Error: no xml file name given to write'
        return
    
    def __read_xml(self, ):
        for k in self.__xml['root'].attrib.keys():
            self.__xml['ns'][k] = self.__xml['root'].attrib[k]
        self.__xml['info'] = self.__xml['root'].findall('Info', self.__xml['ns'])[0]
        self.__xml['glos'] = self.__xml['root'].findall('Glossary', self.__xml['ns'])[0]
        self.__xml['summ'] = self.__xml['root'].findall('DataSummary', self.__xml['ns'])[0]
        self.__xml['plot'] = self.__xml['root'].findall('DataForPlot', self.__xml['ns'])[0]
        self.__xml['data'] = self.__xml['root'].findall('Data', self.__xml['ns'])[0]
        self.__xml['uuid'] = self.__xml['info'].findall('i:ID', self.__xml['ns'])[0].text
        return
    
    def __new_xml(self, ):
        self.__ID = None
        self.__ID_gen()
        __ns = '{' + f"{self.__xml['ns']['']}" + '}'
        self.__xml['root'] = ET.Element("root")
        self.__xml['info'] = ET.SubElement(self.__xml['root'], f"{__ns}Info")
        self.__xml['glos'] = ET.SubElement(self.__xml['root'], f"{__ns}Glossary")
        # ET.register_namespace('', f"{self.__xml['ns']['g']}")
        self.__xml['summ'] = ET.SubElement(self.__xml['root'], f"{__ns}DataSummary")
        self.__xml['plot'] = ET.SubElement(self.__xml['root'], f"{__ns}DataForPlot")
        self.__xml['data'] = ET.SubElement(self.__xml['root'], f"{__ns}Data")
        return
    
    def __ID_gen(self, ):
        if  self.__ID is None:
            self.__ID = uuid.uuid1()
        return
    
    def __info_get(self, title_short, title_full, description):
        __ns = '{' + f"{self.__xml['ns']['i']}" + '}'
        self.__xml['uuid'] = ET.SubElement(self.__xml['info'], f"{__ns}ID")
        self.__xml['uuid'].set('type', 'uuid1')
        self.__xml['uuid'].text = f"{self.__ID}"
        ET.SubElement(self.__xml['info'], f"{__ns}study_title_short").text = title_short
        ET.SubElement(self.__xml['info'], f"{__ns}study_title_full").text = title_full
        ET.SubElement(self.__xml['info'], f"{__ns}study_description").text = description
        ET.SubElement(self.__xml['info'], f"{__ns}created").text = f"{datetime.now()}"
        ET.SubElement(self.__xml['info'], f"{__ns}saved")
        try:
            ET.SubElement(self.__xml['info'], f"{__ns}by").text = f"{os.getlogin()}"
        except:
            pass
        __src = ET.SubElement(self.__xml['info'], f"{__ns}with_src")
        __src.text = f"{__file__}"
        ET.SubElement(__src, f"{__ns}src_date").text = f"{datetime.fromtimestamp(os.path.getmtime(__file__))}"
        ET.SubElement(__src, f"{__ns}src_dir").text = f"{os.path.dirname(__file__)}"
        ET.SubElement(self.__xml['info'], f"{__ns}work_dir").text = f"{os.getcwd()}"
        __host = ET.SubElement(self.__xml['info'], f"{__ns}host")
        ET.SubElement(__host, f"{__ns}host_node").text = f"{platform.node()}"
        ET.SubElement(__host, f"{__ns}host_system").text = f"{platform.system()}"
        ET.SubElement(__host, f"{__ns}host_release").text = f"{platform.release()}"
        ET.SubElement(__host, f"{__ns}host_version").text = f"{platform.version()}"
        ET.SubElement(__host, f"{__ns}host_machine").text = f"{platform.machine()}"
        ET.SubElement(__host, f"{__ns}host_processor").text = f"{platform.processor()}"
        ET.SubElement(__host, f"{__ns}host_architecture").text = f"{platform.architecture()}"
        __py = ET.SubElement(self.__xml['info'], f"{__ns}python")
        ET.SubElement(__py, f"{__ns}python_version").text = f"{platform.python_version()}"
        ET.SubElement(__py, f"{__ns}python_build").text = f"{platform.python_build()}"
        ET.SubElement(__py, f"{__ns}python_compiler").text = f"{platform.python_compiler()}"
        ET.SubElement(__py, f"{__ns}python_branch").text = f"{platform.python_branch()}"
        ET.SubElement(__py, f"{__ns}python_revision").text = f"{platform.python_revision()}"
        ET.SubElement(__py, f"{__ns}python_implementation").text = f"{platform.python_implementation()}"
        return
    
    def __glossary_entry(self, xpath, tag, shorttag, text):
        __ns = '{' + f"{self.__xml['ns']['g']}" + '}'
        __e = ET.SubElement(self.__xml['glos'].findall(f"g:{xpath}", self.__xml['ns'])[0], 
                      f"{__ns}{shorttag}")
        __e.set('tag', tag)
        __e.text = text
        return
    
    def __glossary_make(self, ):
        self.__glossary_make_root()
        self.__glossary_make_info()
        return
    
    def __glossary_make_root(self, ):
        __ns = '{' + f"{self.__xml['ns']['g']}" + '}'
        for i in [
            {'Info':        'Information of date, time, user, executable source file, ' +
                            'directories, host computer, and python environment'},
            {'Glossary':    'Explanation of tags'},
            {'DataSummary': 'Summary results of the simulation results'},
            {'DataForPlot': 'Data for generating summary plots of the simulation results'},
            {'Data':        'Simulation raw data'},
            ]:
            for k, v in i.items():
                __e = ET.SubElement(self.__xml['glos'], f"{__ns}{k}")
                __e.set('tag', f"{k}")
                __e.text  = f"{v}"
        return
    
    def __glossary_make_info(self, ):
        for i in [
            {'ID':                'Unique file ID, and also serves as the file name'},
            {'study_title_short': 'Short study title for identification purpose'},
            {'study_title_full':  'Full descriptive study title'},
            {'study_description': 'Additional description of the study'},
            {'created':           'Date and time data in this file began to be created'},
            {'saved':             'Date and time data in this file were saved'},
            {'by':                'The login user name who created this file'},
            {'with_src':          'The executable source file that was used ' +
                                  'to create data in this file'},
            {'src_date':          'Date and time of the executable source file ' +
                                  'that created data in this file'},
            {'src_dir':           'Directory of the executable source file that ' +
                                  'created data in this file'},
            {'work_dir':          'Directory in which the executable source file ' +
                                  'was run to create data in this file'},
            {'host':              'Information of the host computer'},
            {'host_node':         'The host computer network name'},
            {'host_system':       'The host computer system/OS name'},
            {'host_release':      'The host computer system release'},
            {'host_version':      'The host computer system release version'},
            {'host_machine':      'The host computer machine type'},
            {'host_processor':    'The host computer (real) processor name'},
            {'host_architecture': 'The host computer executable (Python interpreter ' +
                                  'binary) architecture information'},
            {'python':            'Information of the Python interpreter'},
            {'python_version':    'Python version'},
            {'python_build':      'Python build number and date'},
            {'python_compiler':   'Python compiler used to create data ' +
                                  'in this file'},
            {'python_branch':     'Python implementation SCM branch'},
            {'python_revision':   'Python implementation SCM revision'},
            {'python_implementation': 'Python implementation'},
                ]:
            for k, v in i.items():
                self.__glossary_entry('Info', f"i:{k}", 'i', f"{v}")
        return
    
    def __glossary_make_data_sim_CI(self, ):
        for i in [
            {'experiment':        'A standalone simulation experiment'},
            {'ID':                'Unique experiment ID'},
                ]:
            for k, v in i.items():
                self.__glossary_entry('Data', f"d:{k}", 'd', f"{v}")
        for i in [
            {'population':        'The assumed population values'},
            {'n':                 'The total number of cases'},
            {'p':                 'The binomial proportion of success'},
            {'p_var':             'The variance of the binomial proportion of success'},
            {'p_sd':              'The standard deviation of the binomial proportion of success'},
            {'trials':            'The total number of repeated independent experimental trials'},
            {'dx':                'The cell width for integration in p'},
            {'distribution':      'Probability distribution functions'},
            {'k':                 'Number of successes'},
            {'x':                 'Proportion of successes, i.e., k/n'},
            {'pm':                'Probability mass (density)'},
            {'cp':                'Cumulative probability'},
                ]:
            for k, v in i.items():
                self.__glossary_entry('Data', f"dp:{k}", 'dp', f"{v}")
        for i in [
            {'trial':             'An independent simulation experimental trial'},
            {'seq':               'The sequential trial number'},
            {'emp':               'The empirical number of successes'},
            {'mle':               'The maximum-likelihood estimate of p, ' +
                                  'the binomial proportion of success'},
            {'CI99L':             'The left bound of the estimated 99%CI'},
            {'CI99R':             'The right bound of the estimated 99%CI'},
            {'CI99i':             '1 = the estimated 99%CI encloses the population ' +
                                  'value, p, 0 = otherwise'},
            {'CI95L':             'The left bound of the estimated 95%CI'},
            {'CI95R':             'The right bound of the estimated 95%CI'},
            {'CI95i':             '1 = the estimated 95%CI encloses the population ' +
                                  'value, p, 0 = otherwise'},
            {'CI90L':             'The left bound of the estimated 90%CI'},
            {'CI90R':             'The right bound of the estimated 90%CI'},
            {'CI90i':             '1 = the estimated 90%CI encloses the population ' +
                                  'value, p, 0 = otherwise'},
            {'CI80L':             'The left bound of the estimated 80%CI'},
            {'CI80R':             'The right bound of the estimated 80%CI'},
            {'CI80i':             '1 = the estimated 80%CI encloses the population ' +
                                  'value, p, 0 = otherwise'},
                ]:
            for k, v in i.items():
                self.__glossary_entry('Data', f"dt:{k}", 'dt', f"{v}")
        return
    
    def __glossary_make_data_sim_CG(self, ):
        for i in [
            {'experiment':        'A standalone simulation experiment'},
            {'ID':                'Unique experiment ID'},
                ]:
            for k, v in i.items():
                self.__glossary_entry('Data', f"d:{k}", 'd', f"{v}")
        for i in [
            {'population':        'The assumed population values'},
            {'n_neg':             'The total number of actually negative cases'},
            {'n_pos':             'The total number of actually positive cases'},
            {'FPF':               'The assumed population FPF value'},
            {'TPF':               'The assumed population TPF value'},
            {'FPF_var':           'The variance of the assumed population FPF value'},
            {'FPF_sd':            'The standard deviation of the assumed population FPF value'},
            {'TPF_var':           'The variance of the assumed population TPF value'},
            {'TPF_sd':            'The standard deviation of the assumed population TPF value'},
            {'trials':            'The total number of repeated independent experimental trials'},
            {'dx':                'The cell width for integration in FPF'},
            {'dy':                'The cell width for integration in TPF'},
            {'FP_distribution':   'FP probability distribution functions'},
            {'FP_k':              'Number of FP'},
            {'FP_x':              'FPF, i.e., FP_k/n_neg'},
            {'FP_pm':             'FPF probability mass (density)'},
            {'FP_cp':             'FPF cumulative probability'},
            {'TP_distribution':   'TP probability distribution functions'},
            {'TP_k':              'Number of TP'},
            {'TP_x':              'TPF, i.e., TP_k/n_pos'},
            {'TP_pm':             'TPF probability mass (density)'},
            {'TP_cp':             'TPF cumulative probability'},
                ]:
            for k, v in i.items():
                self.__glossary_entry('Data', f"dp:{k}", 'dp', f"{v}")
        for i in [
            {'trial':             'An independent simulation experimental trial'},
            {'seq':               'The sequential trial number'},
            {'emp_FP':            'The empirical number of FP'},
            {'emp_TP':            'The empirical number of TP'},
            {'mle_FPF':           'The maximum-likelihood estimate of FPF'},
            {'mle_TPF':           'The maximum-likelihood estimate of TPF'},
            {'CG99i':             '1 = the estimated 99%CR encloses the population ' +
                                  'values (FPF, TPF), 0 = otherwise, ' +
                                  '-1 and -2 = errors'},
            {'CG99pts':           '99%CR contour points (all points including ' +
                                  'the contour points are within the 99%CR)'},
            {'CG99pt':            'An individual point on the 99%CR contour, ' +
                                  'X = FPF, Y = TPF, P = binomial probability'},
            {'CIs99i':            '1 = the estimated 99%CIs on FPF alone and on ' +
                                  'TPF alone (a rectangle) encloses ' +
                                  'the population values (FPF, TPF), 0 = otherwise'},
            {'FPF_CI99i':         '1 = the estimated 99%CI on FPF alone encloses ' +
                                  'the population FPF value, 0 = otherwise'},
            {'FPF_CI99L':         'The left bound of the estimated 99%CI on FPF alone'},
            {'FPF_CI99R':         'The right bound of the estimated 99%CI on FPF alone'},
            {'TPF_CI99i':         '1 = the estimated 99%CI on TPF alone encloses ' +
                                  'the population TPF value, 0 = otherwise'},
            {'TPF_CI99L':         'The left bound of the estimated 99%CI on TPF alone'},
            {'TPF_CI99R':         'The right bound of the estimated 99%CI on TPF alone'},
            {'CG95i':             '1 = the estimated 95%CR encloses the population ' +
                                  'values (FPF, TPF), 0 = otherwise, ' +
                                  '-1 and -2 = errors'},
            {'CG95pts':           '95%CR contour points (all points including ' +
                                  'the contour points are within the 95%CR)'},
            {'CG95pt':            'An individual point on the 95%CR contour, ' +
                                  'X = FPF, Y = TPF, P = binomial probability'},
            {'CIs95i':            '1 = the estimated 95%CIs on FPF alone and on ' +
                                  'TPF alone (a rectangle) encloses ' +
                                  'the population values (FPF, TPF), 0 = otherwise'},
            {'FPF_CI95i':         '1 = the estimated 95%CI on FPF alone encloses ' +
                                  'the population FPF value, 0 = otherwise'},
            {'FPF_CI95L':         'The left bound of the estimated 95%CI on FPF alone'},
            {'FPF_CI95R':         'The right bound of the estimated 95%CI on FPF alone'},
            {'TPF_CI95i':         '1 = the estimated 95%CI on TPF alone encloses ' +
                                  'the population TPF value, 0 = otherwise'},
            {'TPF_CI95L':         'The left bound of the estimated 95%CI on TPF alone'},
            {'TPF_CI95R':         'The right bound of the estimated 95%CI on TPF alone'},
            {'CG90i':             '1 = the estimated 90%CR encloses the population ' +
                                  'values (FPF, TPF), 0 = otherwise, ' +
                                  '-1 and -2 = errors'},
            {'CG90pts':           '90%CR contour points (all points including ' +
                                  'the contour points are within the 90%CR)'},
            {'CG90pt':            'An individual point on the 90%CR contour, ' +
                                  'X = FPF, Y = TPF, P = binomial probability'},
            {'CIs90i':            '1 = the estimated 90%CIs on FPF alone and on ' +
                                  'TPF alone (a rectangle) encloses ' +
                                  'the population values (FPF, TPF), 0 = otherwise'},
            {'FPF_CI90i':         '1 = the estimated 90%CI on FPF alone encloses ' +
                                  'the population FPF value, 0 = otherwise'},
            {'FPF_CI90L':         'The left bound of the estimated 90%CI on FPF alone'},
            {'FPF_CI90R':         'The right bound of the estimated 90%CI on FPF alone'},
            {'TPF_CI90i':         '1 = the estimated 90%CI on TPF alone encloses ' +
                                  'the population TPF value, 0 = otherwise'},
            {'TPF_CI90L':         'The left bound of the estimated 90%CI on TPF alone'},
            {'TPF_CI90R':         'The right bound of the estimated 90%CI on TPF alone'},
            {'CG80i':             '1 = the estimated 80%CR encloses the population ' +
                                  'values (FPF, TPF), 0 = otherwise, ' +
                                  '-1 and -2 = errors'},
            {'CG80pts':           '80%CR contour points (all points including ' +
                                  'the contour points are within the 80%CR)'},
            {'CG80pt':            'An individual point on the 80%CR contour, ' +
                                  'X = FPF, Y = TPF, P = binomial probability'},
            {'CIs80i':            '1 = the estimated 80%CIs on FPF alone and on ' +
                                  'TPF alone (a rectangle) encloses ' +
                                  'the population values (FPF, TPF), 0 = otherwise'},
            {'FPF_CI80i':         '1 = the estimated 80%CI on FPF alone encloses ' +
                                  'the population FPF value, 0 = otherwise'},
            {'FPF_CI80L':         'The left bound of the estimated 80%CI on FPF alone'},
            {'FPF_CI80R':         'The right bound of the estimated 80%CI on FPF alone'},
            {'TPF_CI80i':         '1 = the estimated 80%CI on TPF alone encloses ' +
                                  'the population TPF value, 0 = otherwise'},
            {'TPF_CI80L':         'The left bound of the estimated 80%CI on TPF alone'},
            {'TPF_CI80R':         'The right bound of the estimated 80%CI on TPF alone'},
                ]:
            for k, v in i.items():
                self.__glossary_entry('Data', f"dt:{k}", 'dt', f"{v}")
        return
    
    def __experiment_make(self, ):
        __ns = '{' + f"{self.__xml['ns']['d']}" + '}'
        self.__xml['expt'] = ET.SubElement(self.__xml['data'], f"{__ns}experiment")
        __ID = ET.SubElement(self.__xml['expt'], f"{__ns}ID")
        __ID.set('type', 'uuid1')
        __ID.text = f"{uuid.uuid1()}"
        return
    
    def __experiment_population_make(self, data={}, ):
        __ns = '{' + f"{self.__xml['ns']['dp']}" + '}'
        __e = ET.SubElement(self.__xml['expt'], f"{__ns}population")
        for k, v in data.items():
            if   isinstance(v, str):
                ET.SubElement(__e, f"{__ns}{k}").text = f"{v}"
            elif isinstance(v, list):
                for x in v:
                    __el = ET.SubElement(__e, f"{__ns}{k}")
                    if isinstance(x, dict):
                        for l, u in x.items():
                            ET.SubElement(__el, f"{__ns}{l}").text = f"{u}"
        return 
    
    def __experiment_trial_entry(self, time0='', data={}, ):
        __ns = '{' + f"{self.__xml['ns']['dt']}" + '}'
        __e = ET.SubElement(self.__xml['expt'], f"{__ns}trial")
        for k, v in data.items():
            # a single value, e.g., CI
            if not isinstance(v, list):
                self.__experiment_trial_entry_text(__e, __ns, k, v)
            # a list of values, e.g., CG
            if isinstance(v, list):
                self.__experiment_trial_entry_list(__e, __ns, k, v)
        if time0:
            __e.set('t0', f"{time0}")
        __e.set('t', f"{datetime.now()}")
        return 
    
    def __experiment_trial_entry_text(self, elm, ns, k, v):
        ET.SubElement(elm, f"{ns}{k}").text = f"{v}"
        return

    def __experiment_trial_entry_list(self, elm, ns, k, v):
        __e = ET.SubElement(elm, f"{ns}{k}")
        for i in v: # v is a list
            for m, u in i.items():  # each member of v is a dict
                if not isinstance(u, dict): # not a dict of attribs
                    __ee = ET.SubElement(__e, f"{ns}{m}").text = f"{u}"
                else:   # a dict of attribs
                    __ee = ET.SubElement(__e, f"{ns}{m}")
                    for n, w in u.items():
                        __ee.set(f"{n}", f"{w}")
            # for m, u in i.items():  # each member of v is a dict
            #     if not m == 'attrib': # i[''] with a key not being 'attrib' contains the text
            #         __ee = ET.SubElement(__e, f"{ns}{m}").text = f"{u}"
            # for m, u in i.items():
            #     if m == 'attrib':     # i['attrib'] is a dict of attributes
            #         __ee = ET.SubElement(__e, f"{ns}{m}")
            #         for n, w in u.items():
            #             __ee.set(f"{n}", f"{w}")
        return

    def __data_CG_graph(self, trial=1, cg='95', show_CI=True):
        __exp = self.__xml['data'].findall('d:experiment', self.__xml['ns'])[0]
        __pop = __exp.findall('dp:population', self.__xml['ns'])[0]
        __n_neg = int(__pop.findall('dp:n_neg', self.__xml['ns'])[0].text)
        __n_pos = int(__pop.findall('dp:n_pos', self.__xml['ns'])[0].text)
        __elm = [x for x in 
                 __exp.findall('dt:trial', self.__xml['ns'])
                 if x.findall('dt:seq', self.__xml['ns'])[0].text == f"{trial}"][0]
        __dict = {'mle': '\\newcommand{\MLE}[0]{',
                  '99':  '\\newcommand{\CIninetynine}[0]{',
                  '95':  '\\newcommand{\CIninetyfive}[0]{',
                  '90':  '\\newcommand{\CIninety}[0]{',
                  '80':  '\\newcommand{\CIeighty}[0]{', 
                  }        
        __text = ''
        __text += f"{__dict['mle']}\n"
        __fp  = int(__elm.findall("dt:emp_FP", self.__xml['ns'])[0].text)
        __tp  = int(__elm.findall("dt:emp_TP", self.__xml['ns'])[0].text)
        __fpf = __elm.findall("dt:mle_FPF", self.__xml['ns'])[0].text
        __tpf = __elm.findall("dt:mle_TPF", self.__xml['ns'])[0].text
        __text += f"  ({__fpf},{__tpf})\n"
        __text += '}\n\n'
        __fpf_CI = self.__CI.cal(__fp, __n_neg, alpha=[.01, .05, .1, .2], dx=.0001, verbose=False)
        __tpf_CI = self.__CI.cal(__tp, __n_pos, alpha=[.01, .05, .1, .2], dx=.0001, verbose=False)
        print(__n_neg, __fp,__n_pos, __tp,)
        print(__fpf_CI)
        print(__tpf_CI)
        for k in ['99', '95', '90', '80']:
            __a = .01 * (100. - float(k))
            __text += f"{__dict[k]}\n"
            __text += f"  ({__fpf_CI['CI'][__a]['L']:.3f},{__tpf_CI['CI'][__a]['L']:.3f})\n"
            __text += f"  ({__fpf_CI['CI'][__a]['R']:.3f},{__tpf_CI['CI'][__a]['L']:.3f})\n"
            __text += f"  ({__fpf_CI['CI'][__a]['R']:.3f},{__tpf_CI['CI'][__a]['R']:.3f})\n"
            __text += f"  ({__fpf_CI['CI'][__a]['L']:.3f},{__tpf_CI['CI'][__a]['R']:.3f})\n"
            __text += f"  ({__fpf_CI['CI'][__a]['L']:.3f},{__tpf_CI['CI'][__a]['L']:.3f})\n"
            __text += '}\n\n'
        
        __dict = {'mle': '\\newcommand{\MLE}[0]{',
                  '99':  '\\newcommand{\CRninetynine}[0]{',
                  '95':  '\\newcommand{\CRninetyfive}[0]{',
                  '90':  '\\newcommand{\CRninety}[0]{',
                  '80':  '\\newcommand{\CReighty}[0]{', 
                  }        
        for k in ['99', '95', '90', '80']:
            __text += f"{__dict[k]}\n"
            __el = __elm.findall(f"dt:CG{k}pts", self.__xml['ns'])[0]
            __pt = []
            for __e in __el.findall(f"dt:CG{k}pt", self.__xml['ns']):
                __xl = __e.attrib[f"CG{k}XL"]
                __yl = __e.attrib[f"CG{k}YL"]
                __pt.append({'x': float(__xl), 'y': float(__yl)})
            __ys = list(set([x['y'] for x in __pt]))
            for __y in sorted(__ys):
                __x = np.min([x['x'] for x in __pt if x['y'] == __y])
                __text += f"  ({__x},{__y})\n"
            for __y in sorted(__ys, reverse=True):
                __x = np.max([x['x'] for x in __pt if x['y'] == __y])
                __text += f"  ({__x},{__y})\n"
            __y = np.min(__ys)
            __x = np.min([x['x'] for x in __pt if x['y'] == __y])
            __text += f"  ({__x},{__y})\n"
            __text += '}\n\n'
        __f = open(os.path.join(self.__tex['dir'],
                                self.__tex['CR_data']), 'w')
        print(__text, file=__f)
        __f.close()
        return
    
    def __sum_show_info(self, ):
        print('\n  .. Information of the simulation datafile:')
        print(xml.dom.minidom.parseString(
            ET.tostring(self.__xml['info'])).toprettyxml(), end='')
        print('  .. The simulation experiment:')
        __exp = self.__xml['data'].findall('d:experiment', self.__xml['ns'])[0]
        __ID  = __exp.findall('d:ID', self.__xml['ns'])[0]
        print(xml.dom.minidom.parseString(
            ET.tostring(__ID)).toprettyxml(), end='')
        print('  .. The simulation population:')
        __pop = __exp.findall('dp:population', self.__xml['ns'])[0]
        print(xml.dom.minidom.parseString(
            ET.tostring(__pop)).toprettyxml().split('<dp:FP_distribution>')[0], end='')
        print()
        return
    
    def __sum_CI_coverage(self, ):
        __exp = self.__xml['data'].findall('d:experiment', self.__xml['ns'])[0]
        __covg = {}
        __covg['all'] = len(__exp.findall('dt:trial', self.__xml['ns']))
        for k in ['99', '95', '90', '80']:
            __covg[f"i{k}"] = len([1 for x in 
                     __exp.findall('dt:trial', self.__xml['ns'])
                     if x.findall(f"dt:CI{k}i", self.__xml['ns'])[0].text == '1'])
            __text  = f"CI{k}: "
            __n = __covg[f"i{k}"]
            __text += f"coverage {100. * __n/__covg['all']:.2f} = "
            __text += f"{__n} / "
            __text += f"{__covg['all']}"
            print(__text)
        return

    def __sum_CG_coverage(self, ):
        __exp = self.__xml['data'].findall('d:experiment', self.__xml['ns'])[0]
        __covg = {}
        __covg['all'] = len(__exp.findall('dt:trial', self.__xml['ns']))
        __covg['CI95'] = {}
        for __x in ['CG', 'CIs', 'FPF_CI', 'TPF_CI']:
            for k in ['99', '95', '90', '80']:
                __covg[f"i{k}"] = len([1 for x in 
                         __exp.findall('dt:trial', self.__xml['ns'])
                         if x.findall(f"dt:{__x}{k}i", self.__xml['ns'])[0].text == '1'])
                # __covg['all'] = len([1 for x in 
                #          __exp.findall('dt:trial', self.__xml['ns'])])
                __covg['CI95'][k] = self.__CI.cal(x=__covg[f"i{k}"], n=__covg['all'], 
                                alpha=[.05], dx=.0001, verbose=False)['CI'][.05]
                __text  = f"{__x}{k}: "
                __n = __covg[f"i{k}"]
                __text += f"coverage {100. * __n/__covg['all']:.2f}% = "
                __text += f"{__n} / "
                __text += f"{__covg['all']}, "
                __l = __covg['CI95'][k]['L']
                __r = __covg['CI95'][k]['R']
                __text += f"95% CI: [{__l * 100:.1f}, {__r * 100:.1f}]%, "
                if (float(k) * .01 <= __r and float(k) * .01 >= __l):
                    __text += 'True: nominal value inside 95% CI'
                else:
                    __text += 'False: nominal value outside 95% CI'
                print(__text)
        return

    def __sum_CI_mle(self, ):
        __exp = self.__xml['data'].findall('d:experiment', self.__xml['ns'])[0]
        __mle = {}
        __mle['all'] = [float(x.text) for x in 
                        __exp.findall('dt:trial/dt:mle', self.__xml['ns'])]
        __mle['mean'] = np.mean(__mle['all'])
        __mle['var'] = np.var(__mle['all'])
        __mle['sd'] = np.std(__mle['all'])
        print(f"MLE: mean {__mle['mean']:.4f}, var {__mle['var']:.8f}, SD {__mle['sd']:.4f}")
        return

    def __sum_CG_mle(self, ):
        __exp = self.__xml['data'].findall('d:experiment', self.__xml['ns'])[0]
        __mle = {}
        __mle['FP_all'] = [float(x.text) for x in 
                        __exp.findall('dt:trial/dt:mle_FPF', self.__xml['ns'])]
        __mle['TP_all'] = [float(x.text) for x in 
                        __exp.findall('dt:trial/dt:mle_TPF', self.__xml['ns'])]
        __mle['FP_mean'] = np.mean(__mle['FP_all'])
        __mle['FP_var'] = np.var(__mle['FP_all'])
        __mle['FP_sd'] = np.std(__mle['FP_all'])
        __mle['TP_mean'] = np.mean(__mle['TP_all'])
        __mle['TP_var'] = np.var(__mle['TP_all'])
        __mle['TP_sd'] = np.std(__mle['TP_all'])
        __text  = f"MLE: FPF: mean {__mle['FP_mean']:.4f}, "
        __text += f"var {__mle['FP_var']:.8f}, "
        __text += f"SD {__mle['FP_sd']:.4f}; "
        __text += f"TPF: mean {__mle['TP_mean']:.4f}, "
        __text += f"var {__mle['TP_var']:.8f}, "
        __text += f"SD {__mle['TP_sd']:.4f}"
        print(__text)
        return

    def __summarize_CI(self, file='', xml=True):
        self.__load_xml(os.path.join(self.__xml['dir'], file))
        self.__read_xml()
        self.__sum_show_info()
        self.__sum_CI_mle()
        self.__sum_CI_coverage()
        return
    
    def __summarize_CG(self, file='', xml=True):
        self.__load_xml(os.path.join(self.__xml['dir'], file))
        self.__read_xml()
        self.__sum_show_info()
        self.__sum_CG_mle()
        self.__sum_CG_coverage()
        # self.__data_CG_graph()
        return
    
    def __summarize(self, file='', xml=True, sim=''):
        if sim == 'CI':
            self.__summarize_CI(file=file, xml=xml)
        if sim == 'CG':
            self.__summarize_CG(file=file, xml=xml)
        return
    
    def new(self, title_short='', title_full='', description=''):
        self.__new_xml()
        self.__info_get(title_short, title_full, description)
        self.__glossary_make()
        return
    
    def glossary_make_data(self, exp=''):
        if exp == 'binomial CI':
            self.__glossary_make_data_sim_CI()
        elif exp == 'binomial CR':
            self.__glossary_make_data_sim_CG()
        return
    
    def exp_init(self, data={}, ):
        self.__experiment_make()
        self.__experiment_population_make(data=data, )
        return 
    
    def exp_trial(self, time0='', data={}, ):
        self.__experiment_trial_entry(time0=time0, data=data, )
        return
    
    def summarize(self, file='', xml=True, sim=''):
        self.__summarize(file=file, xml=xml, sim=sim)
        return
    
    def write(self, ):
        self.__write_xml(file=os.path.join(self.__xml['dir'], f"{self.__ID}.xml"))
        return

