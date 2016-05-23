# -*- coding: utf-8 -*-
"""
Created on Sat Oct 31 20:15:25 2015

@authors: Sonya Tahir, Amit Talapatra, Wendy Zhang, Wei Zheng

This file runs the poverty data plot and plot based on the five selected
indicators in R via the plotmap.R file
"""

import rpy2.robjects as robjects

def main():
    r = robjects.r
    r['source']("plotmap.R")
    r('plot_poverty()')
    print "poverty.pdf has been generated"
    r('plot_final5()')
    print "five_indicators.pdf has been generated"

main()