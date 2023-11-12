# APKPure Downloader
## project structuree
1. `app_list` store the app_ids, such as "com.example.myapp". U need create this dir.
2. `log` log dir. U need create this dir
3. `utils` Encapsulation of common methods.
## how to use
1. you show download the correct version of chrome driver.
2. refer to `config_example.py` to set up the correct `config.py`.
3. add an app list file such as `app_list.txt` into `app_list` dir, which format as follows:
```
com.example.appa
com.example.appb
com.example.appc
```
4. run `main.py`. The log will be output in the `log/download.log`.
```sh
python -b 0 -f 100 # app_list[0:100] will use to crawl apps from apkpure

python -m -b 0 -f 100 # will download again to get missed apps
```
## Note
Because there are two stages: normal and miss. Normal is download apps. The miss stage is used to download apps that failed during the normal stage, such as apps that may have failed due to a download timeout, but of course you can skip this stage if you feel that there are enough apps currently downloading.

So the purpose of the `apk` folder is not to save the apk, but to staging the apk. your correct process should be **normal->miss->transfer apk file to really staging it!**

Don't forget to change the proxy after running a round. Offset is 100 is the appropriate number, so `-f` param is not recommended.