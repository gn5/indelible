"""
    Author: Eugene Gardner
    Affiliation: Wellcome Sanger Institute

    Script to build to AF database necessary for annotation:

    Parameters
    ----------
    1)
	2) mother bam
	3) father bam

    Returns
    -------
	1) File with putative denovo calls

"""

import csv

from indelible.indelible_lib import *

def build_database(score_files, score_threshold):

    db = {}

    allele_count = float(0)

    for file in open(score_files, 'r'):
        allele_count += 1
        print file
        file = file.rstrip()
        c = csv.DictReader(open(file, 'r'), delimiter="\t")
        for line in c:
            if line["prob_Y"] >= score_threshold:
                if line["chrom"] in db:
                    if line["position"] in db[line["chrom"]]:
                        current = db[line["chrom"]][line["position"]]
                        current += 1
                        db[line["chrom"]][line["position"]] = current
                    else:
                        db[line["chrom"]][line["position"]] = 1
                else:
                    db[line["chrom"]] = {}
                    db[line["chrom"]][line["position"]] = 1

        for chr in db:
            for pos in db[chr]:
                af = db[chr][pos] / allele_count
                print chr + "\t" + str(pos) + "\t" + str(af)