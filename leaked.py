from builtins import *

builtglob = list(globals().keys())



from binascii import hexlify
from tokenize import tokenize, untokenize, TokenInfo
from io import BytesIO
from re import findall

from random import choice, shuffle, randint

from zlib import compress





class Hyperion:
    def __init__(self, content: str, clean = True, addbuiltins = True, safemode = True, ultrasafemode = False) -> None:

        # [!!!] Use Safe Modes only if you have errors with your obfuscated script [!!!]

        # clean: Use this if you want to clean the code (compress intendations, remove comments...)
        #
        # [!!!] Be aware that this can cause some bugs [!!!]

        # addbuiltins: Use this to also rename the builtins only if you haven't used the same va
        #
        # [!!!] Be aware that this can cause some bugs [!!!]

        # safemode: Use this if you used positional arguments / predefined arguments in your functions

        # ultrasafemode: Use this to skip the renaming of imports and vars

        self.content = content

        self.add_imports = []

        self.safemode = safemode

        if addbuiltins:
            self.AddBuiltins()


        self.CreateVars()

        if ultrasafemode == False:
            self.RenameImports()
            self.RenameVars()

        self.ObfContent()

        if clean:
            self.CleanCode()

        self.content = '\n'.join(self.add_imports) + '\n' + '\n'.join(self.impcontent) + '\n' + '\n'.join(self.strings) + '\n' + self.content

        self.Compress()



    # Layers

    def AddBuiltins(self):
        imp = "from builtins import " + ','.join(f'{var}' for var in builtglob if not var.startswith('__') and var not in ('None', 'True', 'False') and f'{var}(' in self.content) + '\n'
        if imp == "from builtins import \n":
            imp = ""
        self.content = imp + content

    def CleanCode(self):

        self.RemoveComments()
        self.CompressCode() # Breaks ascii art
        # self.CompressIndentations() # Causes errors sometimes

    def CreateVars(self):

        self.globals = self._randvar()
        self.locals = self._randvar()
        self.vars = self._randvar()

        self.__import__ = self._randvar()

        imports = self._to_import

        impcontent = """
locals()['{0}']=globals
{0}()['{1}']=locals
{1}()['{2}']=__import__
{0}()['{3}']={2}('builtins').vars"""[1:].format(self.globals, self.locals, self.__import__, self.vars, self.unhexlify).splitlines()

        nimpcontent = [f"{self._randglob()}()['{imports[imp]}']={imp}" for imp in imports]
        shuffle(nimpcontent)

        impcontent.extend(iter(nimpcontent))

        self.impcontent = impcontent

    def RenameImports(self):
        _imports = self._gather_imports()
        imports = []
        for imp in _imports:
            imports.extend(iter(imp))
        if '*' in imports:
            raise self.StarImport()
        self.imports = {}
        for imp in imports:
            self.imports[imp] = self._randvar()
        impcontent = [f"{self._randglob()}()['{self.imports[imp]}']={self._randglob()}()['{imp}']" for imp in self.imports]
        shuffle(impcontent)

        self.add_imports = [lin for lin in self.content.splitlines() if self._is_valid(lin)]
        self.content = '\n'.join(lin for lin in self.content.splitlines() if lin not in self.add_imports)
        nimpcontent = list(self.impcontent)
        nimpcontent.extend(iter(impcontent))
        self.impcontent = nimpcontent

    def RenameVars(self):
        f = BytesIO(self.content.encode('utf-8'))
        self.tokens = list(tokenize(f.readline))

        # input('\n'.join(str(tok) for tok in self.tokens))

        strings = {}

        ntokens = []

        passed = []

        for token in self.tokens:
            string, type = token.string, token.type


            if type == 1:
                if (
                    ((self.tokens[self.tokens.index(token)+1].string == '=' and self._is_not_arg(string)) or
                    self.tokens[self.tokens.index(token)-1].string in ('def', 'class')) and
                    self._check_fstring(string) and
                    self._is_not_library(token=token) and
                    string not in passed and
                    string not in self.imports and
                    (not string.startswith('__') and not string.endswith('__'))
                    ):
                    string = self._randvar()
                    strings[token.string] = string
                elif string in strings and self._is_not_library(token=token) and self.tokens[self.tokens.index(token)+1].string != '=':
                    string = strings[string]
                elif string in self.imports and self._is_exact_library(token=token):
                    if ((self.tokens[self.tokens.index(token)+1].string != '=') and
                        self.tokens[self.tokens.index(token)-1].string not in ('def', 'class')):
                        string = self.imports[string]
                else:
                    passed.append(string)

            ntokens.append(TokenInfo(type, string, token.start, token.end, token.line))



        self.content = untokenize(ntokens).decode('utf-8')


    def ObfContent(self):
        f = BytesIO(self.content.encode('utf-8'))
        self.tokens = list(tokenize(f.readline))

        # input('\n'.join(str(tok) for tok in self.tokens))

        self.strings = {}

        ntokens = []

        for token in self.tokens:
            string, type = token.string, token.type

            if type == 1:
                if string in ('True', 'False'):
                    string = self._obf_bool(string)

            elif type == 2:
                string = self._obf_int(string)

            elif type == 3:
                string = self._obf_str(string)

            ntokens.append(TokenInfo(type, string, token.start, token.end, token.line))


        strings = [f"{self.vars}()[{self._protect(var)}]={value}" for var, value in self.strings.items()]

        self.strings = strings

        self.content = untokenize(ntokens).decode('utf-8')



    def Compress(self):

        eval_var = f"globals()['{self._hex('eval')}']"

        arg1, arg2 = self._randvar(), self._randvar()
        lambda1 = f"(lambda {arg1}:{eval_var}({arg1}))"
        lambda2 = f"(lambda {arg1}:{arg1}(__import__('{self._hex('zlib')}')))"
        lambda3 = f"(lambda {arg1}:{arg1}['{self._hex('decompress')}'])"

        lambdas = [lambda1, lambda2, lambda3]

        lambda4 = f"""(lambda {arg2},{arg1}:{arg2}({arg1}))"""
        lambda5 = f"""(lambda:{lambda1}('{self._hex("__import__('builtins').exec")}'))"""

        lambdas2 = [lambda4, lambda5]

        shuffle(lambdas)
        shuffle(lambdas2)

        keys = {lamb: self._randvar() for lamb in lambdas}

        keys2 = {lamb: self._randvar() for lamb in lambdas2}

        decompress = f"{keys[lambda3]}({keys[lambda2]}({keys[lambda1]}('{self._hex('vars')}')))"
        exec_content = f"{keys2[lambda5]}()({keys2[lambda4]}({decompress},{compress(self.content.encode('utf-8'))}))"

        all_keys = keys | keys2

        self.content = 'from builtins import *\n' + ','.join(all_keys.values()) + '=' + ','.join(all_keys.keys()) + '\n' + exec_content





    # Exceptions

    class StarImport(Exception):
        def __init__(self):
            super().__init__("Star Import is forbidden, please update your script")



    # All


    def _hex(self, var):
        return ''.join(f"\\x{hexlify(char.encode('utf-8')).decode('utf-8')}" for char in var)

    def _randvar(self):
        return choice((
            ''.join(choice(('l','I')) for _ in range(20)),
            'O' + ''.join(choice(('O','0')) for _ in range(19))
        ))

    def _randglob(self):
        return choice((
            self.globals,
            self.locals,
            self.vars
        ))

    # CleanCode

    def RemoveComments(self):
        self.content = "".join(lin + '\n' for lin in self.content.splitlines() if lin.strip() and not lin.strip().startswith('#'))

    def CompressCode(self):
        content = self.content
        while True:
            for x in ('=','(',')','[',']','{','}','*','+','-','/',':','<','>',','):
                content = content.replace(f' {x}', x).replace(f'{x} ', x)
            if content == self.content:
                break
            self.content = content

    def CompressIndentations(self):
        l = []

        for lin in self.content.splitlines():
            n = 0
            for x in lin:
                if x == ' ':
                    n += 1
                else:
                    break
            l.append(n)

        nl = []
        for a, b in zip(l, range(len(l))):
            if b == 0:
                nl.append(0 if a == 0 else 1)
                continue
            c = l[b-1]
            if a == 0:
                nl.append(0)
            elif a < c:
                nl.append(nl[b-1]-1)
            elif a > c:
                nl.append(nl[b-1]+1)
            else:
                nl.append(nl[b-1])

        self.content = '\n'.join(' ' * l + lin.lstrip() for lin, l in zip(self.content.splitlines(), nl))


    # CreateVars

    @property
    def _to_import(self):

        self.ord = self._randvar()
        self.chr = self._randvar()
        self.eval = self._randvar()
        self.join = self._randvar()
        self.utf8 = self._randvar()
        self.true = self._randvar()
        self.false = self._randvar()
        self.bool = self._randvar()
        self.str = self._randvar()
        self.float = self._randvar()
        self.unhexlify = self._randvar()
        self.exec = self._randvar()

        imports = {
            'ord': self.ord,
            'chr': self.chr,
            'eval': self.eval,
            "''.join": self.join,
            "'utf8'": self.utf8,
            'True': self.true,
            'False': self.false,
            'bool': self.bool,
            'str': self.str,
            'float': self.float,
            f"{self.__import__}('binascii').unhexlify": self.unhexlify,
            'exec': self.exec
        }
        return imports


    # RenameImports

    def _gather_imports(self):
        imports = [lin for lin in self.content.splitlines() if self._is_valid(lin)]
        return [imp.replace('import ',',').replace('from ', '').replace(' ','').split(',')[1:] if 'from' in imp else imp.replace('import ', '').replace(' ','').split(',') for imp in imports]

    def _is_valid(self, lin: str):
        return ('import' in lin and '"' not in lin and "'" not in lin)

    # RenameVars

    def _is_not_arg(self, string):

        if not self.safemode:
            return True
        funcs = self._gather_funcs
        for lin in self.content.splitlines():
            if string in lin:
                for imp in self.imports.keys():
                    if imp in lin:
                        return False
        return all(string.lower() not in func for func in funcs)

    def _check_fstring(self, string):

        fstrings = findall(r'{[' + self._fstring_legal_chars + r']*}', self.content.lower())
        return all(string.lower() not in fstring for fstring in fstrings)


    def _is_not_library(self, token: str):

        while True:
            if self.tokens[self.tokens.index(token)-1].string == '.':
                token = self.tokens[self.tokens.index(token)-2]
            else:
                break

        return token.string not in self.imports

    def _is_exact_library(self, token: str):
        ntoken = token
        while True:
            if self.tokens[self.tokens.index(token)-1].string == '.':
                token = self.tokens[self.tokens.index(token)-2]
            else:
                break

        return ntoken == token

    @property
    def _gather_funcs(self):
        lins = [lin.strip().split('(')[1] for lin in self.content.splitlines() if lin.strip().split(' ')[0]=='def']
        return lins

    @property
    def _fstring_legal_chars(self):
        return """abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUV_WXYZ0123456789/*-+. ,/():"'"""


    # ObfContent

    def _protect(self, var, force_hex = False):
        r = randint(1, 2)
        if force_hex:
            r = 1
        if r == 1:
            return f"{self.unhexlify}({hexlify(var.encode('utf-8'))}).decode({self.utf8})"
        else:
            return f"'{''.join(reversed(var))}'[::+-+-(-(+1))]"

    def _obf_bool(self, string):
        if string == 'False':
            obf = f'not({self.bool}({self.str}({self.false})))'
        elif string == 'True':
            obf = f'{self.bool}((~{self.false})or({self.true}and{self.false}))'
        string = self._randvar()
        while string in self.strings:
            string = self._randvar()
        self.strings[string] = obf
        return string

    def _obf_int(self, string):
        if string.isdigit():
            obf = self._adv_int(int(string))
        elif string.replace('.','').isdigit():
            obf = f"{self.float}({self._protect(string)})"
        string = self._randvar()
        while string in self.strings:
            string = self._randvar()
        self.strings[string] = obf
        return string

    def _obf_str(self, string):
        obf, do = self._adv_str(string)
        if do:
            string = self._randvar()
            while string in self.strings:
                string = self._randvar()
            self.strings[string] = obf
        else:
            string = obf
        return string

    def _adv_int(self, string):
        n = choice((1, 2))
        if n == 1:
            rnum = randint(1000000,9999999999)
            x = rnum - string
            return f"{self.eval}({self._protect(f'{rnum}-{x}')})"
        elif n == 2:
            rnum = randint(0, string)
            x = string - rnum
            return f"{self.eval}({self._protect(f'{x}+{rnum}')})"

    def _adv_str(self, string):

        var = f"""{self.eval}({self._protect(string, force_hex=True)})"""
        if (string.replace('b','').replace('u','').replace('r','').replace('f','')[0] == '"' and string.split('"')[0].count('f') != 0) or (string.replace('b','').replace('u','').replace('r','').replace('f','')[0] == "'" and string.split("'")[0].count('f') != 0):
            return var, False
        return var, True





file = 'example.py' # nom du fichier a obfusquer
out = 'obf.py' # nom du fichier a créer


# !!! modifiez uniquement si vous avez des erreurs

clean = True
addbuiltins = True
safemode = True
ultrasafemode = False

# [!!!] Use Safe Modes only if you have errors with your obfuscated script [!!!]

# clean: Use this if you want to clean the code (compress intendations, remove comments...)
#
# [!!!] Be aware that this can cause some bugs [!!!]

# addbuiltins: Use this to also rename the builtins only if you haven't used the same va
#
# [!!!] Be aware that this can cause some bugs [!!!]

# safemode: Use this if you used positional arguments / predefined arguments in your functions

# ultrasafemode: Use this to skip the renaming of imports and vars



with open(file, mode='r', encoding='utf-8') as f:
    content = f.read()



hyper = Hyperion(content, clean=clean, addbuiltins=addbuiltins, safemode=safemode, ultrasafemode=ultrasafemode)
obf_content = hyper.content



with open(out, mode='w', encoding='utf-8') as f:
    f.write(obf_content)
