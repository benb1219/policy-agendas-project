# public-laws-scraper
This is a program created under the direction of the Policy Agendas Project. It generates a CSV file automatically populated with data scraped
from the US government's database of public laws. Its chief novelty is its automatic classification scheme. The Policy Agendas Project seeks to
classify political data based on substantive topic area. For this particular project, the researchers were interested in classifying public laws
based on the committees that evaluated them in Congress. Before this program existed, this classification -- or "coding," as they call it -- was
done by hand with a codebook. This program does the coding automatically by reading the PDF of the codebook, grabbing the bill information
(including the committee) from congress.gov, and matching the first committee listed to the code listed in the codebook. While doing that,
it also gathers other information -- such as author, author's party, date passed, etc -- and places them into the columns of a CSV.
