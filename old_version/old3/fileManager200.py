import os
from pyNastran.bdf.bdf import *
import numpy as np
from math import *
# import math

nodesFileName = "Ref_220425/data_nodes.dat"
elementsFileName = "Ref_220425/data_elements.dat"
sectionFileName = "Ref_220425/data_planform.dat"
machFileName = "datFiles_numbering/6_machNum.dat"
rrfFileName = "datFiles_numbering/7_redRF.dat" #수정완료, 하지만 계산이 왜 이렇게 되었는지 알아야함
v3FileName = "datfiles_numbering/8_v3.dat" #수정완료, 하지만 계산이 왜 이렇게 되었는지 알아야함

model = BDF()

idList = [] #declare a variable. start on the first line
xValueList = []
yValueList = []
zValueList = []
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

# ===== special for sol145
idSectList = []
xLeList = []
yLeList = []
zLeList = []
cList = []
machValueList = []
rrfValueList = []
v3ValueList = []
bSpanList = []
aelistList = []
eId = 201 #point for caero1
ptList = []  # [ [], [], [] ]

E = 72397.5
G = 27000.0
nu = 0.32
rho = 0.0000000000000001
mat = model.add_mat1(1, E, G, nu, rho)

# ====================================================================
# =========================== OPEN FILES =============================
# ====================================================================

n = int(input("Bitte gebe eine Beladungszustände mit 25, 50 und 100% ein : "))
if n == 25 :
    with open("Ref_220425/masses_f025/data_masses.dat") as datFile:
        lumpValueList = [data.split() for data in datFile]
        del lumpValueList[0]
        for v in lumpValueList:
            conm1List.append(v[0])  # conm1list 1-100
            mass.append(v[2])
            iYy.append(v[3])
            firstMoment.append(v[4])
elif n == 50 :
    with open("Ref_220425/masses_f050/data_masses.dat") as datFile:
        lumpValueList = [data.split() for data in datFile]
        del lumpValueList[0]
        for v in lumpValueList:
            conm1List.append(v[0])  # conm1list 1-100
            mass.append(v[2])
            iYy.append(v[3])
            firstMoment.append(v[4])
elif n == 100 :
    with open("Ref_220425/masses_f100/data_masses.dat") as datFile:
        lumpValueList = [data.split() for data in datFile]
        del lumpValueList[0]
        for v in lumpValueList:
            conm1List.append(v[0])  # conm1list 1-100
            mass.append(v[2])
            iYy.append(v[3])
            firstMoment.append(v[4])

# open node.dat file_Wing
with open("Ref_220425/data_nodes.dat") as datFile:
    nodeValueList = [data.split() for data in datFile]
    del nodeValueList[0] # delete line 0
    for v in nodeValueList:
        idList.append(v[0]) # add list element
        xValueList.append(v[1])
        yValueList.append(v[2])
        zValueList.append(v[3])

# open elements.dat file_pbeam
with open("Ref_220425/data_elements.dat") as datFile:
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

# <================ special for sol145 ===================>
# open 5_sections.dat file_Wing
with open(sectionFileName) as datFile:
    sectValueList = [data.split() for data in datFile]
    del sectValueList[0]  # 0번 행을 지워라
    for v in sectValueList:
        idSectList.append(v[0])
        xLeList.append(v[1])  # list 원소 추가
        yLeList.append(v[2])
        zLeList.append(v[3])
        cList.append(v[4])

# open 6_machNum.dat file
with open(machFileName) as datFile:
    tempList = [data.split() for data in datFile]
    for t in tempList:
        machValueList.append(float(t[0]))

# open 7_redRF.dat file
with open(rrfFileName) as datFile:
    tempList = [data.split() for data in datFile]
    for t in tempList:
        rrfValueList.append(float(t[0]))

# open 8_v3.dat file
with open(v3FileName) as datFile:
    tempList = [data.split() for data in datFile]
    for t in tempList:
        v3ValueList.append(float(t[0]) * -1)

# ====================================================================
# ========================= ADD ATTRIBUTES ===========================
# ====================================================================

# start model number
model.sol = 200  # start=103

# case control
spc_id = 50
cc = CaseControlDeck([
    'SUBCASE 1',
    'SUBTITLE = Default',
    'METHOD = 5', # MODIFIED GIVENS METHOD OF REAL EIGENVALUE EXTRACTION
    'SPC = %s' % spc_id, # WING ROOT DEFLECTIONS AND PLATE IN-PLANE ROTATIONS FIXED
    'VECTOR(SORT1,REAL)=ALL',
    'SPCFORCES(SORT1, REAL) = ALL',
    'BEGIN BULK',
    'ANALYSIS = FLUTTER',
    'AESYMXY = Asymmetric',
    'AESYMXZ = Symmetric',
    'FMETHOD = 1',
    'ECHO = BOTH',
    'SET 99 = 1,THRU, 12'
])
model.case_control_deck = cc
model.validate()


# model.add_mat1(1, E, G, nu, rho)

model.add_param('POST', [-1])
model.add_param('PRTMAXIM', ['YES'])
model.add_param('SNORM', [20.0])
model.add_param('WTMASS', [1.0])  # default = 1.0
model.add_param('Aunit', [1.0])
model.add_param('OMODES', ['ALL'])

# # insert model.add_grid(id_no, x, y, z)
for i, x, y, z in zip(idList, xValueList, yValueList, zValueList):
    model.add_grid(int(i), [float(x), float(y), float(z)])

