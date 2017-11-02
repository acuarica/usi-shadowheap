#!/usr/bin/python

import sys
import collections
import glob
import os
import subprocess
import traceback
import pprint

class Graph:
    
    class GraphNode:
        def __init__(self):
            self.edges = {}
            self.backedges = {}
            
    def __init__(self):
        self._nodes = {}
        self._roots = set()
    
    def __len__(self):
        return len(self._nodes)
    
    def _putnode(self, node):
        if not node in self._nodes:
            self._nodes[node] = Graph.GraphNode()
            self._roots.add(node)
    
    def numberofedges(self):
        count = 0
        for node, graphnode in self._nodes.iteritems():
            count += len(graphnode.edges)
            
        return count

    def putEdge(self, source, target, label):
        assert source != None, 'Source cannot be None'
        # assert target != None, 'Target cannot be None'
        
        Graph._putnode(self, source)
        Graph._putnode(self, target)
        
        self._nodes[source].edges[label] = target
        self._nodes[target].backedges[label] = source
        
        if target in self._roots:
            self._roots.remove(target)
        
    def nodes(self):
        return self._nodes.iterkeys()
    
    def edges(self, sourceNode):
        return self._nodes[sourceNode].edges.iteritems()
    
    def edgescount(self, sourcenode):
        return len(self._nodes[sourcenode].edges)
    
    def haslabel(self, node, label):
        return label in self._nodes[node].edges

    def edge(self, node, label):
        return self._nodes[node].edges[label]
    
    def backedges(self, targetNode):
        return self._nodes[targetNode].backedges.iteritems()

    def roots(self):
        return self._roots
        
    def edgedif(self, other):
        result = Graph()
        
        for snode, sgraphnode in self._nodes.iteritems():
            ographnode = other._nodes.get(snode)
            if ographnode != None:
                for label, tnode in sgraphnode.edges.iteritems():
                    rtnode = ographnode.edges.get(label)
                    if rtnode != None:
                        if tnode != rtnode:
                            result.putEdge(snode, (tnode, rtnode), label)
                            # result.putEdge(snode, tnode, 'L-' + str(label))
                            # result.putEdge(snode, rtnode, 'R-' + str(label))
            
        return result
    
    def commonnodecount(self, other):
        count = 0
        
        for snode, sgraphnode in self._nodes.iteritems():
            ographnode = other._nodes.get(snode)
            if ographnode != None:
                count += 1

        return count

    def prunestrings(self):
        result = Graph()
        
        for sourceNode in self.nodes():
            if not isinstance(sourceNode, HeapString):
                for label, targetNode in self.edges(sourceNode):
                    if not isinstance(targetNode, HeapString):
                        result.putEdge(sourceNode, targetNode, label)
            
        return result

    def prunefromroots(graph, maxdistance, maxroots, maxedgespernode):
        def visitNode(sourceNode, graph, visited, distance, maxdistance, result, maxedgespernode):
            if distance >= maxdistance:
                return
        
            if sourceNode not in visited:
                visited.add(sourceNode)
                
                i = 0
                for label, targetNode in graph.edges(sourceNode):
                    
                    if i >= maxedgespernode:
                        break
                    
                    i += 1
                    
                    result.putEdge(sourceNode, targetNode, label)
                    
                    visitNode(targetNode, graph, visited, distance + 1, maxdistance, result, maxedgespernode)
                    
        result = Graph()
        
        visited = set()
        
        i = 0
        for root in graph.roots():
            visitNode(root, graph, visited, 0, maxdistance, result, maxedgespernode)
            
            i += 1
            
            if i >= maxroots:
                break
            
        return result
    
    def write(self, filename):
        file = open(filename, 'w')
        
        # file.write('Graph \n')
        # gv.write('  graph [ rankdir=LR ];\n')
        # gv.write('  node [shape=record]\n')

        for snode in self.nodes():
            file.write('Node %s\n' % str(snode))
            for label, tnode in self.edges(snode):
                file.write('  %s -> %r\n' % (label, tnode))
        
        file.close()

