import sys
from os import path as p

class File():

    def __init__(self, path):
        self.path = path
        self.basename = p.basename(path)
        self.name = get_name(self.basename)

class Oto(File):

    def __init__(self, path):
        super().__init__(path)
        self.aliases = {}
        self.names = []
        self.lines = {}
        self.loaded = False
        
        try:
            f = open(self.path, "r")
            self.loaded = True
        except FileNotFoundError:
            try:
                f = open(self.basename, "r")
                self.loaded = True
            except FileNotFoundError:
                self.loaded = False
                return None
            
        for line in f:
            if line != "\n":
                name, alias = get_alias(line)
                if name not in self.names:
                    self.names.append(name)
                self.aliases[alias] = name
                self.lines[alias] = line
        f.close()
        
    def get_partial_oto(self, aliases, options):
        partial_oto = []
        for alias in aliases:
            alias = options.prefix + alias + options.suffix
            partial_oto.append(self.lines[alias])
            try:
                partial_oto.append(self.lines["- " + alias])
            except KeyError:
                pass
        return partial_oto

class Ust(File):

    def __init__(self, path):
        super().__init__(path)
        self.lyrics = []
        f = open(self.path, "r")
        for line in f:
            if line[0:5] == "Lyric":
                lyric = line[6:-1]
                self.lyrics.append(lyric)
        f.close()
        
class Lyrics():
    def __init__(self, usts):
        self.lyrics = []
        self.names = []
        self.wrong_aliases = []
        self.get_lyrics(usts)
        self.lyrics_sort()
        self.kick_rests()
        
    def get_lyrics(self, usts):
        for ust in usts:
            for lyric in ust.lyrics:
                if lyric not in self.lyrics:
                    self.lyrics.append(lyric)
                    
    def lyrics_sort(self):
        self.lyrics.sort()
        sorted = False
        print()
        while not sorted:
            sorted = True
            to_del = [] 
            for i in range(len(self.lyrics)-1):
                if self.lyrics[i] == self.lyrics[i+1]:
                    to_del.append(self.lyrics[i])
                    sorted = False
            for explicit in to_del:
                self.lyrics.pop(self.lyrics.index(explicit))
                print("Found explicit [%s]. Deleted" % explicit)
            
        
    def kick_rests(self):
        if "R"in self.lyrics:
            self.lyrics.remove("R")
            
    def check_VCVs(self):
        cons = "k k' g g' s s' z z' t t' d d' f f' v v' p p' b b' l m n r h l' m' n' r' h' sh sh' zh ts y ch".split(" ")
        for i in range(len(self.lyrics)):
            lyric = self.lyrics[i]
            if  "- " in lyric and lyric.replace("- ","") not in cons:
                self.lyrics[i] = lyric.replace("- ","")
                print("Replaced [%s] with [%s]" % (lyric, self.lyrics[i]))
        self.lyrics_sort()
            
            
            
    def get_names(self, oto, options):
        names = []
        wrong_aliases = []
        for lyric in self.lyrics:
            o_lyric = lyric
            lyric = options.prefix + lyric + options.suffix
            if lyric in oto.aliases.keys():
                if oto.aliases[lyric] not in names:
                    names.append(oto.aliases[lyric])
            else:
                if lyric not in wrong_aliases:
                    wrong_aliases.append(o_lyric)
        names.sort()
        self.names = names
        self.wrong_aliases = wrong_aliases


class Options():

    def __init__(self, dir):
        self.prefix = ""
        self.suffix = ""
        self.isVCVs = False
        
        f = self.open(dir)
        if f: 
            self.read(f)
            f.close()
        self.show()
                
    def open(self, dir):
    
        try:
            f = open(dir+"\\options.ini", "r")
        except FileNotFoundError:
            try:
                f = open("options.ini", "r")
            except FileNotFoundError:
                return False
        return f
        
    def read(self, f):
        for line in f:
            line = line.replace("\n","")
            var, value = line.split("=")
            if var == "prefix":
                self.prefix = value
            if var == "suffix":
                self.suffix = value
            if var == "type" and value == "VCVs":
                self.isVCVs = True
                
    def show(self):
        print("prefix: [%s]" % self.prefix)
        print("suffix: [%s]" % self.suffix)
        print("is VCVs: %s" % self.isVCVs)
        
                
    
    
def get_ext(basename):
    return basename.split(".")[-1]
    
def get_name(basename):
    return "_".join(basename.split(".")[:-1])
    
def get_alias(line):
    
    name, ops = line.split(".wav=")
    alias = ops.split(",")[0]
    return name, alias
    
    
def save_names(names):
    filename = "result\partial reclist (%i).txt" % len(names)
    f = open(filename, "w")
    f.write("\n".join(names))
    
def save_lyrics(lyrics):
    filename = "result\lyrics (%i).txt" % len(lyrics)
    f = open(filename, "w")
    f.write("\n".join(lyrics))
    
def save_oto(oto):
    filename = "result\oto.ini"
    f = open(filename, "w")
    f.write("".join(oto))

def __main__():
    paths = sys.argv[1:]
    dir = p.dirname(sys.argv[0])
    print("Dir: %s" % dir)
    oto = Oto(dir + "\\oto.ini")
    print("Got oto.ini...")
    if not oto.loaded:
        input("Error: no oto.ini")
        return False
        
    got_ust = False
    usts = []
    print("Dropped: ")
    for path in paths:
        print("path")
        if get_ext(p.basename(path)).lower() == "ust":
            if not got_ust:
                got_ust = True
                print("Got UST:")
            usts.append(Ust(path))
            print("\t%s" % usts[-1].name)
    if not got_ust:
        input("Error: got no ust")
        return False
        
    print()    
    options = Options(dir)
    print()
    
    lyrics = Lyrics(usts)
    if options.isVCVs: 
        print("It's VCVs, so let's do something\n")
        lyrics.check_VCVs()
    
    lyrics.get_names(oto, options)
    
    print()
    
    partial_oto = oto.get_partial_oto(lyrics.lyrics, options)
    
    if len(lyrics.names) > 0:
    
        save_names(lyrics.names)
        save_lyrics(lyrics.lyrics)
        save_oto(partial_oto)
        print("Completed")
        print()
        
        if len(lyrics.wrong_aliases) > 0:
            print("Mismatched aliases:")
            print("\n".join(lyrics.wrong_aliases))
        else:
            print("All aliases matched")
            
    else:
    
        input("No matches. Any suffix or prefix? Write it in options.ini and restart")

__main__()