#!/usr/bin/env python

"""Load word lists from a tabular file in matrix shape, and similarity code and align them for use eg. in Edictor"""

import sys
import csv
from pycldf.util import Path
import xlrd
import argparse
from collections import OrderedDict

import segments

import lingpy
import lingpy.compare.partial


class XLSDictReader():
    def __init__(self, filename, sheet_index=0):
        book = xlrd.open_workbook(str(filename))
        self.sheet = book.sheet_by_index(sheet_index)

        self.fieldnames = [self[0, col]
                           for col in range(self.sheet.ncols)]

    def __getitem__(self, index):
        row, col = index
        return self.sheet.cell_value(row, col)

    def __iter__(self):
        for row in range(1, self.sheet.nrows):
            yield OrderedDict(zip(
                self.fieldnames,
                (self[row, column] for column in range(self.sheet.ncols))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("input",
                        type=Path,
                        help="Input file containing the word list matrix.")
    parser.add_argument("--filetype", default="guess",
                        choices=["guess", "csv", "tsv", "xls"],
                        help="Type of the word list matrix file."
                        " (default: guess based on the extension)")
    parser.add_argument("output", default=sys.stdout, nargs="?",
                        type=argparse.FileType('w'),
                        help="Output file to write segmented data to."
                        " (default: STDOUT)")
    parser.add_argument("--gloss", default=[0],
                        type=str.split,
                        help="Columns to be used as gloss languages, specified"
                        " as whitespace-separated list of column headers or"
                        " numerical ids. (default: 0)")
    args = parser.parse_args()

    tokenizer = segments.Tokenizer()

    if args.filetype == "guess":
        args.filetype = args.input.suffix[1:]

    if args.filetype == "csv":
        data = csv.DictReader(args.input.open())
    elif args.filetype == "tsv":
        data = csv.DictReader(args.input.open(), dialect="excel-tab")
    elif args.filetype == "xlsx":
        data = XLSDictReader(args.input)
    else:
        raise ValueError("File type {:} not recognized.".format(
            args.filetype))

    glosses = []
    for column in args.gloss:
        try:
            glosses.append(data.fieldnames[int(column)])
        except ValueError:
            assert column in data.fieldnames
            glosses.append(column)

    out = {0: ["concept", "doculect", "ipa", "tokens"]}
    for line in data:
        gloss = " / ".join(line[x] for x in glosses)
        for lect, words in line.items():
            if lect in glosses:
                continue
            for word in words.split(","):
                word = word.strip()
                if not word:
                    continue
                # Tokenizer uses # as word boundary, partial prefers _
                segments = tokenizer(word, ipa=True).replace("#", "_").split()
                out[len(out)] = [gloss, lect, word, segments]

    lex = lingpy.compare.partial.Partial(out,
        col="doculect", row="concept", segments="tokens", transcription="ipa")
    lex.get_scorer(runs=1000)
    lex.output('tsv', filename='lexstats', ignore=[])
    # For some purposes it is useful to have monolithic cognate classes.
    lex.cluster(method='lexstat', threshold=0.55, ref='cogid', cluster_method="infomap", verbose=True)
    # But actually, in most cases partial cognates are much more useful.
    lex.partial_cluster(method='lexstat', threshold=0.55, ref='partialids', cluster_method="infomap", verbose=True)
    lex.output("tsv", filename="auto-clusters")
    alm = lingpy.Alignments(lex, row="concept", col="doculect",
                            segments="tokens", transcription="ipa",
                            ref="partialids",
                            fuzzy=True)
    alm.align(method='progressive')
    alm.output('tsv', filename='aligned', ignore='all', prettify=False)



