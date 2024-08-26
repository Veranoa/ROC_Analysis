#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  4 16:05:10 2024

@author: jiang
"""

from __future__ import print_function

import sys
sys.path.append('/Users/jiang/lib/python')
import os
import platform
from scipy.stats import binom
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
import uuid
from datetime import datetime
import gzip
import xml.dom.minidom
import argparse
import copy
import glob
import subprocess as SP

# confidence interval

class CG2():
    def __init__(self):
        self.__var = {
            'dx': .0001,
            'dy': .0001,
            }
        self.__df = pd.DataFrame()
        return

    def __reset(self, ):
        """
        Resets (empties) the private dataframe to start a new calculation 
        and to release the dataframe from memory.

        Parameters
        ----------
        None.

        Returns
        -------
        None.

        """
        self.__df.drop(list(self.__df.index.values), inplace=True)
        self.__df.drop(columns=list(self.__df.columns.values), inplace=True)
        return

    def __cal_binomial_MLE(self, x, n):
        """
        Calculates the maximum-likelihood estimate of the binomial probability.

        Parameters
        ----------
        x : int
            Number of "successes."
        n : int
            Number of "total trials."

        Returns
        -------
        float
            Maximum-likelihood estimate of binomial probability.

        """
        return float(x) / float(n)
    
    def __cal_binomial_distribution_2D(self, fp, n_n, tp, n_p):
        """
        Calculates in 2-dimensions the binomial probability cummulative distribution.
        The results are stored in a private dataframe.

        Parameters
        ----------
        fp : int
            The number of false positive cases.
        n_n : int
            The number of actually negative cases.
        tp : int
            The number of true positive cases.
        n_p : int
            The number of actually positive cases.

        Returns
        -------
        None.

        """
        # calculate 
        __cell = []
        __c_xl = []
        __c_xh = []
        __c_yl = []
        __c_yh = []
        __binom_sw = []
        __binom_nw = []
        __binom_se = []
        __binom_ne = []
        __binom_fpf = {}
        __binom_tpf = {}
        __x = 1. - self.__var['dx']
        __y = 1. - self.__var['dy']
        x = 0.
        __binom_fpf[f"{x:.6f}"] = binom.pmf(fp, n_n, x)
        while x <= __x:
            x += self.__var['dx']
            __binom_fpf[f"{x:.6f}"] = binom.pmf(fp, n_n, x)
        y = 0.
        __binom_tpf[f"{y:.6f}"] = binom.pmf(tp, n_p, y)
        while y <= __y:
            y += self.__var['dy']
            __binom_tpf[f"{y:.6f}"] = binom.pmf(tp, n_p, y)
        y = 0.
        while y <= __y:
            x = 0.
            while x <= __x:
                __c_xl.append(x)
                __c_xh.append(x + self.__var['dx'])
                __c_yl.append(y)
                __c_yh.append(y + self.__var['dy'])
                __binom_sw.append(__binom_fpf[f"{__c_xl[-1]:.6f}"] * __binom_tpf[f"{__c_yl[-1]:.6f}"])
                __binom_nw.append(__binom_fpf[f"{__c_xl[-1]:.6f}"] * __binom_tpf[f"{__c_yh[-1]:.6f}"])
                __binom_se.append(__binom_fpf[f"{__c_xh[-1]:.6f}"] * __binom_tpf[f"{__c_yl[-1]:.6f}"])
                __binom_ne.append(__binom_fpf[f"{__c_xh[-1]:.6f}"] * __binom_tpf[f"{__c_yh[-1]:.6f}"])
                __cell.append(self.__var['dx'] * self.__var['dy'] * .25 * 
                    (__binom_sw[-1] + __binom_nw[-1] + __binom_se[-1] + __binom_ne[-1]))
                x += self.__var['dx']
            y += self.__var['dy']
        # convert data to dataframe
        self.__df = pd.DataFrame({
            'XL': __c_xl,
            'XH': __c_xh,
            'YL': __c_yl,
            'YH': __c_yh,
            'sw': __binom_sw,
            'nw': __binom_nw,
            'se': __binom_se,
            'ne': __binom_ne,
            'cell': __cell,
            })
        # sort the dataframe by 'cell' in assending order
        self.__df.sort_values(by=['cell'], inplace=True)
        self.__df.reset_index(drop=True, inplace=True)
        # calculate cumulative integral and add to dataframe
        __cell_cum = []
        __cell_cum.append(self.__df['cell'][0])
        for i in range(1, len(self.__df['cell'])):
            __cell_cum.append(__cell_cum[i - 1] + self.__df['cell'][i])
        self.__df['ccum'] = __cell_cum
        return
    
    def __get_normalization_factor(self, ):
        """
        Get the 2-dimensional cummulative probabillity distribution 
        normalization factor, which is calculated in the 
        __cal_binomial_distribution_2D() method.

        Parameters
        ----------
        None.

        Returns
        -------
        float
            The 2-dimensional cummulative probabillity distribution 
            normalization factor.

        """
        return list(self.__df['ccum'])[-1]
    
    def __cal_normalized_cum_dist(self, ):
        """
        Calculates 2-dimensional normalized binomial probability cummulative 
        distribution. The results are stored in the private dataframe.

        Parameters
        ----------
        None.

        Returns
        -------
        None.

        """
        __cg = []
        __norm = 100. / self.__get_normalization_factor()
        for i in range(len(self.__df['ccum'])):
            __cg.append(100. - self.__df['ccum'][i] * __norm)
        self.__df['CG'] = __cg
        return
    
    def __cal_CR_bound(self, esmt={}, alpha=[.05], dx=.1, dy=.1, FPF=False, TPF=False):
        """
        Calculates the 2-dimensional bound of the joint FPF-TPF CRs. 
        The results are stored in the private dataframe.
        

        Parameters
        ----------
        esmt : dict, optional
            DESCRIPTION. The default is {}.
        alpha : list of floats, optional
            The alpha values of a nominal joint CRs levels. The default is [.05].
        dx : float, optional
            The integration interval on FPF for calculating the joint binomial
            cummulative distribution. The default is .0001.
        dy : float, optional
            The integration interval on TPF for calculating the joint binomial
            cummulative distribution. The default is .0001.
        FPF : float, optional
            The population FPF value. The default is None.
        TPF : float, optional
            The population TPF value. The default is None.

        Returns
        -------
        esmt : TYPE
            DESCRIPTION.

        """
        __dx = .5 * dx
        __dy = .5 * dy
        esmt['CG2'] = {}
        for a in alpha:
            __k = f"CG{(1 - a) * 100:.0f}pts"
            esmt['CG2'][a] = {}
            if FPF and TPF:
                esmt['CG2'][a]['i'] = self.__cal_CG_contains_population_values(
                    esmt, fpf=FPF, tpf=TPF)
            esmt['CG2'][a][__k] = []
            __x_mins = []
            __x_maxs = []
            __dff = esmt['df'][esmt['df']['CG'] <= (1. - a) * 100.]
            __dff = __dff.sort_values(by=['YL'], inplace=False)
            __ys = sorted(__dff['YL'].unique())
            for y in __ys:
                __dfy = __dff[__dff['YL'] == y]
                __dfy = __dfy.sort_values(by=['XL'], inplace=False, ignore_index=True)
                __x_mins.append({
                    'X': f"{(__dfy['XL'][0] + __dx):.4f}",
                    'Y': f"{(y + __dy):.4f}",
                    'P': f"{(__dfy['CG'][0]):.2f}",
                    })
                __index = __dfy.shape[0] - 1
                if __index:
                    __x_maxs.append({
                        'X': f"{(__dfy['XL'][__index] + __dx):.4f}",
                        'Y': f"{(y + __dy):.4f}",
                        'P': f"{(__dfy['CG'][__index]):.2f}",
                        })
            # make a full counterclockwise contour
            esmt['CG2'][a][__k].extend(__x_mins)
            esmt['CG2'][a][__k].extend(reversed(__x_maxs))
            esmt['CG2'][a][__k].append(__x_mins[0])
        return esmt
    
    def __cal_CIs_fpf_tpf(self, fp=.1, n_n=100, tp=.8, n_p=75,dx=.001, dy=.001,
                 alpha=[], CI=None, FPF=None, TPF=None, verbose=False):
        """
        Calculates FPF and TPF binomial CIs separately with an instance of 
        the CI class.

        Parameters
        ----------
        fp : TYPE, optional
            DESCRIPTION. The default is .1.
        n_n : TYPE, optional
            DESCRIPTION. The default is 100.
        tp : TYPE, optional
            DESCRIPTION. The default is .8.
        n_p : TYPE, optional
            DESCRIPTION. The default is 75.
        dx : TYPE, optional
            DESCRIPTION. The default is .001.
        dy : TYPE, optional
            DESCRIPTION. The default is .001.
        alpha : TYPE, optional
            DESCRIPTION. The default is [].
        CI : TYPE, optional
            DESCRIPTION. The default is None.
        FPF : TYPE, optional
            DESCRIPTION. The default is None.
        TPF : TYPE, optional
            DESCRIPTION. The default is None.
        verbose : TYPE, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        __fpf_CI : dict
            Estimate of the FPF binomial probability and CIs.
        __tpf_CI : dict
            Estimate of the TPF binomial probability and CIs.

        """
        __fpf_CI = CI.cal(fp, n_n, alpha=alpha, dx=dx, Prob=FPF, verbose=False)
        __tpf_CI = CI.cal(tp, n_p, alpha=alpha, dx=dy, Prob=TPF, verbose=False)
        return __fpf_CI, __tpf_CI
    
    def __cal_CG_contains_population_values(self, est, fpf=None, tpf=None, alpha=[]):
        """
        Calculates whether joint FPF-TPF binomial CRs estimated with an instance 
        of the CR class contains a given pair of binomial probability population 
        values (FPF, TPF).

        Parameters
        ----------
        est : dict
            Estimate of binomial CRs produced by an instanc of the CR class. 
        fpf : float, optional
            A given binomial probability FPF population value. The default is None.
        tpf : float, optional
            A given binomial probability TPF population value. The default is None.

        Returns
        -------
        est : dict
            Estimate of binomial CRs.

        """
        if not (fpf and tpf):
            return est
        __df = self.__df.loc[
                    (self.__df['XL'] <= fpf) & (self.__df['XH'] >= fpf) &
                    (self.__df['YL'] <= tpf) & (self.__df['YH'] >= tpf) ]
        __a = __df['CG'].to_list()
        # for a in alpha:
        for a in est['CG2'].keys():
            __p = 100. * (1. - a)
            if len(__a) == 0:
                est['CG2'][a]['i'] = -1   # error: (fpf, tpf) outside the bound of the ROC square
            elif len(__a) > 1:
                est['CG2'][a]['i'] = -2   # error: should match only one row in dataframe but found more than one
            elif __a[0] <= __p:
                est['CG2'][a]['i'] = 1
            elif __a[0] > __p:
                est['CG2'][a]['i'] = 0
        return est
    
    def __cal_CIs_contains_population_values(self, est, fpf=None, tpf=None):
        """
        Calculates whether a rectanglar region defined by FPF and TPF binomial 
        CIs estimated separately with an instance of the CR class contains 
        a given pair of binomial probability population values (FPF, TPF).

        Parameters
        ----------
        est : dict
            Estimate of binomial CRs produced by an instanc of the CR class. 
        fpf : float, optional
            A given binomial probability FPF population value. The default is None.
        tpf : float, optional
            A given binomial probability TPF population value. The default is None.

        Returns
        -------
        est : dict
            Estimate of binomial CRs.

        """
        if not (fpf and tpf):
            return est
        # for a in alpha:
        for a in est['CG2'].keys():
            if  fpf >= est['CI FPF']['CI'][a]['L'] and \
                fpf <= est['CI FPF']['CI'][a]['R'] and \
                tpf >= est['CI TPF']['CI'][a]['L'] and \
                tpf <= est['CI TPF']['CI'][a]['R']:
                est['CG2'][a]['CIi'] = 1
            else:
                est['CG2'][a]['CIi'] = 0
        return est

    def __cal_CR_all(self, fp, n_n, tp, n_p, alpha=[.05], dx=.0001, dy=.0001,
              CI=None, FPF=None, TPF=None, verbose=False):
        """
        Estimates the FPF and TPF binomial probabilities and their joint CRs.

        Parameters
        ----------
        fp : int
            The number of false positive cases.
        n_n : int
            The number of catually negative cases.
        tp : int
            The number of true positive cases.
        n_p : int
            The number of catually positive cases.
        alpha : list of floats, optional
            The alpha values of a nominal joint CRs levels. The default is [.05].
        dx : float, optional
            The integration interval on FPF for calculating the joint binomial
            cummulative distribution. The default is .0001.
        dy : float, optional
            The integration interval on TPF for calculating the joint binomial
            cummulative distribution. The default is .0001.
        CI : class instance, optional
            An instance of the CI class. The default is None.
        FPF : float, optional
            The population FPF value. The default is None.
        TPF : float, optional
            The population TPF value. The default is None.
        verbose : bool, optional
            Whether to print verbose messages. The default is False.

        Returns
        -------
        __esmt : dict
            Estimate of the FPF and TPF binomial probability and their joint CRs.

        """
        self.__reset()
        self.__var['dx'] = dx
        self.__var['dy'] = dy
        self.__cal_binomial_distribution_2D(fp, n_n, tp, n_p, )
        self.__cal_normalized_cum_dist()
        __esmt = {'mle': {}}
        __esmt['mle']['FPF'] = self.__cal_binomial_MLE(fp, n_n)
        __esmt['mle']['TPF'] = self.__cal_binomial_MLE(tp, n_p)
        __esmt['CG'] =list(self.__df['CG'])
        __esmt['df'] = self.__df
        __esmt['CI FPF'], __esmt['CI TPF'] = self.__cal_CIs_fpf_tpf(
            fp=fp, n_n=n_n, tp=tp, n_p=n_p,dx=dx, dy=dy,
            alpha=alpha, CI=CI, FPF=FPF, TPF=TPF, verbose=verbose)
        __esmt = self.__cal_CR_bound(esmt=__esmt, alpha=alpha, dx=dx, dy=dy, )
        __esmt = self.__cal_CG_contains_population_values(
            __esmt, fpf=FPF, tpf=TPF)
        __esmt = self.__cal_CIs_contains_population_values(
            __esmt, fpf=FPF, tpf=TPF)
        self.__reset()
        return __esmt
    
    def __report(self, fp, n_n, tp, n_p, alpha, esmt, ):
        __text  =  "The ML estimate of\n"
        __text += f"  FPF of {fp} / {n_n} is {esmt['mle']['FPF']:.4f}, \n"
        __text += f"  TPF of {tp} / {n_p} is {esmt['mle']['TPF']:.4f}.\n"
        for __a in alpha:
            __aa = (1. - __a) * 100.
            __size = float(len([x for x in esmt['CG'] if x < __aa])) / \
                     float(len(esmt['CG']))
            __text += f"  {__aa:.0f}% CG size is {__size:.4f}.\n"
        print(__text, end='')
        return
    
    def __report_CI(self, fp=.1, n_n=100, tp=.8, n_p=75, fpf_CI={}, tpf_CI={}, 
                    alpha=[], ):
        for a in alpha:
            print(f"  {(1. - a) * 100:.0f}% CI of FPF of " + 
                  f"{fp} / {n_n} is " +
                  f"[{fpf_CI['CI'][a]['L']:.3f}, " + 
                  f"{fpf_CI['CI'][a]['R']:.3f}], " +
                  f"TPF of {tp} / {n_p} is " +
                  f"[{tpf_CI['CI'][a]['L']:.3f}, " + 
                  f"{tpf_CI['CI'][a]['R']:.3f}]")
        return
    
    def __report_CG2_pts_tex_data(self, esmt={}, dx=.001, dy=.001,
                                  fp=.1, n_n=100, tp=.8, n_p=75,
                                  tex={}, alpha=[], verbose=False, CI=None):
        if not tex:
            return
        __text = ''
        __dict = {
            'mle': r'\newcommand{\MLE}[0]{',
            '99':  r'\newcommand{\CIninetynine}[0]{',
            '95':  r'\newcommand{\CIninetyfive}[0]{',
            '90':  r'\newcommand{\CIninety}[0]{',
            '80':  r'\newcommand{\CIeighty}[0]{', 
        }  
        __text += f"{__dict['mle']}\n"
        __text += f"  ({esmt['mle']['FPF']:.4f},{esmt['mle']['TPF']:.4f})\n"
        __text += '}\n\n'

        for __a in alpha:
            k = f"{(1. - __a) * 100:.0f}"
            __text += f"{__dict[k]}\n"
            __text += f"  ({esmt['CI FPF']['CI'][__a]['L']:.3f},{esmt['CI TPF']['CI'][__a]['L']:.3f})\n"
            __text += f"  ({esmt['CI FPF']['CI'][__a]['R']:.3f},{esmt['CI TPF']['CI'][__a]['L']:.3f})\n"
            __text += f"  ({esmt['CI FPF']['CI'][__a]['R']:.3f},{esmt['CI TPF']['CI'][__a]['R']:.3f})\n"
            __text += f"  ({esmt['CI FPF']['CI'][__a]['L']:.3f},{esmt['CI TPF']['CI'][__a]['R']:.3f})\n"
            __text += f"  ({esmt['CI FPF']['CI'][__a]['L']:.3f},{esmt['CI TPF']['CI'][__a]['L']:.3f})\n"
            __text += '}\n\n'
        if verbose:
            self.__report_CI(fp=fp, n_n=n_n, tp=tp, n_p=n_p, alpha=alpha,
                             fpf_CI=esmt['CI FPF'], tpf_CI=esmt['CI TPF'])
    
        __dict = {
            '99':  r'\newcommand{\CRninetynine}[0]{',
            '95':  r'\newcommand{\CRninetyfive}[0]{',
            '90':  r'\newcommand{\CRninety}[0]{',
            '80':  r'\newcommand{\CReighty}[0]{', 
        }   
        for a in sorted(esmt['CG2'].keys()):
            k = f"{(1. - a) * 100:.0f}"
            __text += f"{__dict[k]}\n"
            for i in esmt['CG2'][a][f"CG{k}pts"]:
                __text += f"  ({i['X']},{i['Y']})\n"
            __text += '}\n\n'
        __file = os.path.join(tex['dir'], f"{tex['CR_data']}.{fp}_{n_n}.{tp}_{n_p}")
        __f = open(__file, 'w')
        print(__text, file=__f)
        __f.close()
        if verbose:
            __text  = f"  CG bound coordinates are saved in {__file}"
            print(__text)
        return
    
    def cal(self, fp=.1, n_n=100, tp=.8, n_p=75, alpha=[.05], dx=.0001, dy=.0001, 
            FPF=None, TPF=None, tex={}, verbose=False, CI=None):
        # print(fp, n_n, tp, n_p, alpha, dx, dy, tex, verbose)
        if not isinstance(alpha, list):
            alpha = [alpha]
        __esmt = self.__cal_CR_all(fp=fp, n_n=n_n, tp=tp, n_p=n_p, alpha=alpha, dx=dx, dy=dy,
                            CI=CI, FPF=FPF, TPF=TPF, verbose=verbose)
        if verbose:
            self.__report(fp, n_n, tp, n_p, alpha, __esmt, )
        self.__report_CG2_pts_tex_data(esmt=__esmt, alpha=alpha, 
                                       dx=dx, dy=dy, CI=CI, 
                                       fp=fp, n_n=n_n, tp=tp, n_p=n_p,
                                       tex=tex, verbose=verbose)
        return __esmt
    

    

class CI():
    def __init__(self):
        self.__var = {
            'dx': .0001,
            }
        self.__df = pd.DataFrame()
        return
    
    def __reset(self, ):
        """
        Resets (empties) the private dataframe to start a new calculation 
        and to release the dataframe from memory.

        Parameters
        ----------
        None.

        Returns
        -------
        None.

        """
        self.__df.drop(list(self.__df.index.values), inplace=True)
        self.__df.drop(columns=list(self.__df.columns.values), inplace=True)
        return

    def __cal_binomial_MLE(self, x, n):
        """
        Calculates the maximum-likelihood estimate of the binomial probability.

        Parameters
        ----------
        x : int
            Number of "successes."
        n : int
            Number of "total trials."

        Returns
        -------
        float
            Maximum-likelihood estimate of binomial probability.

        """
        return float(x) / float(n)
    
    def __cal_binomial_distribution(self, x, n):
        """
        Calculates the binomial probability cummulative distribution.
        The results are stored in a private dataframe.

        Parameters
        ----------
        x : int
            Number of "successes."
        n : int
            Number of "total trials."

        Returns
        -------
        None.

        """
        __cell_prob = []    # binomial probability within a cell
        __cell_lower = []   # lower bound of a cell
        __cell_upper = []   # upper bound of a cell
        __binom_lower = []  # binomial probability density at the lower bound of a cell
        __binom_upper = []  # binomial probability density at the upper bound of a cell
        __p = 0.            # a given binomial probability value
        # calculate binomial probability density data 
        __const = self.__var['dx'] * .5
        __binom_lower.append(binom.pmf(x, n, __p))
        while __p + self.__var['dx'] <= 1.:
            __cell_lower.append(__p)
            __cell_upper.append(__p + self.__var['dx'])
            __binom_upper.append(binom.pmf(x, n, __p + self.__var['dx']))
            __cell_prob.append(__const * 
                np.sum([__binom_lower[-1], __binom_upper[-1]]))
            __binom_lower.append(__binom_upper[-1])
            __p += self.__var['dx']
        del __binom_lower[-1]
        # construct the dataframe
        self.__df = pd.DataFrame({
            'L': __cell_lower,
            'R': __cell_upper,
            'LB': __binom_lower,
            'RB': __binom_upper,
            'cell': __cell_prob,
            })
        # sort the dataframe by 'cell' in assending order
        self.__df.sort_values(by=['cell'], inplace=True)
        self.__df.reset_index(drop=True, inplace=True)
        # calculate cumulative binomial probability distribution and add to the dataframe
        __cell_cum = []
        __cell_cum.append(self.__df['cell'][0])
        for i in range(1, len(self.__df['cell'])):
            __cell_cum.append(__cell_cum[i - 1] + self.__df['cell'][i])
        self.__df['ccum'] = __cell_cum
        # print(self.__df)
        return
    
    def __get_normalization_factor(self, ):
        """
        Get the cummulative probabillity distribution normalization factor,
        which is calculated in the __cal_binomial_distribution() method.

        Parameters
        ----------
        None.

        Returns
        -------
        float
            The cummulative probabillity distribution normalization factor.

        """
        return list(self.__df['ccum'])[-1]
    
    def __cal_CI_bound(self, p, alpha):
        """
        Calculates binomial CI bounds from the binomial probabillity
        cummulative distribution.

        Parameters
        ----------
        p : float 
            binomial probability.
        alpha : float
            The alpha value of a nominal CI level.

        Returns
        -------
        __CIbd : list of floats
            Binomial CI bound.

        """
        __len = len([x for x in self.__df['ccum'] 
                     if x < alpha * self.__get_normalization_factor()])
        __CIbd = [0., 1.]
        __lt = [x for x in list(self.__df['L'])[:__len] if x > p]
        __rt = [x for x in list(self.__df['R'])[:__len] if x < p]
        if len(__lt):
            __CIbd[1] = np.min(__lt)
        if len(__rt):
            __CIbd[0] = np.max(__rt)
        # if p == 1.0:
        #     __CIbd[1] = 1.
        # else:
        #     __CIbd[1] = np.min([x for x in list(self.__df['L'])[:__len] if x > p])
        # if p == 0.:
        #     __CIbd[0] = 0.
        # else:
        #     __CIbd[0] = np.max([x for x in list(self.__df['R'])[:__len] if x < p])
        return __CIbd
        # return [np.max([x for x in list(self.__df['R'])[:__len] if x < p]),
        #         np.min([x for x in list(self.__df['L'])[:__len] if x > p]) ]
    
    def __cal_CI_contains_population_value(self, est, p=None, ):
        """
        Calculates whether binomial CIs estimated with an instance of the 
        CI class contains a given binomail probability population value.

        Parameters
        ----------
        est : dict
            Estimate of binomial CIs produced by an instanc of the CI class. 
        p : float, optional
            A given binomial probability population value. The default is None.

        Returns
        -------
        est : dict
            Estimate of binomial CIs.

        """
        if not p:
            return est
        # for a in alpha:
        for a in est['CI'].keys():
            if p >= est['CI'][a]['L'] and p <= est['CI'][a]['R']:
                est['CI'][a]['i'] = 1
            else:
                est['CI'][a]['i'] = 0
        return est
    
    def __cal_CI_all(self, x, n, alpha=[.05], dx=.0001, Prob=None):
        """
        Estimates the binomial probability and CIs.

        Parameters
        ----------
        x : int
            The number of "successes." The default is None.
        n : int
            The number of "total trials." The default is None.
        alpha : list of floats, optional
            The alpha values of a nominal CI levels. The default is [.05].
        dx : float, optional
            The integration interval for calculating binomial
            cummulative distribution. The default is .0001.
        Prob : float, optional
            Binomial probability population value. The default is None.

        Returns
        -------
        __esmt : dict
            An estimate of the binomial probability and its CIs.

        """
        self.__reset()
        if not isinstance(alpha, list):
            alpha = [alpha]
        self.__var['dx'] = dx
        self.__cal_binomial_distribution(x, n)
        __esmt = {'CI': {}}
        __esmt['mle'] = self.__cal_binomial_MLE(x, n)
        for a in alpha:
            __CI = self.__cal_CI_bound(__esmt['mle'], a)
            __esmt['CI'][a] = {'L': __CI[0], 'R': __CI[1]}
        __esmt = self.__cal_CI_contains_population_value(
            __esmt, p=Prob, )
        # CI = self.__depr2_CI(x, n, alpha)
        self.__reset()
        return __esmt
    
    def __report(self, x, n, esmt, ):
        __text  =  "The ML estimate of binomial proportion of "
        __text += f"{x} / {n} is {esmt['mle']:.4f}, "
        for a in esmt['CI'].keys():
            __text += f"{(1 - a) * 100.:.0f}% CI: {esmt['CI'][a]['L']:.4f}, {esmt['CI'][a]['R']:.4f}, "
        print(__text)
        return
    
    def cal(self, x, n, alpha=[.05], dx=.0001, Prob=None, verbose=False):
        __esmt = self.__cal_CI_all(x, n, alpha=alpha, dx=dx, Prob=Prob)
        if verbose:
            self.__report(x, n, __esmt, )
        return __esmt    


    
    
