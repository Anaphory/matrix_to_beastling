import csv
import xlrd
import segments

book = xlrd.open_workbook("Wordlists.xlsx")
sheet = book.sheet_by_index(0)

def cell(row, col):
  return sheet.cell_value(row, col)

tokenizer = segments.Tokenizer()
def segment(word):
  return tokenizer(word, ipa=True, separator=" _ ")

column_names = [cell(0, col)
                for col in range(sheet.ncols)]

with open("wordlist.tsv", "w") as out:
  write = csv.writer(out, dialect="excel-tab").writerow
  write(["ID", "CONCEPT", "DOCULECT", "IPA", "TOKENS"])
  i = 1
  for row in range(1, sheet.nrows):
    concept = cell(row, 0)
    for col in range(2, sheet.ncols):
      lect = cell(0, col)
      for form in cell(row, col).split(","):
        form = form.strip()
        segments = segment(form)
        write([i, concept, lect, form, segments])
        i += 1
