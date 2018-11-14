import lingpy
import lingpy.compare.partial

lex = lingpy.compare.partial.Partial(
  "wordlist.tsv")

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
