#!/usr/bin/env python
# coding: iso-8859-1

from svnGraphManager import svnGraphManager
from pyConfiguration import pysvngraphConfiguration as Configuration

def main() :
    import sys

    configfile = None
    use_graphmanager = True
    use_dumpconfig = False

    # Yes, yes, it's an ugly command line parsing. It need total rewritting

    output = None
    if len(sys.argv)>1 :
        configfile = sys.argv[1]
        if configfile == '--dumpconfig' :
            if len(sys.argv)>2 :
                configfile = sys.argv[2]
                if len(sys.argv)>3 :
                    output = sys.argv[3]
            else :
                configfile = None
            use_graphmanager = False
            use_dumpconfig = True

    try :
        if use_graphmanager :
            svnGraphManager(configfile).run()
        elif use_dumpconfig :
            old_sys_stdout = sys.stdout
            if output :
                sys.stdout = file(output,'wt')
            configuration = Configuration(configfile)
            configuration.read()
            print configuration
            if output :
                sys.stdout.close()
            sys.stdout = old_sys_stdout            
    except :
        exc_info = sys.exc_info()
        track = exc_info[2]
        print "** Error"
        while track :
            print "    File %s, line %d, in %s" % (track.tb_frame.f_code.co_filename,track.tb_lineno,track.tb_frame.f_code.co_name)
            track = track.tb_next
        print "  ** %s (%s)" % ( exc_info[1], exc_info[0].__name__ )
        print "  <PRESS RETURN>"
        sys.stdin.readline()

if __name__ == '__main__' :
    main()
