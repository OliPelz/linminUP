#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------------------
# File Name: align_lastal.py
# Purpose:
# Creation Date: 2014 - 2015
# Last Modified: Fri Nov 13 17:02:09 2015
# Author(s): The DeepSEQ Team, University of Nottingham UK
# Copyright 2015 The Author(s) All Rights Reserved
# Credits:
# --------------------------------------------------

import re
import subprocess
import threading

class last_threader(threading.Thread):

    def __init__(
        self,
	oper,
        args,
        seqid,
        fastqdata,
        basename,
        basenameid,
        dbname,
        db,
	ref_fasta_hash,
        ):
        threading.Thread.__init__(self)
	self.oper = oper
        self.seqid = seqid
        self.fastqdata = fastqdata
        self.basename = basename
        self.basenameid = basenameid
        self.dbname = dbname
        self.db = db
        self.args = args
	self.ref_fasta_hash = ref_fasta_hash

    def run(self):
        do_last_align(
	    self.oper,
            self.args,
            self.seqid,
            self.fastqdata,
            self.basename,
            self.basenameid,
            self.dbname,
            self.db,
	    self.ref_fasta_hash
            )


# ---------------------------------------------------------------------------
def init_last_threads(
    oper,
    args,
    connections,
    fastqhash,
    basename,
    basenameid,
    dbname,
    dbcheckhash,
    ref_fasta_hash,
    ):
    backgrounds = []
    d = 0
    for seqid in fastqhash.keys():
        db = connections[d]
        fastqdata = fastqhash[seqid]
        background = last_threader(
	    oper,
            args,
            seqid,
            #dbcheckhash,
            fastqdata,
            basename,
            basenameid,
            dbname,
            db,
	    ref_fasta_hash,
            )
        background.start()
        backgrounds.append(background)
        d += 1
    for background in backgrounds:
        background.join()


# ---------------------------------------------------------------------------

