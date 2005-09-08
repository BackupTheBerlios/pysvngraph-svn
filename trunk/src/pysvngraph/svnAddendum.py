#!/usr/bin/env python
# coding: iso-8859-1

# --------------------------------------- class : svnAddendumEvent --
# -------------------------------------------------------------------

class svnAddendumEvent :
    EVENTTYPE_IGNORE = 0
    EVENTTYPE_MERGE = 1
    def __init__( self, eventType=None, revision=None, branch=None, branchFrom=None, revisionFrom=None, branchTo=None, revisionTo=None ) :
        self._eventType    = eventType
        self._revision     = revision
        self._branch       = branch
        self._branchFrom   = branchFrom
        self._revisionFrom = revisionFrom
        self._branchTo     = branchTo
        self._revisionTo   = revisionTo
    def eventType    (self) : return self._eventType
    def revision     (self) : return self._revision
    def branch       (self) : return self._branch
    def branchFrom   (self) : return self._branchFrom
    def revisionFrom (self) : return self._revisionFrom
    def branchTo     (self) : return self._branchTo
    def revisionTo   (self) : return self._revisionTo

# -------------------------------------------- class : svnAddendum --
# -------------------------------------------------------------------

class svnAddendum :
    EVENTTYPE_IGNORE = svnAddendumEvent.EVENTTYPE_IGNORE
    EVENTTYPE_MERGE = svnAddendumEvent.EVENTTYPE_MERGE
    def __init__( self ) :
        pass

    def parse_addendum_tag( self, line, revision=None ):
        event = None

        # This method can return BEFORE the end of the method

        while len(line)>0 and line[-1] in ('\r','\n'):
            line = line[:-1]

        if len(line)<=0 :
            return None

        subtag = line

        if line[0] == 'r' :
            parts = line.split(':',1)
            if len(parts) != 2 :
                return None
            subtag = parts[1]
            try :
                revision = int(parts[0][1:])
            except ValueError :
                return None

        if len(subtag)<=0 :
            return None
        if subtag[0]!='<' or subtag[-1]!='>' :
            return None
        tagelements = subtag[1:-1].split('|')
        if len(tagelements) <= 0 :
            return None

        if tagelements[0] == 'IGNORE' :
            event = svnAddendumEvent(eventType=svnAddendumEvent.EVENTTYPE_IGNORE,revision=revision)
        elif tagelements[0] == 'MERGE' :
            if len(tagelements) != 3 :
                return None
            branch = tagelements[1]
            if len(tagelements[2]) < 1 :
                return None
            if tagelements[2][0] != '[' or tagelements[2][-1] != ']' :
                return None
            try :
                (fromelement,toelement) = tagelements[2][1:-1].split(']->[',1)
            except ValueError :
                return None
            #frompair = fromelement.rsplit(':',1)
            #topair = toelement.rsplit(':',1)

            frompos = fromelement.rfind(':')
            topos = toelement.rfind(':')
            
            if (frompos<0) or (topos<0) :
                return None

            try :
                branchFrom = fromelement[:frompos]
                branchTo = toelement[:topos]
                revisionFrom = int(fromelement[frompos+1:])
                revisionTo = int(toelement[topos+1:])
            except ValueError :
                return None

            event = svnAddendumEvent(
                eventType=svnAddendumEvent.EVENTTYPE_MERGE,
                revision=revision,
                branch=branch,
                branchFrom=branchFrom,
                revisionFrom=revisionFrom,
                branchTo=branchTo,
                revisionTo=revisionTo,
                )
        else :
            return None

        return event

    def parse_text( self, text, revision=None ):
        events = []

        for line in text.split('\n') :
            event = self.parse_addendum_tag(line,revision)
            if event :
                events.append(event)

        return events

    def parse_file( self, filename ):
        events = []

        handle = open(filename,'rt')
        for line in handle :
            event = self.parse_addendum_tag(line)
            if event :
                events.append(event)
        handle.close()

        return events


if __name__ == '__main__' :
    from main import main
    main()