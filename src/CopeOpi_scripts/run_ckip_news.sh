rm -rf ./out/*
rm -rf ./out.csv

java -cp "opinion/*.jar:." CopeOpi_trad ckip_to_cope_list.lst -d

