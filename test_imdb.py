from PyMovieDb import IMDB
imdb = IMDB()
res = imdb.get('https://m.imdb.com/title/tt30180830/?ref_=fea_em00059_11_title_sm')
print(res)