class Stamp():
    _TYPE_CLASS = 0
    _TYPE_OBJECT = 1
    
    _TYPE_BITS = 1
    _THREAD_BITS = 8
    _CLASS_BITS = 19
    _OBJECT_BITS = 36

    _TYPE_MASK = ((1L << _TYPE_BITS) - 1)
    _THREAD_MASK = ((1L << _THREAD_BITS) - 1)
    _CLASS_MASK = ((1L << _CLASS_BITS) - 1)
    _OBJECT_MASK = ((1L << _OBJECT_BITS) - 1)

    _OBJECT_POS = (0)
    _CLASS_POS = (_OBJECT_POS + _OBJECT_BITS)
    _THREAD_POS = (_CLASS_POS + _CLASS_BITS)
    _TYPE_POS = (_THREAD_POS + _THREAD_BITS)
    
    _TYPE_DESC = [ 'CLASS', 'OBJECT' ]
    
    def __init__(self, value):
        assert isinstance(value, long), 'Stamp value %r must be of type long' % value
        assert value != 0L, 'Stamp value zero (%r) is invalid for stamp' % value
        
        self.value = value

        self.type = (value >> Stamp._TYPE_POS) & Stamp._TYPE_MASK
        self.threadid = (value >> Stamp._THREAD_POS) & Stamp._THREAD_MASK
        self.classid = (value >> Stamp._CLASS_POS) & Stamp._CLASS_MASK
        self.objectid = (value >> Stamp._OBJECT_POS) & Stamp._OBJECT_MASK
        
        self.isclass = self.type == Stamp._TYPE_CLASS
        self.isobject = self.type == Stamp._TYPE_OBJECT
        
        self.typedesc = Stamp._TYPE_DESC[self.type]

    def __eq__(self, other):
        return isinstance(other, Stamp) and self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return  31 + (self.value ^ (self.value >> 32));
 
    def __str__(self):
        return '{%s.%s.%s.%s@%s}' % (self.typedesc, self.threadid, self.classid, self.objectid, self.value) 
    
    def __repr__(self):
        return self.__str__()

class HeapObject(object):
    def __init__(self, stamp, heapclass):
        assert stamp != None
        assert isinstance(stamp, Stamp), 'Stamp %r must be of type Stamp' % stamp
        
        self.stamp = stamp
        self.heapclass = heapclass
        
        self.values = collections.defaultdict(list)
    
    def putvalue(self, key, value):
        self.values[key].insert(0, value)

    def __eq__(self, other):
        return isinstance(other, HeapObject) and self.stamp == other.stamp
        # return self.stamp == other.stamp and ((self.heapclass == None and other.heapclass == None) or (self.heapclass == other.heapclass))

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return  hash(self.stamp.value)
        # return  31 + (self.stamp.value ^ (self.stamp.value >> 32))

    def __str__(self):
        classdesc = self.heapclass.name if self.heapclass else "<missing>"  
        return '%s:%s|%s' % (self.stamp, classdesc, self.values)
    
    """ To avoid circular references"""
    def __repr__(self):
        classdesc = self.heapclass.name if self.heapclass else "<missing>"  
        return '%s:%s' % (self.stamp, classdesc)

class HeapClass(HeapObject):
    
    def __init__(self, classstamp, classname, superclass):
        HeapObject.__init__(self, classstamp, None)

        assert isinstance(superclass, HeapClass) or superclass == None
        
        self.name = classname
        self.superClass = superclass
        self._fields = None
        self._fieldsbyname = set()

    def prepare(self):
        assert self._fields == None, 'Unknown state of field in class %s' % self
        
        self._fields = []
        
        if self.superClass != None:
            self._appendfields(self.superClass)
    
    # def putinterface(self, heapinter):
    #    self._appendfields(interclass)
        
    def _appendfields(self, heapclass):
        for field in heapclass._fields:
            fieldname = field[0]
            fieldtype = field[1]
            
            self.putfield(fieldname, fieldtype)
        
    def putfield(self, fieldname, fieldtype):
        assert self._fields != None, 'Class not prepared %s' % self
        
        if fieldname in self._fieldsbyname:
            pass
            # print >> sys.stderr, 'Field %s already present in class %s %s' % (fieldname, self.name, self._fieldsbyname)
            
        self._fieldsbyname.add(fieldname)
        
        self._fields.append((fieldname, fieldtype))
    
    def getfield(self, index):
        assert isinstance(index, long)
        assert self._fields != None, 'Class not prepared %s' % self
        # assert self.existsfield(index), 'Index %d not %s with fields #%s %s' % (index, self, len(self._fields), self._fields)
        
        # TODO: Implement field interfaces
        if self.existsfield(index):
            return self._fields[index]
        else:
            return ('fieldunknown?', 'class unknown?')

    def existsfield(self, index):
        assert self._fields != None, 'Class not prepared %s' % self
        return index < len(self._fields) and index >= 0
    
    # TODO: implement eq for heapclass 
    # def __eq__(self, other):
    #    return HeapObject.__eq__(self, other) and self.name == other.name

    def __str__(self):
        return '%s(%s):Class' % (self.name, self.stamp)

