import fileinput
import json

cl_vertices_f = {}
cl_vertices_l = {}
cl_edges_back = {}
cl_edges_fwrd = {}

def sorted_keys( d ):
  return sorted(d.keys())

def json2dict( x ):
  return json.loads(x, encoding="utf-8")

def dict2jsonarray( x ):
  z = []
  keys = sorted_keys(x)
  for k in keys:
    z.append( k )
    z.append( x[k] )
  return json.dumps( z )

def vcc_length( x ):
  return len(x.keys()) + len(list(filter(lambda x: x is not None,x.values())))

def build_dc_recursively( d, fq, vertices_f, vertices_l, edges_back, edges_fwrd ):
  places = sorted_keys(d)
  dj = dict2jsonarray( d )

  for pl in places:
    e = d.copy()
    if e[pl] is None:
      del e[pl]      
    else:
      e[pl] = None
    ej = dict2jsonarray( e )

    if dj not in edges_back:
      edges_back[dj] = {}
    edges_back[dj][ej] = 1
    if ej not in edges_fwrd:
      edges_fwrd[ej] = {}
    edges_fwrd[ej][dj] = 1

    if ej not in vertices_f:
      vertices_f[ej] = fq
      vertices_l[ej] = vcc_length( e )
      if len(e) > 0:
        build_dc_recursively( e, fq, vertices_f, vertices_l, edges_back, edges_fwrd )

for line in fileinput.input():
  d = json2dict(line)
  fq = d.pop('fq', None)

  for k in d:
    if d[k] == "NULL":
      d[k] = None

  if "NOM" not in d:
    d["NOM"] = None

  dvfq = {}
  dvl = {}
  de = {}
  deb = {}

  dj = dict2jsonarray( d )

  length = vcc_length( d )
  dvfq[dj] = fq
  dvl[dj] = length

  build_dc_recursively( d, fq, dvfq, dvl, de, deb )

  for k in dvfq:
    if k not in cl_vertices_f:
      cl_vertices_f[k] = dvfq[k]
    else:
      cl_vertices_f[k] += dvfq[k]
  for k in dvl:
    if k not in cl_vertices_l:
      cl_vertices_l[k] = dvl[k]
  for i in de:
    for j in de[i]:
      if i not in cl_edges_back:
        cl_edges_back[i] = {}
      cl_edges_back[i][j] = 1
  for i in deb:
    for j in deb[i]:
      if i not in cl_edges_fwrd:
        cl_edges_fwrd[i] = {}
      cl_edges_fwrd[i][j] = 1

# -----

STAY = 1.7
JMP1 = 4
JMP2 = 4
JMP3 = 100000000

def print_msg( msg ):
  print( " {0}".format( msg ) )

def print_simple( i ):
  fq = cl_vertices_f[i]
  l = cl_vertices_l[i]

  print( "{0}\t{1}\t{2}".format( i, fq, l ))

def print_full( i ):
  fq = cl_vertices_f[i]

  if i in cl_edges_fwrd:
    d = cl_edges_fwrd[i]
    for j in sorted(d.keys(), key=lambda x: (cl_vertices_f[x],x)):
      ratio = fq/cl_vertices_f[j]
      cl = "??"
      if ratio < STAY:
        cl = "= !stay"
      if ratio > JMP1:
        cl = "^"
      print ( "<-  {0}  {1:2.2f}  {2}  {3}".format(
              cl_vertices_f[j], ratio, j, cl ))
  print( "x" )

  if i in cl_edges_back:
    d = cl_edges_back[i]
    for j in sorted(d.keys(), key=lambda x: (cl_vertices_f[x],x)):
      ratio = cl_vertices_f[j]/fq
      cl = "??"
      if ratio < STAY:
        cl = "="
      if ratio > JMP1:
        cl = "^ !jump"
      print ( "->  {0}  {1:2.2f}  {2}  {3}".format(
              cl_vertices_f[j], ratio, j, cl ))
  print( "x" )

  print_simple( i )

def ratio( x, y ):
  return cl_vertices_f[y]/cl_vertices_f[x]

def is_stay( x, y, stay=STAY ):
  return ratio( x, y ) < stay

def is_jump( x, y, jump ):
  return ratio( x, y ) > jump

def has_filler( x ):
  xx = json.loads(x, encoding="utf-8")
  values = xx[1::2]
  return any( values )

def is_top_of_cl( x ):
  return x not in cl_edges_fwrd

n = 1
for i in sorted(cl_vertices_f, key=lambda x: (cl_vertices_l[x],-cl_vertices_f[x],x)):

  print( "#{0}".format( n ) )
  n += 1

  print_full( i )

  if i not in cl_edges_fwrd:
    print_msg( "No out-edge, skip." )
  elif ( cl_vertices_f[i] < 3 ):
    print_msg( "Too rare (<3), skip." )
  elif ( cl_vertices_l[i] > 8 ):
    print_msg( "Too long (>8), skip." )
  else:
    print_msg( "Processing." )
    d = cl_edges_fwrd[i]
  
    act = i

    path = []

    while True:
      stay_found = True
      jump_found = True

      max_out = None
      d = cl_edges_fwrd.get( act, {} )

      if d:
        max_out = max(d.keys(), key=lambda x: (cl_vertices_f[x],x))

      if max_out and is_stay( max_out, act ):
        print_msg( "A stay found, we follow." )
        path.append( 'v' )
        print_simple( max_out )
        act = max_out

      else:
        print_msg( "No stay (ratio={0:2.2f} > {1}), we stop.".format(
          ratio( max_out, act ) if max_out else 0, STAY ) )
        stay_found = False

        max_inn = None
        d = cl_edges_back.get( act, {} )

        if d:
          max_inn = max(d.keys(), key=lambda x: (cl_vertices_f[x],x))

        if max_inn:
          r = ratio( act, max_inn )
          jump = None
          info_msg = None
          jump_type = None

          if has_filler( max_inn ):
            jump = JMP1
            info_msg = "keeping a filler"
            jump_type = "t(k)"
          elif not has_filler( act ):
            jump = JMP2
            info_msg = "no filler"
            jump_type = "t(n)"
          elif has_filler( act ) and not has_filler( max_inn ):
            jump = JMP3
            info_msg = "omitting last filler"
            jump_type = "t(o)"
          else:
            print_msg( "impossible outcome" )
            exit( 1 )

          if is_jump( act, max_inn, jump ):
            print_msg( "An appropriate jump ({0}, {1}<) found, we follow.".format( info_msg, jump ) )
            path.append( jump_type )
            print_simple( max_inn )
            act = max_inn
          else:
            print_msg( "No appropriate jump ({0}, {1:2.2f} < {2}), we stop.".format( info_msg, r, jump ) )
            jump_found = False

        else:
          print_msg( "No backward edge -- no jump, we stop." )
          jump_found = False

      if not stay_found and not jump_found: break

    if ( is_top_of_cl( act ) ):
      print_msg( "Concrete sentence skeleton." )

    else:
      print( "{0}\t{1}\t{2}\tpVCC".format( act, cl_vertices_f[act], cl_vertices_l[act] ))
  print()

