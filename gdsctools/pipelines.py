# -*- python -*-
#
#  This file is part of DREAMTools software
#
#  Copyright (c) 2014-2015 - EBI-EMBL
#
#  File author(s): Thomas Cokelaer <cokelaer@ebi.ac.uk>
#
#  Distributed under the GPLv3 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#  website: http://github.org/dreamtools
#
##############################################################################
"""Main standalone application dreamtools"""
import argparse
import sys
from easydev.console import red, purple, darkgreen
from gdsctools import anova, readers


__all__ = ['anova_pipeline', 'ANOVAOptions']


def print_color(txt, func_color, underline=False):
    import easydev
    try:
        if underline:
            print(easydev.underline(func_color(txt)))
        else:
            print(func_color(txt))
    except:
        print(txt)


def anova_pipeline(args=None):
    """This function is used by the standalone application called
    **gdsctools_anova**

    ::

        gdsctools_anova --help

    """
    if args is None:
        args = sys.argv[:]
    user_options = ANOVAOptions(prog="gdsctools_anova")

    if len(args) == 1:
        user_options.parse_args(["prog", "--help"])
    else:
        options = user_options.parse_args(args[1:])

    r = readers.IC50(options.ic50)

    an = anova.ANOVA(r, features=options.features)
    an.settings.savefig = options.savefig
    print options
    if options.savefig is True:
        options.show_boxplots = True
    try:
        df = an.anova_one_drug_one_feature(options.drug, 
            feature_name=options.feature, 
            show_boxplot=options.show_boxplots, 
            savefig=options.savefig)
        print('ok')
    except Exception as err:
        print(red(err.__str__()))
        return

    print(df.T)
    import pylab
    pylab.show()


class ANOVAOptions(argparse.ArgumentParser):
    """Define user interface for the gdsctools_anova standalone application


    """
    description = "tests"
    def __init__(self, version="1.0", prog=None):

        usage = """usage: python %s --challenge d8c1 --sub-challenge sc1a --submission <filename>\n""" % prog
        usage += """      python %s --challenge d5c2 --submission <filename>""" % prog
        epilog="""Author(s): Thomas Cokelaer (GDSCtools) and authors from
the GDSCtools repository. .

Source code on: https://github.com/CancerRxGene/gdsctools
Issues or bug report ? Please fill an issue on
http://github.com/CancerRxGene/gdsctools/issues """
        description = """General Description:

            TODO

"""
        # FIXME : not robust but will work for now
        super(ANOVAOptions, self).__init__(usage=usage, version=version, prog=prog,
                epilog=epilog, description=description,
                formatter_class=argparse.RawDescriptionHelpFormatter)
        self.add_input_options()

    def add_input_options(self):
        """The input options to gdsctools_anova are defined here"""
        group = self.add_argument_group("General", 'General options (compulsary or not)')

        group.add_argument("--ic50", dest='ic50',
                         default=None, type=str,
                         help="""A file in TSV format with IC50s. First column
                         should be the COSMIC identifiers. Following columns
                         contain the IC50s for a set of drugs. The header must
                         be COSMIC IDS, Drug_1_IC50, Drug_2_IC50, ... """)
        group.add_argument("--features", dest='features',
                           default=None, type=str,
                           help="""A matrix of genomic features. First column 
                           is made of COSMIC identifiers that should match 
                           those from the IC50s matrix. Then 3 compulsary 
                           columns are required named 'Sample', 'Tissue', 
                           'MSI'. Other
                           columns should be the genomic features. There are
                           recognised if the (1) ends in _mut for mutation, or
                           starts with loss or gain for the CNA cases. 
                           """)
        #group.add_argument("--data", dest='data',
        #                 default=None, type=str,
        #                 help="A TSV file with cosmic Ids as rows and Drug and"
        #                 + " features as columns. ")
        group.add_argument("--save-images", dest='savefig',
                         action="store_true",
                         help="verbose option.")
        group.add_argument("--verbose", dest='verbose',
                         action="store_true",
                         help="verbose option.")
        group.add_argument("--show-boxplots", dest='show_boxplots',
                         action="store_true",
                         help="show images.")
        group.add_argument("--on-web", dest='on_web',
                         action="store_true",
                         help="TODO")
        group.add_argument("--drug", dest="drug",
                         help="""The name of a valid drug identifier to be 
                         found in the header of the IC50 matrix""")
        group.add_argument("--feature", dest="feature",
                         help="""The name of a valid feature to be found in the
                         Genomic Feature matrix""")