class HeapString(HeapObject):
    def __init__(self, stamp):
        HeapObject.__init__(self, stamp, None)
        
    def __str__(self):
        return '%s:String' % (self.stamp)

class HeapClassTable:
    def __init__(self):
        self._classesbystamp = {}
        self._classesbyid = {}

    def putclass(self, heapclass):
        assert isinstance(heapclass, HeapClass)
        
        self._classesbystamp[heapclass.stamp] = heapclass
        self._classesbyid[heapclass.stamp.classid] = heapclass
        
    def getclassbystamp(self, classstamp):
        assert isinstance(classstamp, Stamp), 'The classstamp %r is not a Stamp' % classstamp
        assert classstamp in self._classesbystamp, 'The classstamp %r is not present' % classstamp

        return self._classesbystamp[classstamp]
        
    def getclassbyobjectstamp(self, objectstamp):
        assert isinstance(objectstamp, Stamp), 'The objectstamp %r is not a Stamp' % objectstamp
        assert objectstamp.classid in self._classesbyid, 'The classid %r for stamp %s is not present' % (objectstamp.classid, objectstamp)
        
        return self._classesbyid[objectstamp.classid]
    
    def hasstamp(self, classstamp):
        assert isinstance(classstamp, Stamp), 'The classstamp %r is not a Stamp' % classstamp

        return classstamp in self._classesbystamp

class ClassesLoader:
    def __init__(self):
        pass
 
    def loadclasses(self, classfilenames):
        rawdata = {}
        
        for classfilename in classfilenames:
            rawklass = ClassesLoader._parseclass(classfilename)
            rawdata[rawklass['classstamp']] = rawklass

        return ClassesLoader._loadjavaclasses(rawdata)

    @staticmethod
    def _loadjavaclasses(rawdata):
        heapclasstable = HeapClassTable()
        
        for classstamp, klass in rawdata.iteritems():
            if not heapclasstable.hasstamp(classstamp):
                ClassesLoader._loadjavaclass(rawdata, heapclasstable, classstamp, klass)
    
        return heapclasstable

    @staticmethod
    def _loadjavaclass(rawdata, heapclasstable, stamp, rawclass):
        assert(stamp == rawclass['classstamp'])
        
        classStamp = rawclass['classstamp']
        classId = rawclass['classid']
        classname = rawclass['classname']
        superClassStamp = rawclass['superclassstamp']
        
        if superClassStamp == None:
            klass = HeapClass(classStamp, classname, None)
        else:
            if not heapclasstable.hasstamp(superClassStamp):
                ClassesLoader._loadjavaclass(rawdata, heapclasstable, superClassStamp, rawdata[superClassStamp])
            
            superclass = heapclasstable.getclassbystamp(superClassStamp)
            klass = HeapClass(classStamp, classname, superclass)
        
            for field in superclass._fields:
                fieldname = field[0]
                fieldtype = field[1]
                klass.putfield(fieldname, fieldtype)
        
        for field in rawclass['fields']:
            fieldname = field[0]
            fieldtype = field[1]
            klass.putfield(fieldname, fieldtype)
    
        
        # sig = 'L' + classname + ';'
        # if sig not in cls:
            
         
        heapclasstable.putclass(klass)

    @staticmethod
    def _parseclass(classfilename):    
        file = open(classfilename)
    
        header = collections.deque([ s.strip() for s in file.readline().split(':') ])
    
        klass = {}
        
        klass['classstamp'] = Stamp(long(header.popleft()))
        klass['classid'] = Stamp(long(header.popleft()))
        klass['classname'] = header.popleft()
        
        value = long(header.popleft())
        klass['superclassstamp'] = None if value == -1 else Stamp(value) 
        
        fields = []
        if len(header) == 0:
            print >> sys.stderr, 'Warning:', klass['classname'], 'does not have fields definition' 
        else:
            fieldCount = int(header.popleft())
        
            i = 0
            while i < fieldCount:
                field = collections.deque([ s.strip() for s in file.readline().split(':') ])
                
                # index = field[0].strip()
                fieldName = field[1]
                fieldType = field[2]
                
                fields.append((fieldName, fieldType))
                
                i += 1
    
        klass['fields'] = fields
        
        return klass

