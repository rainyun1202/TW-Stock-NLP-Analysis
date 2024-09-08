rm -rf ./out/*
rm -rf ./out.csv

java -cp "opinion/*.jar:." CopeOpi_trad file_trad.lst -d

