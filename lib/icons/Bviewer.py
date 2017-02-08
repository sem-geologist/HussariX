import pyqtgraph as pg
import lxml.objectify as lo
import numpy as np
import sys
import os
import misc.elements as el

def n2a(atom_number):
    for k in list(el.elements.keys()):
        if el.elements[k]['General_properties']['Z'] == atom_number:
            return k

class EDXSpectrum():
    def __init__(self, spectrum):
        # bellow initiation happens reading bruker xml or part of xml marked as Type="TRTSpectrum"
        self.name = str(spectrum.attrib['Name'])
        if self.name.endswith('.spx') or self.name.endswith('.xls'):
            self.name = self.name[:-4]
        self.realTime = int(spectrum.TRTHeaderedClass.ClassInstance.RealTime)
        self.lifeTime = int(spectrum.TRTHeaderedClass.ClassInstance.LifeTime)
        self.zeroPeakPosition = int(spectrum.TRTHeaderedClass.ClassInstance.ZeroPeakPosition)
        self.amplification = int(spectrum.TRTHeaderedClass.ClassInstance.Amplification)
        self.shapingTime = int(spectrum.TRTHeaderedClass.ClassInstance.ShapingTime)
        self.detectorType = str(spectrum.TRTHeaderedClass.ClassInstance[1].Type)
        self.hv = float(spectrum.TRTHeaderedClass.ClassInstance[2].PrimaryEnergy)
        self.elevationAngle = float(spectrum.TRTHeaderedClass.ClassInstance[2].ElevationAngle)
        self.azimutAngle = float(spectrum.TRTHeaderedClass.ClassInstance[2].AzimutAngle)
        self.soCoatCorrection = float(spectrum.TRTHeaderedClass.ClassInstance[2].DoCoatCorrection)
        
        self.spectrumHeader = spectrum.ClassInstance[0]
        #inside this header there is CalicAbs, CalibLin, Date, Time, ChannelCount
        
        self.data = np.fromstring(str(spectrum.Channels), dtype='uint16', sep=",")
        
        self.results = []  # the quantification results of manual or automatic calculation
        for h in spectrum.ClassInstance[1].Result:
            self.results.append(h)
        
        self.elementList = []  # the elements marked manualy or automatically
        for i in spectrum.ClassInstance[2].ChildClassInstances.ClassInstance:
            self.elementList.append(i.Element)
        
        self.coatingElement = int(spectrum.ChildClassInstances.ClassInstance.CoatingElement)
        self.noCarbonCoating = 0  #  (No2Carbon) # helper flag introduced, it is not in the xml
        
    def result_table(self):
        pass
    
    def ploting_data(self):
        pass
    
    def apa(self): #Auto Plot Annotations
        energies = []
        if atom_number <=14:
            pass
        elif 14 < atom_number <= 20:
            pass
        elif 20 < atom_number <= 30:
            pass
        elif 30 < atom_number <= 40:
            pass 
        # where is 40-56????
        elif 56 < atom_number <= 71:
            pass
        elif 71 < atom_number <= 89:
            pass
        else:
            pass


thingy = lo.parse('w1_ 1.spx')
root = thingy.getroot()
spectrum = root.ClassInstance


asdas = EDXSpectrum(spectrum)

pg.plot(asdas.data)