class FollowReferencesVisitor:
    def __init__(self, heapclasstable):
        self.graph = Graph()
        self.heapclasstable = heapclasstable
        self.data = None
            
    def putroot(self, source, targetstamp, targetclassstamp):
        target = self.get(targetstamp, targetclassstamp)
        refno = self.graph.edgescount(source) if source in self.graph.nodes() else 0
        label = 'ref%d' % (refno)
        self.put(source, target, label)
        
        return target

    def visit_jniglobal(self, targetstamp, targetclassstamp):
        self.putroot('JNI GLOBAL', targetstamp, targetclassstamp)

    def visit_systemclass(self, targetstamp, targetclassstamp):
        # assert Stamp(targetstamp).isclass

        self.putroot('SYSTEM CLASS', targetstamp, targetclassstamp)
        
    def visit_monitor(self, targetstamp, targetclassstamp):
        self.putroot('MONITOR', targetstamp, targetclassstamp)

    def visit_stacklocal(self, threadstamp, threadid, depth, location, slot, targetstamp, targetclassstamp):
        self.putroot('STACK LOCAL', targetstamp, targetclassstamp)

    def visit_jnilocal(self, threadstamp, threadid, depth, targetstamp, targetclassstamp):
        self.putroot('JNI LOCAL', targetstamp, targetclassstamp)

    def visit_thread(self, targetstamp, targetclassstamp):
        self.putroot('THREAD', targetstamp, targetclassstamp)

    def visit_other(self, targetstamp, targetclassstamp):
        self.putroot('OTHER', targetstamp, targetclassstamp)
    
    def putst(self, sourcestamp, sourceclassstamp, targetstamp, targetclassstamp, label):
        source = self.get(sourcestamp, sourceclassstamp)
        target = self.get(targetstamp, targetclassstamp)
        
        self.put(source, target, label)
        
    def visit_field(self, refinfo, sourcestamp, sourceclassstamp, targetstamp, targetclassstamp):
        source = self.get(sourcestamp, sourceclassstamp)
        self.get(targetstamp, targetclassstamp)
        
        if source != None:
            assert source.heapclass != None, '%s' % source
            label = 'FIELD$' + source.heapclass.getfield(refinfo)[0]
            self.putst(sourcestamp, sourceclassstamp, targetstamp, targetclassstamp, label)
        
    def visit_staticfield(self, refinfo, sourcestamp, sourceclassstamp, targetstamp, targetclassstamp):
        assert sourcestamp == 0L or Stamp(sourcestamp).isclass

        source = self.get(sourcestamp, sourceclassstamp)
        self.get(targetstamp, targetclassstamp)

        if source != None:
            assert isinstance(source, HeapClass), '%s' % source
            label = 'FIELD$' + source.getfield(refinfo)[0]
            self.putst(sourcestamp, sourceclassstamp, targetstamp, targetclassstamp, label)


    def visit_arrayelement(self, refinfo, sourcestamp, sourceclassstamp, targetstamp, targetclassstamp):
        self.get(sourcestamp, sourceclassstamp)
        self.get(targetstamp, targetclassstamp)
        
        label = refinfo
        
        self.putst(sourcestamp, sourceclassstamp, targetstamp, targetclassstamp, label)
        
    def visit_constantpool(self, refinfo, sourcestamp, sourceclassstamp, targetstamp, targetclassstamp):
        self.get(sourcestamp, sourceclassstamp)
        self.get(targetstamp, targetclassstamp)
        
        assert Stamp(sourcestamp).isclass

    def visit_class(self, sourcestamp, sourceclassstamp, targetstamp, targetclassstamp):
        self.get(sourcestamp, sourceclassstamp)
        self.get(targetstamp, targetclassstamp)
        
        assert targetstamp == 0L or Stamp(targetstamp).isclass
        
    def visit_superclass(self, sourcestamp, sourceclassstamp, targetstamp, targetclassstamp):
        self.get(sourcestamp, sourceclassstamp)
        self.get(targetstamp, targetclassstamp)

        assert sourcestamp == 0L or Stamp(sourcestamp).isclass
        assert targetstamp == 0L or Stamp(targetstamp).isclass
    
    def visit_interface(self, sourcestamp, sourceclassstamp, targetstamp, targetclassstamp):
        # label = 'INTERFACE%d' % self.graph.edgescount(source)
        self.get(sourcestamp, sourceclassstamp)
        self.get(targetstamp, targetclassstamp)
        assert sourcestamp == 0L or Stamp(sourcestamp).isclass
        assert targetstamp == 0L or Stamp(targetstamp).isclass

    def visit_classloader(self, sourcestamp, sourceclassstamp, targetstamp, targetclassstamp):
        self.get(sourcestamp, sourceclassstamp)
        self.get(targetstamp, targetclassstamp)
        
    def visit_signers(self, sourcestamp, sourceclassstamp, targetstamp, targetclassstamp):
        self.get(sourcestamp, sourceclassstamp)
        self.get(targetstamp, targetclassstamp)
        
    def visit_protectiondomain(self, sourcestamp, sourceclassstamp, targetstamp, targetclassstamp):
        self.get(sourcestamp, sourceclassstamp)
        self.get(targetstamp, targetclassstamp)

    def get(self, stamp, classstamp):
        if classstamp == 0L:
            return None
        
        classstamp = Stamp(classstamp)
        
        assert classstamp.isclass, 'Stamp %r is not a class stamp' % classstamp
        
        heapclass = self.heapclasstable.getclassbystamp(classstamp)
        
        if stamp == 0L:
            if heapclass.name not in ['[C', 'Ljava/lang/String;']:
                # print >> sys.stderr, 'Warning: object not stamped', stamp, 'of class', heapclass, '@', self.data
                pass
            
            return None
        
        stamp = Stamp(stamp)
        assert not stamp.isobject or stamp.classid == classstamp.classid, '%s %s' % (stamp, classstamp)
        assert stamp.threadid != 0L
   
        if heapclass.name == "Ljava/lang/Class;":
            if self.heapclasstable.hasstamp(stamp):
                return self.heapclasstable.getclassbystamp(stamp)
            else:
                return HeapObject(stamp, heapclass)
        # elif heapclass.name == "Ljava/lang/String;":
        #    return HeapString(stamp)
        else:
            return HeapObject(stamp, heapclass)
        
    def put(self, source, target, label):
        if source != None and target != None:
            self.graph.putEdge(source, target, label)
        
