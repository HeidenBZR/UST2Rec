import sys
from os import path as p
import os
from tkinter import messagebox

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
        messagebox.showinfo("info", path)
        self.read_oto(path)
        
    def read_oto(self, path):
        for dir in os.listdir(path) + [""]:
            if os.path.isdir(os.path.join(path, dir)):
                filename = os.path.join(path, dir, "oto.ini")
                print(filename)
                if not os.path.exists(filename):
                    continue
                    
                f = open(filename, "r")
                self.loaded = True
                for line in f:
                    if line != "\n":
                        name, alias = get_alias(line)
                        if name not in self.names:
                            self.names.append(name)
                        self.aliases[alias] = name
                        self.lines[alias] = line
                f.close()
        
    def get_partial_oto(self, aliases):
        partial_oto = []
        for alias in aliases:
            partial_oto.append(self.lines[alias])
            # if "- " + alias in self.lines:
                # partial_oto.append(self.lines["- " + alias])
        return partial_oto

class Ust(File):

    def __init__(self, path):
        super().__init__(path)
        self.lyrics = []
        f = open(self.path, "r")
        for line in f:
            if line.startswith("VoiceDir="):
                self.VoiceDir = line[len("VoiceDir="):-1]
            if line.startswith("@alias="):
                lyric = line[len("@alias="):-1]
                self.lyrics.append(lyric)
        f.close()
        
        
class Lyrics():
    def __init__(self, ust):
        self.lyrics = []
        self.names = []
        self.wrong_aliases = []
        self.get_lyrics(ust)
        self.lyrics_sort()
        self.kick_rests()
        
    def get_lyrics(self, ust):
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
            
            
    def get_names(self, oto):
        names = []
        wrong_aliases = []
        for lyric in self.lyrics:
            o_lyric = lyric
            if lyric in oto.aliases.keys():
                if oto.aliases[lyric] not in names:
                    names.append(oto.aliases[lyric])
            else:
                if lyric not in wrong_aliases:
                    wrong_aliases.append(o_lyric)
        names.sort()
        self.names = names
        self.wrong_aliases = wrong_aliases


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
    
def save_wrong_aliases(names):
    filename = "result\wrong aliases (%i).txt" % len(names)
    f = open(filename, "w")
    f.write("\n".join(names))
    
def save_oto(oto):
    filename = "result\oto.ini"
    f = open(filename, "w")
    f.write("".join(oto))

def __main__():
    global ust;

    try:
        path = sys.argv[1]
        # messagebox.showinfo("got file", sys.argv[1])
        print("Dir: %s" % path)
            
        got_ust = False
        if get_ext(p.basename(path)).lower() == "tmp":
            if not got_ust:
                got_ust = True
                print("Got UST:")
            ust = Ust(path)
            print("\t%s" % ust.name)
        if not got_ust:
            messagebox.showerror("error", "Error: got no ust")
            return False
            
        oto = Oto(ust.VoiceDir)
        if not oto.loaded:
            messagebox.showerror("error", "Error: no oto.ini")
            return False
            
        lyrics = Lyrics(ust)
        
        lyrics.get_names(oto)
        
        print()
        
        partial_oto = oto.get_partial_oto(lyrics.lyrics)
        
        if len(lyrics.names) > 0:
        
            save_names(lyrics.names)
            save_lyrics(lyrics.lyrics)
            save_oto(partial_oto)
            print("Completed")
            print()
            
            if len(lyrics.wrong_aliases) > 0:
                print("Mismatched aliases:")
                print("\n".join(lyrics.wrong_aliases))
                save_wrong_aliases(lyrics.wrong_aliases)
            else:
                print("All aliases matched")
                
        else:
        
            messagebox.showwarning("warning", "no matches; something is wrong")
            print("No matches")
            
        messagebox.showinfo("success", "result saved on %s" % os.path.abspath("result"))
    except Exception as inst:
        message = "%s \n" % type(inst)
        message += "%s \n" % ", ".join(inst.args)
        messagebox.showerror("error", message)
__main__()