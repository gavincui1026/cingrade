from PyMovieDb import IMDB
imdb = IMDB()
res = imdb.get('https://www.imdb.com/title/tt15239678/?ref_=hm_top_tt_i_6')
print(res)