class ParserException(Exception):
    def __init__(self, lineno, line, tb):
        self._lineno = lineno
        self._line = line
        self._tb = tb

    def __str__(self):
        return ('Error on line no. %s: %s\n' % (self._lineno, self._line)) + self._tb

class FollowReferencesParser():
    def __init__(self):
        pass
                
    def parse(self, filename, visitor):
        file = open(filename)
            
        lineno = 0
        funcs = {}

        for line in file:        
            lineno += 1
            
            parts = [ s.strip() for s in line.split(':') ]
            
            refkind = parts[0]

            try:
                if refkind not in funcs:
                    fname = ''.join(refkind.split('_')).lower()
                    func = getattr(visitor, 'visit_' + fname)
                    funcs[refkind] = func
                
                visitor.data = (lineno, parts)
                args = [ long(a) for a in parts[1:-2] ]
                funcs[refkind](*args)

            except Exception as e:
                raise ParserException(lineno, line, traceback.format_exc())


def dumpGraphvizClassDiagram(classes, filename):
    out = open(filename, 'w')
    
    out.write('digraph JavaClassDiagram {\n')
    out.write('  node [shape=record,style=filled,fillcolor=gray95]\n')
    out.write('  edge [dir=back, arrowtail=empty]\n')

    for stamp, klass in classes.iteritems():
        out.write('  "%s" [ label = "{%s ' % (klass, klass))
        
        for field in klass._fields:
            out.write('| %s' % (field[0]))
        
        out.write('}" ]')
        
        if klass.superClass:
            out.write('  "%s" -> "%s"' % (klass.superClass, klass))
        # 2 [label = "{SCEV|...|...}"]
        
    out.write("}\n")


