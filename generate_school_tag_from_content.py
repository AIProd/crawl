from io import StringIO
from html.parser import HTMLParser
import pandas as pd
import keyword
import pickle


class MLStripper(HTMLParser):
  def __init__(self):
    super().__init__()
    self.reset()
    self.strict = False
    self.convert_charrefs= True
    self.text = StringIO()
  def handle_data(self, d):
    self.text.write(d)
  def get_data(self):
    return self.text.getvalue()

def strip_tags(html):
  s = MLStripper()
  s.feed(html)
  return s.get_data()

def store_array_as_file(array, file_path):
  with open(file_path, 'wb') as file:
    pickle.dump(array, file)

df = pd.read_excel('1.xlsx', sheet_name='Schools')
school_list = df['name'].tolist()

# iterating using loop
res = []
for sub in school_list:
  print(sub)
  for word in sub.split():
    # check for keyword using iskeyword()
    if keyword.iskeyword(word):
      res.append(word)
 
# printing result
store_array_as_file(res, 'keywords.pkl')
print("Extracted Keywords : " + str(res))

# html_string = "<p>This is <b>bold</b> text.</p>"
# print(strip_tags(html_string))