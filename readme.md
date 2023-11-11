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
## Note
Because there are two stages: normal and miss. Normal is download apps. The miss phase is to go and download the apps that didn't work in the NORMAL phase, they may be due to timeouts etc.

So the purpose of the apk folder is not to save the apk, but to staging the apk. your correct process should be <p style="color:red">normal->miss->transfer apk file to really staging it!</p>

However, if you could get enough apps such as 90+/100(download apps/offset), miss stage could be skiped.

<p style="color:red">Don't forget after running a round, change the proxy. Offset is 100 is the appropriate number</p>