class TlogParser():
    def parse(self, tlogfilenames, visitor):            
        def dispatch(line, funcs):
            def getvalue(value):
                try:
                    return long(value)
                except ValueError:
                    return value
                  
            try:
                parts = [ s.strip() for s in line.split(':') ]
            
                event = parts[0]
            
                if event not in funcs:
                    func = getattr(visitor, 'visit_' + event.lower())
                    funcs[event] = func
                
                args = [ getvalue(p) for p in parts[1:] ]
                funcs[event](*args)
            
            except Exception as e:
                tb = traceback.format_exc()

                raise ParserException(0, line, tb)
        
        class Entry:
            def __init__(self, file):
                self.file = file
                self.curline = file.readline()
            
            def next(self):
                self.curline = self.file.readline()
                
            def hasnext(self):
                return self.curline != ''

        funcs = {}
        
        it = [ Entry(open(name)) for name in tlogfilenames ]
        it = [ t for t in it if t.curline != '']
        
        while len(it) > 0:
            min = None
            t = None
            for i in it:
                eventno = long(i.curline.split(':')[0])
                
                assert eventno != min, 'Error eventno duplicated: %s %s %s %s' % (eventno, min, i, t)

                if eventno < min or min == None:
                    t = i
                    min = eventno
            
            line = ':'.join(t.curline.rstrip().split(':')[1:])
            
            dispatch(line, funcs)
            
            t.next()

            it = [ t for t in it if t.curline != '']
        
class ClassTableBuilderVisitor():
    def __init__(self):
        self.heapclasstable = HeapClassTable()
    
    def visit_classfileload(self, classname):
        pass

    def visit_classload(self, classsig):
        pass
    
    def visit_classprepare(self, classsig):
        pass
    
    def visit_vmstart(self):
        pass

    def visit_vminit(self):
        pass
    
    def visit_vmdeath(self):
        pass
    
    def visit_exception(self):
        pass
    
    def visit_stampclass(self, classstamp, classid, superclassstamp, classsig):
        classstamp = Stamp(classstamp)
        
        superclass = self.heapclasstable.getclassbystamp(Stamp(superclassstamp)) if superclassstamp != -1L else None
        
        heapclass = HeapClass(classstamp, classsig, superclass)
        
        self.heapclasstable.putclass(heapclass)

    def visit_prepareclass(self, classstamp, interfacesdef, fieldsdef):
        classstamp = Stamp(classstamp)
        heapclass = self.heapclasstable.getclassbystamp(classstamp)
        
        # iis = [ s.strip() for s in interfacesdef.split('#') if s.strip() != '' ][1:]
        # for interstamp in iis:
        #    interstamp = Stamp(interstamp)
        
        fs = [ s.strip() for s in fieldsdef.split('#') if s.strip() != '' ][1:]
        
        heapclass.prepare()
        
        for fielddef in fs:
            field = fielddef.split('@')
            fieldname = field[1]
            fieldtype = field[2]
            # print field
            heapclass.putfield(fieldname, fieldtype)
    
