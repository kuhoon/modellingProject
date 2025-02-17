import os
from pyNastran.bdf.bdf import BDF, CaseControlDeck

model = BDF()
E = 72397.5
G = 27000.0
nu = 0.32
rho = 0.0000000000000001
mat = model.add_mat1(1, E, G, nu, rho)

idList = [] #declare a variable. start on the first line
xValueList = []
yValueList = []
zValueList = []
xLeValueList = []
xTelueList = []
conm1List = []
mass = []
iYy = []
firstMoment = []
pbeamList = []
areaList = []
i1List = []
i2List = []
jList = []
idFromList = []
idToList = []

M1 = "Wing_data_MA_Beechraft1900D_230218/wing_data/DP6/M1_no_batteries/data_masses.dat"
M2 = "Wing_data_MA_Beechraft1900D_230218/wing_data/DP6/M2_max_batteries_wing box center/data_masses.dat"
M3 = "Wing_data_MA_Beechraft1900D_230218/wing_data/DP6/M3_max_batteries_front spar center/data_masses.dat"
nodesFileName = "Wing_data_MA_Beechraft1900D_230218/wing_data/_general/data_nodes.dat"
elementsFileName = "Wing_data_MA_Beechraft1900D_230218/wing_data/_general/data_elements.dat"

n = int(input("Bitte gebe eine Beladungszustände mit 1(no_batteries), 2(max_batteries_wing_box_center) und 3(max_batteries_front_spar_center) : "))
if n == 1 :
    with open(M1) as datFile:
        lumpValueList = [data.split() for data in datFile]
        del lumpValueList[0]
        for v in lumpValueList:
            conm1List.append(v[0])  # conm1list 1-100
            mass.append(v[2])
            iYy.append(v[3])
            firstMoment.append(v[4])
elif n == 2 :
    with open(M2) as datFile:
        lumpValueList = [data.split() for data in datFile]
        del lumpValueList[0]
        for v in lumpValueList:
            conm1List.append(v[0])  # conm1list 1-100
            mass.append(v[2])
            iYy.append(v[3])
            firstMoment.append(v[4])
elif n == 3 :
    with open(M3) as datFile:
        lumpValueList = [data.split() for data in datFile]
        del lumpValueList[0]
        for v in lumpValueList:
            conm1List.append(v[0])  # conm1list 1-100
            mass.append(v[2])
            iYy.append(v[3])
            firstMoment.append(v[4])

# open node.dat file_Wing
with open(nodesFileName) as datFile:
    nodeValueList = [data.split() for data in datFile]
    del nodeValueList[0] # delete line 0
    for v in nodeValueList:
        idList.append(v[0]) # add list element
        xValueList.append(v[1])
        yValueList.append(v[2])
        zValueList.append(v[3])
        xLeValueList.append(v[5])
        xTelueList.append(v[6])

# open elements.dat file_pbeam
with open(elementsFileName) as datFile:
    elementValueList = [data.split() for data in datFile]
    del elementValueList[0]
    for v in elementValueList:
        pbeamList.append(v[0])
        idFromList.append(v[1])
        idToList.append(v[2])
        areaList.append(v[3])
        i1List.append(v[4])
        i2List.append(v[5])
        jList.append(v[7])

# insert model.add_grid(id_no, x, y, z) for 1_nodes.dat
for i, x, y, z, xl, xt in zip(idList, xValueList, yValueList, zValueList, xLeValueList, xTelueList):
    model.add_grid(int(i), [float(x), float(y), float(z)])
    model.add_grid(25+2*int(i), [float(xl), float(y), float(z)]) #le, te grid
    model.add_grid(26+2*int(i), [float(xt), float(y), float(z)])

# insert model.add_conm1(id_conm1, id_no, Mlump)
nn = int(input("Bitte geben Sie 1 für ungekoppelt, 2 für gekoppelt ein : "))