# insert model.add_conm1(id_conm1, id_no, Mlump)
nn = int(input("Bitte geben Sie 1 für ungekoppelt, 2 für gekoppelt ein : "))

if nn == 1 :
    for j, i, m, s, iyy in zip(conm1List, idList, mass, firstMoment, iYy):
        model.add_card(['CONM1', int(j) + 10000, int(i), 0,
                        float(m),
                        0.0, float(m),
                        0.0, 0.0, float(m),
                        0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, float(iyy),
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 'CONM1')
elif nn == 2 :
    for j, i, m, s, iyy in zip(conm1List, idList, mass, firstMoment, iYy):
        model.add_card(['CONM1', int(j) + 10000, int(i), 0,
                        float(m),
                        0.0, float(m),
                        0.0, 0.0, float(m),
                        0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, float(s), 0.0, float(iyy),
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 'CONM1')

# insert model.add_pbeam(id_pbeam, mid, x/xb, so, area, i1, i2, i12, j)
for p, a, i1, i2, j in zip(pbeamList, areaList, i1List, i2List, jList):
    model.add_pbeam(int(p), 1, [0.0], ['YES'], [float(a)], [float(i1)], [float(i2)], [0], [float(j)], k1=1., k2=1.)

# insert model.add_cbeam
for p, idFrom, idTo in zip(pbeamList, idFromList, idToList):
    model.add_cbeam(int(p), int(p), [int(idFrom), int(idTo)], [0., 0., 1.], None)

# insert model.add_spc1, spcadd
model.add_spc1(spc_id, '123456', [1, 2, 3])
model.add_spcadd(1, spc_id)

# insert model.add_eigrl
eigrl = model.add_eigrl(5, nd=12, norm='MAX') # how many want to mode

# <=========== sol 145 ===============>
# insert model.add_point(id_no, x, y, z)
for x, y, z, c in zip(xLeList, yLeList, zLeList, cList):
    model.add_point(eId, [float(x), float(y), float(z)])
    ptList.append([float(x), float(y), float(z)])
    eId = eId + 1
    model.add_point(eId, [float(x) + float(c), float(y), float(z)])
    eId = eId + 1

# insert model.add_aefact for caero1
box1 = np.linspace(0,1,5)

# x1 = np.linspace(0, pi/2, 13) # wide narrow
# y1= np.sin(x1)
# # print(y1)
#
# x2 = np.linspace(-pi/2, pi/2, 33) # narrow wide narrow
# y2 = (np.sin(x2)+1)/2
# print(y2)

# x2 = np.linspace(0,7*pi/24, 10)
# y2=np.sin(x2)
# y22= np.linspace(sin(7*pi/24),1,6)
y2 = np.linspace(0, 0.8, 11)
y22 = np.linspace(0.8, 1, 4)
box2 = np.unique(np.concatenate((y2, y22)))
print(len(box2))
print(box2)

y3 = np.linspace(0, 0.14, 6)
y33 = np.linspace(0.14, 0.92, 25)
y333 = np.linspace(0.92, 1, 6)
box3 = np.unique(np.concatenate((y3, y33, y333)))
print(len(box3))
print(box3)

bSpanList = [len(box1)-1, len(box2)-1, len(box3)-1] # [4, 12, 32], maximal panel [4, 14, 36]

model.add_aefact(1, box1)
model.add_aefact(2,box2)
model.add_aefact(3, box3)

# insert model.add_paero1, caero1
eId2 = 103001
nCh = 6 #nchord
for i in range(len(idSectList) - 1):  # leg, list = 길이, 원소의 갯수
    model.add_paero1(eId2)
    model.add_caero1(eId2, eId2, 1, np.array(ptList[i], float), float(cList[i]), np.array(ptList[i + 1], float), float(cList[i + 1]), 0, 0, i+1, nCh, 0)
    eId2 += 1000

# # insert model.add_set1, aero, aeros
model.add_set1(1, idList)
model.add_aero(float(1.0), float(2100.0), float(1.225E-12), 0)  # velocity, mean_aerodynamic_chord, air_density,
model.add_aeros(float(2100.0), float(17760.0), float(3.442E7 / 2), 0, 0)  # mean_aerodynamic_chord, reference_surface, half span model => half area

# insert model.add_mkaero2
for m in machValueList:
    for rf in rrfValueList:
        model.add_mkaero2([m], [rf])

# insert model.add_spline7
model.add_card(['SPLINE7',1, 105001, 1, None, 1, 1.0, 1.0, None, None, None, None, 'BOTH', 'FBS6', 1.0, 1.0, None], 'SPLINE7')

# manage aelist
eId2 = eId2 - (1000 * len(bSpanList))
for i in range(len(bSpanList)):
    for b in range(bSpanList[i] * nCh):
        aelistList.append(eId2 + b)
    eId2 += 1000
model.add_aelist(1, aelistList)  # mesh 33x6=

# manage flfact
seaAD = 1.225E-12
cruiseAD = 8.170E-13 #cruise_level_air_density
model.add_flfact(1, [float(cruiseAD/seaAD)])
model.add_flfact(2, [float(0.0)])
model.add_flfact(3, v3ValueList)

# insert model.add_flutter
model.add_flutter(1, 'PK', 1, 2, 3, 'L', None, None, float(1E-3)) #interpolation 'L'inear

# write bdf file
# model.validate()
bdf200_filename_out = os.path.join('sol200_addDLM_f025_coupled_4_13_34_test.bdf')
model.write_bdf(bdf200_filename_out, enddata=True)
print(bdf200_filename_out)
print("====> write bdf file success!")

