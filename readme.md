# APKPure Downloader
## project structuree
1. `app_list` store the app_ids, such as "com.example.myapp"
2. `log` log dir
3. `utils` Encapsulation of common methods.
## how to use
1. you show download chrome driver with correct version.
2. set right config params refer `config_example.py`
3. add an app list file into `app_list` dir, which format as follows:
```
com.example.appa
com.example.appb
com.example.appc
```
4. run `main.py`. And log will appear in `log/download.log`.
```sh
python -b 0 -f 100 # app_list[0:100] will use to crawl apps from apkpure

python -m -b 0 -f 100 # will download again to get missed apps
```
Because there are two stages: normal and miss.