if nn == 1 : # Entkopplung
    for j, i, m, s, iyy in zip(conm1List, idList, mass, firstMoment, iYy):
        model.add_card(['CONM1', int(j) + 10000, int(i), 0,
                        float(m),
                        0.0, float(m),
                        0.0, 0.0, float(m),
                        0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, float(iyy),
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 'CONM1')
elif nn == 2 : # Kopplung
    for j, i, m, s, iyy in zip(conm1List, idList, mass, firstMoment, iYy):
        model.add_card(['CONM1', int(j) + 10000, int(i), 0,
                        float(m),
                        0.0, float(m),
                        0.0, 0.0, float(m),
                        0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, float(s)*-1, 0.0, float(iyy),
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 'CONM1')

# insert model.add_pbeam(id_pbeam, mid, x/xb, so, area, i1, i2, i12, j)
for p, a, i1, i2, j in zip(pbeamList, areaList, i1List, i2List, jList):
    model.add_pbeam(int(p), 1, [0.0], ['YES'], [float(a)], [float(i1)], [float(i2)], [0], [float(j)], k1=1., k2=1.)

# insert model.add_cbeam
for p, idFrom, idTo in zip(pbeamList, idFromList, idToList):
    model.add_cbeam(int(p), int(p), [int(idFrom), int(idTo)], [0., 0., 1.], None)

# insert model.add_spc1
spc_id = 50
model.add_spc1(spc_id, '123456', [1, 2, 3])

# insert model.add_rbe2
for i in range(1,27):
    model.add_rbe2(150+i, i, '123456', [25+2*i])
    model.add_rbe2(177+i, i, '123456', [26+2*i])

# eigrl = model.add_eigrl(10, None, None, 10, 0, None, None, 'MASS', None, None) # how many want to mode
eigrl = model.add_eigrl(5, nd=12, norm='MAX')
model.sol = 103  # start=103
cc = CaseControlDeck([
    'SUBCASE 1',
    'SUBTITLE = Default',
    'METHOD = 5', #number of nd
    'SPC = %s' % spc_id,
    'VECTOR(SORT1,PUNCH, REAL)=ALL',
    'SPCFORCES(SORT1, REAL) = ALL',
    'BEGIN BULK',
    'MEFFMASS(ALL) = YES',
    'ECHO = BOTH'
])
model.case_control_deck = cc
model.validate()

model.add_param('POST', [-1]) #print result. 0 = .xdb, -1, 1 = .op2
model.add_param('PRTMAXIM', ['YES'])
model.add_param('OMODES', ['ALL']) #Output for extracted modes will be computed.(all=default)
model.add_param('WTMASS', [1.])


if n == 1 :
    if nn == 1: # Entkopplung
        bdf_filename_out = os.path.join('MA_final/DP6/sol103/ungekoppelt/sol103_DP6_M1_uncoupled.bdf')
    if nn == 2: # Kopplung
        bdf_filename_out = os.path.join('MA_final/DP6/sol103/kopplung/sol103_DP6_M1_coupled.bdf')
if n == 2 :
    if nn == 1: # Entkopplung
        bdf_filename_out = os.path.join('MA_final/DP6/sol103/ungekoppelt/sol103_DP6_M2_uncoupled.bdf')
    if nn == 2: # Kopplung
        bdf_filename_out = os.path.join('MA_final/DP6/sol103/kopplung/sol103_DP6_M2_coupled.bdf')
if n == 3 :
    if nn == 1: # Entkopplung
        bdf_filename_out = os.path.join('MA_final/DP6/sol103/ungekoppelt/sol103_DP6_M3_uncoupled.bdf')
    if nn == 2: # Kopplung
        bdf_filename_out = os.path.join('MA_final/DP6/sol103/kopplung/sol103_DP6_M3_coupled.bdf')


model.write_bdf(bdf_filename_out, enddata=True)
print(bdf_filename_out)
print("====> write bdf file success!")