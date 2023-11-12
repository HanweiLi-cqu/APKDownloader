from androguard.core.bytecodes import apk
from androguard.core.androconf import show_logging
show_logging(level="ERROR")
    
class AndroguardParse:
    def __init__(self,file) -> None:
        self.file = file
        self.apk = None
    
    def get_package(self):
        if self.file.endswith(".apk"):
            if self.apk is None:
                try:
                    self.apk = apk.APK(self.file)
                except Exception as e:
                    return None
            return self.apk.get_package()
        else:
            return None

    def get_premission(self):
        if self.apk is None:
            self.apk = apk.APK(self.file)
        return self.apk.get_permissions()