class TlogVisitor(ClassTableBuilderVisitor):
    def __init__(self):
        ClassTableBuilderVisitor.__init__(self)
        
        self.graph = Graph()
        self.objecttable = {}
        
    def visit_garbagecollectionstart(self):
        pass
    
    def visit_free(self, stamp):
        pass
    
    def visit_alloc(self, thisstamp):
        assert thisstamp != 0L
    
    def visit_newarray(self, arraystamp, count, atype):
        assert arraystamp != 0L
    
    def visit_anewarray(self, stamp, count, classname):
        pass
        
    def visit_putfield(self, fieldname, sourcestamp, targetstamp):
        assert sourcestamp != 0L
        assert targetstamp != 0L
        # if sourcestamp == 0L or targetstamp == 0L:
        #    print 'Warning: (not tagged) invalid putfield: ', fieldname, sourcestamp, targetstamp
        #    return
        
        source = self._getobject(sourcestamp)
        
        assert source != None
        # print 'Warning: null source on putfield', fieldname, sourcestamp, targetstamp
        # return
        
        target = self._getobject(targetstamp)
        
        label = 'FIELD' + '$' + fieldname
        self._put(source, target, label)
        
        source.putvalue(label, target)
        
        # print source, target, fieldname
    
    def visit_putstatic(self, fieldname, classname, newvaluestamp):
        pass
    
    def visit_aastore(self, index, arrayref, value):
        source = self._getobject(arrayref)
        target = self._getobject(value)
        label = index
        
        self._put(source, target, label)

        source.putvalue(index, target)
    
    def _getobject(self, stampvalue):
        if stampvalue == -1L:
            return None
        
        stamp = Stamp(stampvalue)
        heapclass = self.heapclasstable.getclassbyobjectstamp(stamp)
        
        try:
            return self.objecttable[stamp]
        except KeyError:
            return self.objecttable.setdefault(stamp, HeapObject(stamp, heapclass))
    
    def _put(self, source, target, label):
        self.graph.putEdge(source, target, label)

