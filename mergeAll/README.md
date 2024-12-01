# Web Search Engine Project

### Contributors:
- Hoang Tu Huynh
- Nhan Anh Thai 
- Isabel Ganda
- Matthew Alcasabas
- Renard Pascual


### Techniques:
![](https://img.shields.io/badge/Code-MongoDB-informational?style=flat&logo=MongoDb&color=Green)
![](https://img.shields.io/badge/Code-Python-informational?style=flat&logo=python&color=blue)

### How to run this project?

#### Set up the virtual environment:
``` 
python -m venv cs4250 
```
- For Windows User:
``` 
./cs4250/Scripts/activate
```

- For Mac Users:
```
source cs4250/bin/activate
```
#### Download all necessary python packages 
```
pip install -r requirements.txt
```
#### Running the project
##### Craw the target webpage

```
python ./crawler.py
```

##### Parse the target webpage to Mongodb database

```
python ./crawler.py
```

##### Take all the search area to form a completed database with all information of professors

```
python ./search.py
```
