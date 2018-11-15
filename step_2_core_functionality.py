import lingpy
import lingpy.compare.partial

lex = lingpy.compare.partial.Partial(
  "wordlist.tsv")

try:
  scorers_etc = lingpy.compare.lexstat.LexStat(
    "lexstats.tsv")
  lex.scorer = scorers_etc.scorer
  lex.cscorer = scorers_etc.cscorer
  lex.bscorer = scorers_etc.bscorer
except OSError:
  lex.get_scorer(runs=10000)
  lex.output('tsv', filename='lexstats', ignore=[])

lex.partial_cluster(
  method='lexstat',
  threshold=0.55,
  cluster_method="infomap",
  ref='partialids',
  verbose=True)

alm = lingpy.Alignments(lex, ref="partialids", fuzzy=True)
alm.align(method='progressive')
alm.output('tsv', filename='aligned',
  ignore='all', prettify=False)
