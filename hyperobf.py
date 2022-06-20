import requests, sys, os, shutil
try: import pyinstaller
except: os.system('pip install -q pyinstaller')

class Obfuscator:
    def __init__(self, clean, addbuiltins, shell, safemode, ultrasafemode):
        self.addbuiltins   = addbuiltins
        self.clean         = clean
        self.shell         = shell
        self.safemode      = safemode
        self.ultrasafemode = ultrasafemode
        
    def get_data(self):
        file_path = input('Drop File Here > ')
        
        try:
            data = open(file_path, 'r').read()
        except FileNotFoundError:
            sys.exit('File not found')

        return data, file_path

    def obfuscate(self, data):

        req = requests.post(
                url ='https://api.plague.fun/',
                params = {
                    'clean': self.clean,
                    'addbuiltins': self.addbuiltins,
                    'shell': self.shell,
                    'safemode': self.safemode,
                    'ultrasafemode': self.addbuiltins
                },
                headers = {
                    'origin': 'https://obf.plague.fun',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
                }, 
                data = data
            )

        if 'You are a skid' in req.text:
            print('[ x ] You are ratelimited lmao, use vpn')
        else:
            print(' [ * ] hyperobfuscated successfully')
            with open('hyperobf.py', 'a') as _:
                _.write(req.text)


class Exefy:
    def __init__(self, path, icon, name):
        self.name = name
        self.icon = icon
        self.path = path

    def to_exe(self):
        os.system(f'pyinstaller --noconfirm --onefile --console --icon "{self.icon}" --name "{self.name}"  "{self.path}"')
        shutil.rmtree('build')
        for file in next(os.walk(os.getcwd()), (None, None, []))[2]:
            if file[-1] == "c":
                os.remove(file)
        try:
            os.replace(f"dist/{self.name}.exe", f"./{self.name}.exe")
            shutil.rmtree('dist')
        except:
            pass
        print(' [ * ] exefied successfully')


if __name__ == '__main__':
    obf = Obfuscator(
        clean         = True,
        addbuiltins   = True,
        shell         = True,
        safemode      = True,
        ultrasafemode = False, #use this only if you have errors !!
    )

    data, file_path = obf.get_data()
    obf.obfuscate(data)
    
    input('Add imports to obfuscated file before turning it into an .exe')

    exefy = Exefy(
        path = file_path,
        icon = None, #if yes, include icon file path
        name = 'obf' 
    )
    exefy.to_exe()
    
