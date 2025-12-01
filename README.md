# Project Structure


This project was created by:
- Abel Jozsef Szemler (absz@itu.dk)
- Benjamin Storm Larsen (bsla@itu.dk)
- Florentina Fabregas Alippi (flfa@itu.dk)
- Miina Johanna Mäkinen (miin@itu.dk)
- Raivis Lickrastins (rail@itu.dk)


## Scraping
The scraper is built with GoLang and is found in the `scraper/` directory. To run it you need to have Go installed on your machine and the `awscli` configured with your AWS credentials, and update the S3 bucket name and region in the `main.go` file. To run it simply use the command:
```bash
go run main.go
```
or build it with (MacOS/Linux):
```bash
go build -o scraper main.go
chmod +x scraper
./scraper
```
<!-- 

```text
wild-data/
├── src/    
│   └── <python scripts>   # build_csv.py
│
├── data/
│   ├── august/
│   │   └── raw/   # here the json files for the period of 1-21 august
│   │   └── combined_output.csv 
│   │   └── .gitignore
└── README.md
 -->