class SampleVisitor(TlogVisitor):
    COLUMNS = {}
    
    def __init__(self, samplenames, csv):
        TlogVisitor.__init__(self)
        
        self._samplenames = samplenames
        self.table = []
        self.csv = csv
    
    def compute(self, sample, tlgraph, frgraph, dfgraph, hbgraph):
        c = tlgraph.commonnodecount(frgraph)
        
        row = []
        
        SampleVisitor.COLUMNS[len(row)] = ('   S', '%4d', 'Sample number')
        row.append(sample)
        
        for g, name in [(tlgraph, 'TL'), (frgraph, 'FR')]:
            SampleVisitor.COLUMNS[len(row)] = ('   #N-' + name, '%8d', 'Number of nodes in ' + name)
            row.append(len(g))
            
            SampleVisitor.COLUMNS[len(row)] = ('   #E-' + name, '%8d', 'Number of edges in ' + name)
            row.append(g.numberofedges())
        
        SampleVisitor.COLUMNS[len(row)] = ('     #CN', '%8d', 'Number of common nodes between TL and FR')
        row.append(c)
        
        SampleVisitor.COLUMNS[len(row)] = ('  %CN/TL', '%%% 4.3f', '% of common nodes w.r.t TL')
        row.append(float(c) / len(tlgraph) * 100)
        
        SampleVisitor.COLUMNS[len(row)] = ('  %CN/FR', '%%% 4.3f', '% of common nodes w.r.t FR')
        row.append(float(c) / len(frgraph) * 100)
        
        eds = dfgraph.numberofedges()
        
        SampleVisitor.COLUMNS[len(row)] = ('     #DE', '%8d', 'Number of different edges between TL and FR')
        row.append(eds)
        
        SampleVisitor.COLUMNS[len(row)] = ('  %DE/TL', '%%% 4.3f', '% of different edges w.r.t TL')
        row.append(float(eds) / tlgraph.numberofedges() * 100)
        
        SampleVisitor.COLUMNS[len(row)] = ('  %DE/FR', '%%% 4.3f', '% of different edges w.r.t FR')
        row.append(float(eds) / frgraph.numberofedges() * 100)     

        eds = hbgraph.numberofedges() / 2
        
        SampleVisitor.COLUMNS[len(row)] = ('     #HB', '%8d', 'Number of different edges in a happens-before relation between TL and FR')
        row.append(eds)
        
        SampleVisitor.COLUMNS[len(row)] = ('  %HB/TL', '%%% 4.3f', '% of different edges w.r.t TL')
        row.append(float(eds) / tlgraph.numberofedges() * 100)
        
        SampleVisitor.COLUMNS[len(row)] = ('  %HB/FR', '%%% 4.3f', '% of different edges w.r.t FR')
        row.append(float(eds) / frgraph.numberofedges() * 100)     

        header = ''
        format = ''
        ref = ''
        ref += '# TL: Heap graph built with the trace log data\n'
        ref += '# FR: Heap graph built with the FollowReferences dump data\n'
        ref += '# \n'
        for i in range(len(SampleVisitor.COLUMNS)):
            col = SampleVisitor.COLUMNS[i]
            header += col[0] + ' ' 
            format += col[1] + ' '
            ref += '# %-10s: %s\n' % (col[0].strip(), col[2])
        
        if len(self.table) == 0:
            self.csv.write(ref + '\n')
            self.csv.write(header + '\n')
            
        values = format % tuple(row)
        self.csv.write(values + '\n')
        
        self.table.append(row)
        
    def visit_sample(self, sample, samplefilename):
        print '  Visiting sample', sample, '...',
        
        tlgraph = self.graph
        
        samplename = self._samplenames[sample - 1]
        
        print 'loading', samplename, 'FollowReferences dump file...',
        
        frvisitor = FollowReferencesVisitor(self.heapclasstable)
        FollowReferencesParser().parse(samplename, frvisitor)
        frgraph = frvisitor.graph

        basename = os.path.splitext(samplename)[0]

        #tlgraph.write(basename + '-tl.graph')
        #frgraph.write(basename + '-fr.graph')
        
        print 'computing dif...',
        dfgraph = tlgraph.edgedif(frgraph)
        dfgraph.write(basename + '-df.graph')
        
        hbgraph = Graph()
        # A dif graph has some particular properties
        for node in dfgraph.nodes():
            for label, ttnode in dfgraph.edges(node):
                tlnode = ttnode[0]
                frnode = ttnode[1]
                
                assert tlnode == node.values[label][0], 'The left (TL) node must be the last assignment seen: ' % (tlnode, node.values[label][0], label)
                
                if frnode in node.values[label]:
                    # We reached a real difference
                    hbgraph.putEdge(node, tlnode, 'L-' + str(label))
                    hbgraph.putEdge(node, frnode, 'R-' + str(label))
                
        hbgraph.write(basename + '-hb.graph')
        
        self.compute(sample, tlgraph, frgraph, dfgraph, hbgraph)
        
        print 'sample', sample, '[DONE]'
        # newgraph = graph
        # newgraph = pruneStrings(newgraph)
        # newgraph = pruneFromRoots(newgraph, 10, 30, 10)
    
    def visit_endsample(self, sample):
        pass
    
    def visit_entermain(self):
        pass
    
    def visit_exitmain(self):
        pass
    
    @staticmethod
    def _makedot(graph, filename):
        print '  Creating tlog graph image %s...' % gvFilename
        _dumpgraphviz(graph, filename)
        _dot(gvFilename)
    
    @staticmethod
    def _dumpgraphviz(graph, filename):
        basename = os.path.splitext(filename)[0]
        gv = open(basename + '.gv', 'w')
        
        gv.write('digraph G {\n')
        gv.write('  graph [ rankdir=LR ];\n')
        gv.write('  node [shape=record]\n')
        
        nodes = ""
        edges = ""
        
        for sourceNode in graph.nodes():
            nodes += '  "node%s" [ label = " <port%s> %s ' % (sourceNode, 'this', sourceNode)
            
            eid = 0
            for label, targetNode in graph.edges(sourceNode):
                nodes += ' | <port%d> %s' % (eid, label)
                edges += '  "node%s":port%d -> "node%s":port%s\n' % (sourceNode, eid, targetNode, 'this')
                eid += 1
            
            nodes += '" ];\n'
     
        gv.write(nodes)
        gv.write(edges)
        gv.write("}\n")
        gv.close()
    
    @staticmethod
    def _dot(filename):    
        basename = os.path.splitext(filename)[0]
        outfilename = basename + '.png'
        
        dotout = subprocess.check_output(['/usr/local/bin/dot', '-Tpng', '-o', outfilename, filename])

def main():          
    dbdir = './db/'
    samplenames = glob.glob(dbdir + 'fr.*.log')
    tlogfiles = glob.glob(dbdir + 'tlog.*.log')
    
    print 'Expecting', len(samplenames), 'FollowReferences dump files'

    csv = file(dbdir + 'summary.txt', 'w')

    visitor = SampleVisitor(samplenames, csv)

    print 'Retrieving', len(tlogfiles), 'transaction log files'

    TlogParser().parse(tlogfiles, visitor)
    
    csv.close()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
