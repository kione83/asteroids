import random
#import http client
import http.client

#make my own ssl
import ssl 
ssl._create_default_https_context = ssl._create_unverified_context
#make a connection to the API

url = "wordsapiv1.p.rapidapi.com"
conn = http.client.HTTPSConnection(url)
headers = {
    'x-rapidapi-key': "13860b3cfcmsh53f92e505445da2p14f18ejsn56b146dbccdb",
    'x-rapidapi-host': "wordsapiv1.p.rapidapi.com"
}

conn.request("GET", "/words/?random=true&limit=100", headers=headers)
data = conn.getresponse()
read_data = data.read()


#make a list of all the letters
letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

#30 by 30 grid
grid = [[" " for _ in range(40)] for _ in range(40)]

#fill the grid with letters random letters
for i in range(30):
    for j in range(30):
        grid[i][j] = random.choice(letters)

#get 30 random words from the API call above
random_words = []
for i in range(30):
    word = random.choice(read_data.decode("utf-8").split())
        
    #add the word to the list of random words
    if word not in random_words:
        random_words.append(word)

print(f"Word: {word}, Length: {len(word)}")
print(f"Horizontal range: (0, {30 - len(word)})")
print(f"Vertical range: (0, {30 - len(word)})")

#place the words in the grid
# for word in random_words:
#     placed = False
#     while not placed:
#         direction = random.choice(["horizontal", "vertical"])
#         if direction == "horizontal":
#             row = random.randint(0, 29)
#             col = random.randint(0, 30 - len(word))
#             if all(grid[row][col + i] == " " for i in range(len(word))):
#                 for i in range(len(word)):
#                     grid[row][col + i] = word[i]
#                 placed = True
#         else:  # vertical
#             row = random.randint(0, 30 - len(word))
#             col = random.randint(0, 29)
#             if all(grid[row + i][col] == " " for i in range(len(word))):
#                 for i in range(len(word)):
#                     grid[row + i][col] = word[i]
#                 placed = True
# #display the grid
# # for row in grid:
#     # print(" ".join(row))

#create a pdf in the same directory that contains the words
from fpdf import FPDF

#create the file
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
#add the words to the pdf
for word in random_words:
    pdf.cell(200, 10, txt=word, ln=True)
#save the pdf
pdf.output("second/words.pdf")


