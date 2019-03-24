"""
    Author: Alejandro Sifrim
    Affiliation: Wellcome Trust Sanger Institute

    Script to call inheritance mode of an event

    Parameters
    ----------
    1) child score file
	2) mother bam
	3) father bam

    Returns
    -------
	1) File with putative denovo calls

"""

import os
import sys
import pysam
import csv
from indelible.indelible_lib import *
import scipy.stats as sp
import math

def compute_stats(bam_reader,chrom,position,relationship,config):
	res = {}
	if bam_reader is None:
		res['coverage'] = None
		res['indel_context']['deletions'] = None
		res['indel_context']['insertions'] = None
		res['sr_context'] = None
	else:
		res['coverage'] = coverage_at_position_pileup(bam_reader, chrom, position)
		res['indel_context'] = reads_with_indels_in_neighbourhood(bam_reader, chrom, position, config)
		res['sr_context'] = split_reads_in_neighbourhood(bam_reader, chrom, position, config)
		# res['relationship'] = relationship

	return res

def denovo_caller_trio(child_input, mother_bam, father_bam, output_path,config):

	mum_reader = bam_open(mother_bam)
	dad_reader = bam_open(father_bam)

	scored_file = csv.DictReader(open(child_input,'r'), delimiter="\t")
	new_fieldnames = scored_file.fieldnames
	new_fieldnames.extend(("mum_sr","dad_sr",'mum_indel_context','dad_indel_context',"mum_cov","dad_cov"))
	output_file = csv.DictWriter(open(output_path,'w'),fieldnames=new_fieldnames,delimiter="\t")
	output_file.writeheader()

	for v in csv.DictReader(open(child_input,'r'), delimiter="\t"):
		if float(v['prob_Y']) >= config['SCORE_THRESHOLD']:
			mum_stats = compute_stats(mum_reader,v['chrom'],int(v['position']),'mum',config)
			dad_stats = compute_stats(dad_reader,v['chrom'],int(v['position']),'dad',config)
			v['mum_sr'] =  mum_stats['sr_context']
			v['dad_sr'] =  dad_stats['sr_context']
			v['mum_indel_context'] =  mum_stats['indel_context']['deletions'] +  mum_stats['indel_context']['insertions']
			v['dad_indel_context'] =  dad_stats['indel_context']['deletions'] + dad_stats['indel_context']['insertions']
			v['mum_cov'] = mum_stats['coverage']
			v['dad_cov'] = dad_stats['coverage']
			if mother_bam is None or father_bam is None:
				output_file.writerow(v)
			else:
				if v['mum_sr'] <= config['SR_THRESHOLD'] and v['dad_sr'] <= config['SR_THRESHOLD'] and v['mum_cov'] >= config['COV_THRESHOLD'] and v['dad_cov'] >=  config['COV_THRESHOLD']:
					output_file.writerow(v)