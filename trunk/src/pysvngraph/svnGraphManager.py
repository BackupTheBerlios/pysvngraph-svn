#!/usr/bin/env python
# coding: iso-8859-1

import posixpath

from svnRepository import myset
from svnGraph import svnGraph
from svnRepository import svnRepository
from svnAction import svnAction

from svnHistory import svnHistoryFile as svnHistory
from graphRenderer import graphRendererHTML as graphRenderer
from svnAddendum import svnAddendum
from pyConfiguration import pysvngraphConfiguration as Configuration

# ---------------------------------------- class : svnGraphManager --
# -------------------------------------------------------------------

class svnGraphManager :
    def __init__(self,configurationfile=None) :
        self._configuration = Configuration(file=configurationfile)
        self._configuration.read()

        self._url = None
        self._trunk = None
        self._output = None
        self._rootname = None
        self._filename = None
        self._addendum = None
        self._columns = None

        for attr in ('url','trunk','output','rootname','filename') :
            if getattr(self,'_'+attr) == None and (attr in self._configuration) :
                setattr(self,'_'+attr,self._configuration[attr])

        for attr in ('addendum','columns') :
            if getattr(self,'_'+attr) == None and (attr in self._configuration) :
                setattr(self,'_'+attr,self._configuration[attr].split(','))

        if self._addendum == None :
            self._addendum = []

        if self._rootname == None :
            self._rootname = self._url

        if self._trunk == None and self._rootname != None:
            self._trunk = posixpath.join(self._rootname,'trunk')

        if self._output == None :
            self._output = 'graph-svn'

        self._graphRendererClass = graphRenderer
        print self._configuration
        if 'graphRenderer' in self._configuration :
            if self._configuration['graphRenderer'] == 'Reportlab' :
                from graphRendererReportlab import graphRendererReportlab
                self._graphRendererClass = graphRendererReportlab

        self._svnHistoryClass = svnHistory
        if 'svnHistory' in self._configuration :
            if self._configuration['svnHistory'] == 'pysvn' :
                from svnHistoryPySvn import svnHistoryPySvn
                self._svnHistoryClass = svnHistoryPySvn

        if self._columns and self._trunk not in self._columns :
            self._columns = [self._trunk] + self._columns


    def update_with_addendumevents(self,events) :
        action_added = False
        for event in events :
            if event.eventType() == event.EVENTTYPE_IGNORE :
                if event.revision() != None :
                    self._svnrepository.add_action( svnAction( svnAction.ACTIONTYPE_IGNORE, self._trunk, event.revision() ) )
            elif event.eventType() == event.EVENTTYPE_MERGE :
                action = svnAction(
                        svnAction.ACTIONTYPE_MERGE,
                        event.branch(),
                        event.revision(),
                        branchFrom=event.branchTo(),
                        revisionFrom=event.revisionTo(),
                        branchFromSource=event.branchFrom(),
                        revisionFromSource=event.revisionFrom(),
                        )
                self._svnrepository.add_action(
                    action,
                    )
                action_added = True
        return action_added

    def run(self):
        self._svnhistory = self._svnHistoryClass(self._url,self._filename)
        self._svnrepository = svnRepository(self._url,self._trunk)
        self._graphrenderer = self._graphRendererClass(filename=self._output+self._graphRendererClass.default_extension)

        self._graph = svnGraph(self._svnrepository,self._graphrenderer,self._configuration)

        svnaddendum = svnAddendum()

        for addendumfilename in self._addendum :
            self.update_with_addendumevents(svnaddendum.parse_file(addendumfilename))

        branch_list = myset()
        branch_list.add(self._trunk)

        for x in branch_list :
            print x

        lastbranchecount = len(branch_list)
        for svnrevision in self._svnhistory :
            #print "%s : %s" % (svnrevision.number(),svnrevision)
            r = svnrevision.number()
            #print "%s : " % (r,)
            working_branches = myset()
            action_added = False

            if self.update_with_addendumevents(svnaddendum.parse_text(svnrevision.comment(),r)) :
                action_added = True

            for svnfilechange in svnrevision :
                #print "    %s" % (svnfilechange,)
                fromfile = svnfilechange.fromfile()
                if svnfilechange.change_type() == svnfilechange.CHANGE_TYPE_ADDED :
                    if fromfile != None :
                        if fromfile in branch_list :
                            branch_list.add(svnfilechange.filename())
                            self._svnrepository.add_action( svnAction( svnAction.ACTIONTYPE_CREATION, svnfilechange.filename(), r, svnfilechange.fromfile(), svnfilechange.fromrev() ) )
                            action_added = True
                            print "    %s : %s -> %s" % (r,svnfilechange.fromfile(),svnfilechange.filename())
                    elif svnfilechange.filename() == self._trunk :
                        self._svnrepository.add_action( svnAction( svnAction.ACTIONTYPE_CREATION, svnfilechange.filename(), r ) )
                        action_added = True
                        print "    %s : * %s" % (r,svnfilechange.filename())

            for svnfilechange in svnrevision :
                filename = svnfilechange.filename()
                if filename not in branch_list :
                    for branch in branch_list :
                        if filename[:len(branch)] == branch :
                            if branch not in working_branches :
                                self._svnrepository.add_action( svnAction( svnAction.ACTIONTYPE_WORK, branch, r ) )
                                action_added = True
                                working_branches.add(branch)

            for svnfilechange in svnrevision :
                if (svnfilechange.change_type() == svnfilechange.CHANGE_TYPE_DELETED) :
                    if svnfilechange.filename() in branch_list :
                        #branch_list.remove(svnfilechange.filename())
                        self._svnrepository.add_action( svnAction( svnAction.ACTIONTYPE_DELETE, svnfilechange.filename(), r ) )
                        action_added = True
                        # print "    %s : X %s" % (r,svnfilechange.filename())

            if lastbranchecount != len(branch_list) :
                pass # print "----XxxX(%d)" % (len(branch_list),)
            lastbranchecount = len(branch_list)

            if action_added :
                self._svnrepository.add_info_revision( r, author=svnrevision.author(), date=svnrevision.date() )

        self._svnrepository.resolv()

        if self._columns :
            self._graph.columns(self._columns)
        self._graph.render()

if __name__ == '__main__' :
    from main import main
    main()