def do_last_align(
    oper,
    args,
    qname,
    fastqhash,
    basename,
    basenameid,
    dbname,
    db,
    ref_fasta_hash,
    ):
    cursor = db.cursor()

    # def do_bwa_align(seqid, fastqhash, basename, basenameid, dbname, cursor):
    # Op BAM Description
    # M 0 alignment match (can be a sequence match or mismatch)
    # I 1 insertion to the reference
    # D 2 deletion from the reference
    # N 3 skipped region from the reference
    # S 4 soft clipping (clipped sequences present in SEQ)
    # H 5 hard clipping (clipped sequences NOT present inSEQ)
    # P 6 padding (silent deletion from padded reference)
    # = 7 sequence match
    # X 8 sequence mismatch
    # align_prefix=ref_basename

    # print "starting alignment", (time.time())-starttime
    # cmd='lastal -s 2 -T 0 -Q 0 -a 1  %s.last.index %s.fasta > %s.temp.maf' %(ref_fasta_hash[dbname]["prefix"], basename, basename)
    # cmd='parallel-fasta -j %s "lastal -s 2 -T 0 -Q 0 -a 1 %s.last.index" < %s.fasta > %s.temp.maf'  %(args.threads, ref_fasta_hash[dbname]["prefix"], basename, basename)
    # print cmd
    # proc = subprocess.Popen(cmd, shell=True)
    # status = proc.wait()

    options = '-' + args.last_options.replace(',', ' -')
    cmd = str()
    if oper is 'linux':
        import os
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        cmd = 'lastal %s  %s -' % (options,
                                   ref_fasta_hash[dbname]['last_index'])
        cmd = "qsub -I -v CMD='" + cmd + "' -N 'run_lastal_align' " + scriptDir + "/../openpbs.sh"

    if oper is 'windows':
        cmd = 'lastal %s  %s ' % (options,
                                  ref_fasta_hash[dbname]['last_index'])

    read = '>%s \r\n%s' % (qname, fastqhash['seq'])

    # print cmd

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate(input=read)

    # print err

    status = proc.wait()
    maf = out.encode('utf-8')
    lines = maf.splitlines()

    count_read_align_record = dict()
    count_read_aligned_bases = dict()

    colstring = \
        'basename_id,refid,alignnum,covcount,alignstrand,score,seqpos,refpos,seqbase,refbase,seqbasequal,cigarclass'
    colstring_maf = \
        'basename_id,refid,alignnum,alignstrand,score,r_start,q_start,r_align_len,q_align_len,r_align_string,q_align_string'

    alignedreadids = dict()
    primes = dict()

    # with open(basename+".temp.maf", "r") as lastfile:
    # lines=lastfile.readlines()

    count_read_align_record = 0

    # lines=out.splitlines()

    line_number = 0

    # print "lines", len(lines)

    while line_number < len(lines) - 2:

        # print lines[line_number]
        # print ">>>", len(lines[line_number]), "<<<"

        if 0 < len(lines[line_number]) and lines[line_number][0] is 'a' \
            and lines[line_number + 1][0] is 's' and lines[line_number
                + 2][0] is 's':

            # print "num",line_number, line_number+1, line_number+2
            # ---------------------------------------------------------------------------

            score = re.split(' |=', lines[line_number])[2]
            r_list = lines[line_number + 1].split()
            q_list = lines[line_number + 2].split()

            # name start alnSize strand seqSize alignment

            rname = r_list[1]
            rstart = int(r_list[2])
            rlen = int(r_list[3])
            rend = int(r_list[5])

            # ---------------------------------------------------------------------------

            qname = q_list[1]
            qstart = int(q_list[2])
            qlen = int(q_list[3])
            qend = int(q_list[5])

            # ---------------------------------------------------------------------------

            raln = list(r_list[6])
            qaln = list(q_list[6])
            strand = q_list[4]

            # ---------------------------------------------------------------------------

            if args.verbose is True:
                align_message = '%s\tAligned:%s:%s-%s (%s) ' % (qname,
                        rname, rstart, rstart + rlen, strand)
                print align_message

            # ---------------------------------------------------------------------------I think this is the point we know a read is aligning.
            # print dbname,qname.split('.')[1]

            sql = 'UPDATE ' + dbname + '.' + qname.split('.')[-1] \
                + " SET align='1' WHERE basename_id=\'%s\'" % basenameid  # ML
            cursor.execute(sql)
            db.commit()

            # print lines[line_number]
            # print lines[line_number+1]
            # print lines[line_number+2]

            # ---------------------------------------------------------------------------

            count_read_align_record += 1  # count the read id occurances

            # ---------------------------------------------------------------------------

            readbases = list(fastqhash['seq'])
            qualscores = fastqhash['quals']

            # refbases=ref_fasta_hash["seq_len"][rname]

            refid = ref_fasta_hash[dbname]['refid'][rname]

            # ---------------------------------------------------------------------------

            align_strand = ''

            # ---------------------------------------------------------------------------

            if strand is '+':
                align_strand = 'F'

            # ---------------------------------------------------------------------------

            if strand is '-':
                align_strand = 'R'

            # --------------------------------------------------------------------------- do 5' 3' aligned read base position calc. ########

            tablename = 'last_align_' + qname.rsplit('.', 1)[1]
            valstring = ''

            first_q_align_base_index = int(q_list[2])
            last_q_align_base_index = int(q_list[2]) + int(q_list[3]) \
                - 1
            first_refbase = raln[0]
            last_refbase = raln[len(raln) - 1]
            first_refbase_index = rstart + 1
            last_refbase_index = rstart + rlen

            if strand is '-':
                last_q_align_base_index = int(q_list[5]) \
                    - int(q_list[2]) - 1
                first_q_align_base_index = int(q_list[5]) \
                    - int(q_list[2]) - int(q_list[3])
                first_refbase = raln[len(raln) - 1]
                last_refbase = raln[0]
                first_refbase_index = rstart + rlen
                last_refbase_index = rstart + 1

            if tablename in primes:
                if first_q_align_base_index + 1 \
                    < primes[tablename]['fiveprime']['seqpos']:  # lowest seqpos
                    primes[tablename]['fiveprime']['seqpos'] = \
                        first_q_align_base_index + 1
                    valstring = '('
                    valstring += '%s,' % basenameid  # basename_id
                    valstring += '%s,' % refid  # refid
                    valstring += '%s,' % count_read_align_record  # alignnum
                    valstring += '%s,' % '0'  # covcount

                    # valstring+= "%s," % count_read_aligned_bases[(qname,rname,rstart)] # covcount

                    valstring += "\'%s\'," % align_strand  # alignstrand
                    valstring += '%s,' % score  # score
                    valstring += '%s,' % (first_q_align_base_index + 1)  # seqpos
                    valstring += '%s,' % first_refbase_index  # refpos
                    valstring += "\'%s\'," \
                        % readbases[first_q_align_base_index]  # seqbase
                    valstring += "\'%s\'," % first_refbase  # refbase
                    valstring += '%s,' \
                        % qualscores[first_q_align_base_index]  # seqbasequal
                    valstring += '%s' % '7'  # cigarclass
                    valstring += ')'
                    primes[tablename]['fiveprime']['string'] = valstring

                if primes[tablename]['threeprime']['seqpos'] \
                    < last_q_align_base_index + 1:  # lowest seqpos
                    primes[tablename]['threeprime']['seqpos'] = \
                        last_q_align_base_index + 1
                    valstring = '('
                    valstring += '%s,' % basenameid  # basename_id
                    valstring += '%s,' % refid  # refid
                    valstring += '%s,' % count_read_align_record  # alignnum
                    valstring += '%s,' % '0'  # covcount

                    # valstring+= "%s," % count_read_aligned_bases[(qname,rname,rstart)] # covcount

                    valstring += "\'%s\'," % align_strand  # alignstrand
                    valstring += '%s,' % score  # score
                    valstring += '%s,' % (last_q_align_base_index + 1)  # seqpos
                    valstring += '%s,' % last_refbase_index  # refpos

                    # print (qstart+qlen), len(readbases)

                    valstring += "\'%s\'," \
                        % readbases[last_q_align_base_index]  # seqbase
                    valstring += "\'%s\'," % last_refbase  # refbase
                    valstring += '%s,' \
                        % qualscores[last_q_align_base_index]  # seqbasequal
                    valstring += '%s' % '7'  # cigarclass
                    valstring += ')'
                    primes[tablename]['threeprime']['string'] = \
                        valstring

            if tablename not in primes:
                primes[tablename] = dict()
                primes[tablename]['fiveprime'] = dict()
                primes[tablename]['fiveprime']['seqpos'] = \
                    first_q_align_base_index + 1
                valstring = '('
                valstring += '%s,' % basenameid  # basename_id
                valstring += '%s,' % refid  # refid
                valstring += '%s,' % count_read_align_record  # alignnum
                valstring += '%s,' % '0'  # covcount

                # valstring+= "%s," % count_read_aligned_bases[(qname,rname,rstart)] # covcount

                valstring += "\'%s\'," % align_strand  # alignstrand
                valstring += '%s,' % score  # score
                valstring += '%s,' % (first_q_align_base_index + 1)  # seqpos
                valstring += '%s,' % first_refbase_index  # refpos
                valstring += "\'%s\'," \
                    % readbases[first_q_align_base_index]  # seqbase
                valstring += "\'%s\'," % first_refbase  # refbase
                valstring += '%s,' \
                    % qualscores[first_q_align_base_index]  # seqbasequal
                valstring += '%s' % '7'  # cigarclass
                valstring += ')'
                primes[tablename]['fiveprime']['string'] = valstring
                primes[tablename]['threeprime'] = dict()
                primes[tablename]['threeprime']['seqpos'] = \
                    last_q_align_base_index + 1
                valstring = '('
                valstring += '%s,' % basenameid  # basename_id
                valstring += '%s,' % refid  # refid
                valstring += '%s,' % count_read_align_record  # alignnum
                valstring += '%s,' % '0'  # covcount

                # valstring+= "%s," % count_read_aligned_bases[(qname,rname,rstart)] # covcount

                valstring += "\'%s\'," % align_strand  # alignstrand
                valstring += '%s,' % score  # score
                valstring += '%s,' % (last_q_align_base_index + 1)  # seqpos
                valstring += '%s,' % last_refbase_index  # refpos

                # print (qstart+qlen), len(readbases)
                # print len(qualscores), qend, "#----------------------------------"

                valstring += "\'%s\'," \
                    % readbases[last_q_align_base_index]  # seqbase
                valstring += "\'%s\'," % last_refbase  # refbase
                valstring += '%s,' % qualscores[last_q_align_base_index]  # seqbasequal
                valstring += '%s' % '7'  # cigarclass
                valstring += ')'
                primes[tablename]['threeprime']['string'] = valstring

            # ---------------------------------------------------------------------------

            # ------------ upload MAF -----------
            # if (args.upload_maf is True):

            valstring = str()
            valstring += '%s,' % basenameid  # basename_id
            valstring += '%s,' % refid  # refid
            valstring += '%s,' % count_read_align_record  # alignnum
            valstring += "\'%s\'," % align_strand  # alignstrand
            valstring += '%s,' % score  # score
            valstring += '%s,' % rstart  # r_start
            valstring += '%s,' % qstart  # q_start
            valstring += '%s,' % rlen  # r_align_len
            valstring += '%s,' % qlen  # q_align_len
            valstring += "\'%s\'," % r_list[6]  # r_align_string
            valstring += "\'%s\'" % q_list[6]  # q_align_string
            tablename = 'last_align_maf_' + qname.rsplit('.', 1)[1]
            sql = 'INSERT INTO %s (%s) VALUES (%s) ' % (tablename,
                    colstring_maf, valstring)

            # print sql

            cursor.execute(sql)
            db.commit()

            # ---------------------------------------------------------------------------
            # print "dbname", dbname
            # filehandle=dbcheckhash["mafoutdict"][dbname]
            # filehandle.write(lines[line_number])
            # filehandle.write(lines[line_number+1])
            # filehandle.write(lines[line_number+2]+os.linesep)
            # ---------------------------------------------------------------------------

        line_number += 1

    # -------------- upload 5' 3' prime ends ---------

    for tablename in primes:
        fiveprimetable = tablename + '_5prime'
        threeprimetable = tablename + '_3prime'

        string = primes[tablename]['fiveprime']['string']
        sql = 'INSERT INTO %s (%s) VALUES %s' % (fiveprimetable,
                colstring, string)

        # print "L", sql

        cursor.execute(sql)
        db.commit()

        string = primes[tablename]['threeprime']['string']
        sql = 'INSERT INTO %s (%s) VALUES %s' % (threeprimetable,
                colstring, string)

        # print "L", sql

        cursor.execute(sql)
        db.commit()


    # ---------------------------------------------------------------------------
    # os.remove(basename+".temp.maf")
    # print "finished alignment", (time.time())-starttime

# ---------------------------------------------------------------------------
