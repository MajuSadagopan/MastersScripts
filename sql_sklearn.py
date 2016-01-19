import word_grid_obj as wg

#Global Variables
database = 'region_waterloo'
user = 'postgres'
password ='love2Learn'
host = 'localhost'
port = '5433'

#DB Variables
word_output_table = 'iht_word_comboy3'
table_name = 'iht_trained_survey'
text_column = 'comment'
category = 'match_tabl'


#SQL QUERIES
tsvector_query="select gid, to_tsvector('simple',"+text_column+"),"+category+", "+text_column+" from "+table_name+" where "+category+" is not Null"
tstat_query="select array_agg(word) from ts_stat('"+"select to_tsvector(''simple'', "+text_column+") from "+table_name+"')"


wgrid = wg.wordgrid(database,user,password,host,port)
vectors = wgrid.db_query(tsvector_query)
vector_group = wgrid.tsv_dict(vectors,1)


wgrid.keywords2postgres(word_output_table)
