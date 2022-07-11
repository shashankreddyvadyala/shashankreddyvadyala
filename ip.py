import os,re
import numpy as np
import warnings
warnings.fileterwarnings('ignore')
import xlsxwriter as xl
from HTP_Package_v5_1 import collector_v4 as c3
from HTP_Package_v5_1 import smartCollectorHTPFFD72 as sc
from HTP_Package_v5_1 import HTP_data
from HTP_Package_v5_1 import HTP_analysis
from HTP_Package_v5_1 import HTP_plotter
import openpyxl
import pandas as pd
import openpyxl import load_workbook

####################################################################
class DataGeneration():
    
##############################################
    def __init__(self,dictt,HTPmaninInpFiles,partNames,solnDict,inputpath,outputPath):
        self.__dictt           =dictt
        self.__fac             =float(self.__dictt['ModelFactor'])
        self.__mData           ={}
        self.__c3              =c3.SmartCollector()
        self.__tauRootPath     = dictt['TaurootPath']
        self.__files           = HTPMainInpFiles
        self.__aoaLst          = []
        self.__ihDict          = {}
        self.__ABbyCref        = []
        self.__addMarkers      = []
        self.__markersHTPon    = []
        self.__markersHTPoff   = []
        self.__markerHTP       = []
        self.__fwdMarkers      = partNames
        self.__solnDict        = solnDict
        self.__inputPath       = inputPath
        self.__outputpath      = outputPath
        
        
######################################################################

    def __rotMatrix(self,axis,angle):
        axis                  = np.array(axis)
        angle                 = angle*np.pi/180
        skew                  = lambda v : np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
        symmetric             = lambda v:np.dot(bv.reshape(3,1),v.reshape(1,3))
        return (symmetric(axis)*(1-np.cos(angle))+skew(axis*np.sin(angle)+np.eye(3)*np.cos(angle))

###############################################################################
    def __getIH(self):
        ihDict            =  {}
        pattern           = re.compile(r'ih(m?\d+p\d+)')
        for string in self.__files:
            try:
                val    = ((pattern.search(string)).group(1)).replace('p','.')
                val    = val.replace('m','-')
                ihDict[string] = val
            except:
                ihDict[string] = "HTPoff"
        return ihDict
###############################################################################
    def __getAOAlst(self):
        aoaLst             = []
        file               = self.__outputPath + "/"+self.__files[0]
        noAOA              = int(self.__dictt['NoAOACases'])
        marker             = self.__dictt['Additional_Markers'][0]
        f                  = open(file,'r')
        lines              = f.readlines()
        f.close()
        for idx,line in enumerate(lines):
            if marker == line.strip():
                lno = idx
        for idx in range(lno+2,lno+2+noAOA):
            aoaLst.append(lines[idx].split())[0])
            
        self.__aoaLst      = aoaLst
        
#################################################################################

      def __getDatadict(self,header,line):
          val       = [x.strip() for x in line.split()]
          val.pop(0) 
          dictt     = {}
          for idx in range (len(val)): dictt[header[idx]] = val[idx]
          return dictt
      
##############################################################################
     def __getIHdata(self,file,markers):
         noAOA            = int(self.__dictt['NoAOACases'])
         odict            = {}
         f                = open(file,'r')
         lines            = f.readlines()
         f.close()
         markersLno       = {}
         for idx,line in enumerate(lines):
             for m in markers:
                 if m == line.strip():
                     markerslno[m] = idx
        header = lines[markerslno[markers[0]]+1]).split()
        header.pop(0)
        for m in markers:
            odict[m] = {}
            lno = markersLno[m]
            for idx in range(lno=2,lno+2+noAOA):
                aoa = (lines[idx].split())[0]
                odict[m][aoa] = {}
                odict[m][aoa] = self.__getDatadict(header,lines[idx])
        return odict
    
#####################################################################

      def __createHTPmainInpFiles(self,file,option):
          CLiftLst     = []
          CDragLst     = []
          CMyLst       = []
          
          
          if option == "AC":
              for aoa in self.__aoaLst:
                  CLiftLst.append(self.__fac*float(self.__mdata[file]['Total'][aoa]['CLift']))
                  CDragtLst.append(self.__fac*float(self.__mdata[file]['Total'][aoa]['CDrag']))
                  CMyLst.append(self.__fac*float(self.__mdata[file]['Total'][aoa]['CMy']))
                  
             # print(CLiftlst)
             
         if option == "REAR":
             if file == "HTPoff.txt":
                 for aoa in self.__aoaLst:
                     clsum      = 0
                     cdsum      = 0
                     cmysum     = 0
                     for idx,m in enumerate (self.__markersHTPoff):
                         clsum   = clsum + float(self.__mData['HTPoff.txt'][m][aoa]['CLift'])
                         cdsum   = cdsum + float(self.__mData['HTPoff.txt'][m][aoa]['CDrag'])
                         cmysum   = cmysum + float(self.__mData['HTPoff.txt'][m][aoa]['CMy'])
                         
                    CLiftLst.append(self.__fac*clsum)
                    CDragLst.append(self.__fac*cdsum)
                    CMyLst.append(self.__fac*cmysum)
                    
            else:
                for aoa in self.__aoaLst:
                    clsum      = 0
                    cdsum      = 0
                    cmysum     = 0
                    for idx,m in enumerate(self.__markersHTPon):
                        clsum    = clsum + float(self.__mData[file][m][aoa]['CLift'])
                        cdsum    = cdsum + float(self.__mData[file][m][aoa]['CDrag'])
                        cmysum    = cmysum + float(self.__mData[file][m][aoa]['CM_y'])
                        
                    
                    CLiftLst.append(self.__fac*clsum)
                    CDragLst.append(self.__fac*cdsum)
                    CMyLst.append(self.__fac*cmysum)
                    
            outFileName        = self.__ihDict[file] + "-"+option+".txt"
            outfile            = open(self.__outputPath = "/" +outFileName,'w')
            outFile.write("Alpha\t" + "CLift\t" + "CDrag\t" + "CMy\n")
            for idx in range(len(self.__aoalst)):
                outFile.write(str(self.__aoaLst[idx])  +"\t" +str(CLiftLst[idx]) + "\t" +str(CDragLst[idx]) + "\t" +str(CMyLst[idx]) +"\n")
            # print(outfile)
            
            print("HTPmain Input file successfully created fot " + str(file) + "for" +option)
            outFile.close()
            return outfileName
        
##############################################################################

      def __createConfigFile(self,HTPmainInputFiles,option):
          cfgFile    = open(self.__outputPath +"/" +"config_" + option + ".cfg",'w')
          cfgFile.write("REF:  " + self.__inputPath + "/" +"HTP_Package_v5_1" +"/" +"reference_AC_NF" + ".txt\n")
          
          for f in self.__files:
              try:
                  iHval = float(self.__ihDict[f])
                  # print(iHval)
                  cfgFile.write(str(iHval) +" " + self.__outputPath + "/" + HTPmainInpFiles[f])
                  cfgFile.write("\n")
              except:
                  cfgFile.write("OFF"  +" " + self.__outputPath + "/" + HTPmainInpFiles[f])
                  cfgFile.write("\n")
        print(iHval)
        cfgFile.close()
        print("config file for " + option +" created successfully.")
        
#######################################################################################
       
       def __runHTPmain(self,option):
           print("HTP main run started for " + option)
           print(".............................................")
           user_inputs                = {'htp_config' : self.outputPath + "/" +"config_" + option +".cfg" , 'format' :'basic'}
           # print(user_inputs)
           cfd_raw_data, reerence        = HTP_data.cfd_inputs(user_inputs["htp_config"], user_inputs["format"])
           htp_former_data            = cfd_raw_data['Basic']
           HTP_data.pickling_data(htp_former_data, 'former_data.pkl',self.__outputPath)
           data_unpickled = HTP_data.unpickling_data(os.path.join(self.__outputPath,'former_data.pkl'))
           
           # analysis section
           htp_data, htp_data_visual       = HTP_analysis.data_model(htp_former_data)
           ih0, ih0_ext, clh_ih_linear_coef, epsilon, epsilon_altep, alpha_h, alpha_h_altep, clh_ac, cmh_ac, cdh_ac, clh,cdh,clh_altep,cdh_altep, coeffic = HTP_analysis.tails_data(htp_data, reerence['alpha_h0'], reference['epsilon_alternative'], reference['surface_htp'],reference['surface_wing'], length_ratio=1.0)
           # print(coeffic[3,:])
           
           # folder management
           
           path                          = self.__outputPath
           iteration                     = HTP_data.folder_management(path,option)
           
           # (plotter section)
           
           HTP_plotter.cfd_plotter     (reference['name'], os.path.join(path,'HTP_analysis_' + str(iteration) + "_" +option), htp_former_data, htp_data, htp_data_visual)
           if not np.isnan(ih0).all():
               HTP_plotter.check_plotter   (reference['name'], os.path.join(path, 'HTP_analysis_' + str(iteration) + "_" + option), htp_data, ih0, ih_ext,clh_ih_linear_coef, clh_ac,cdh_ac, reference['surface_htp'],reference['surface_wing'])
           HTP_plotter.alpha_H0_plotter(reference['name'], os.path.join(path,'HTP_analysis_'+str(iteration) + "_" + option), htp_data,clh, epsilon, epsilon_altep, reference['surface_htp'], reference['surface_wing'])
           HTP_plotter.htp_plotter(reference['name'], os.path.join(path,'HTP_analysis_'+str(iteration) + "_" + option), htp_data[0]['Alpha'],epsilon,epsilon_altep,alpha_h, alpha_h_altep, clh, clh_altep, cdh, cdh_altep, cmh_ac, reference['epsilon_alternative'], reference['alpha_ho'],reference['surface_htp'], reference['surface_wing'])
           
           
           HTP_plotter.file_writer_v2 (alpha_h, clh, cdh,cmh_ac, htp_data[0]['Alpha'], epsilon, epsilon_altep, coeffic, path,iteration,option)
           
           # print(HTP_plotter[0,:])
           print("HTP-main run completed for " + option)
           print("............................................")
           print("post process successfull for " + option)
           
           # print(ih0)
           
           if np.isnan(ih0).all():
               ih0 = ['NA' for i in range(len(ih0))]
               
           return epsilon,ih0,coeffic[3,:],epsilon_altep
       
########################################################################


        def __deleteHTPmainFiles(self,HTPmainInpFiles):
            for key in HTPmainInpFiles.keys():
                file = self.__outputPath+"/"+HTPmainInpFiles[key]
                if os.path.exists(file):
                    os.remove(file)
                else:
                    print("file does not exist")
            print("files deleted successfully")
            
###########################################################################

        def __deleteConfigFiles(self):
            file1 = self.__outputPath + "/" +"cofig_AC_NF.cfg"
            file2 = self.__outputPath + "/" +"cofig_REAR_NF.cfg"
            
            if os.path.exists(file1) and os.path.exists(file2):
                os.remove(file1)
                os.remove(file2)
                print("config files successfully deleted")
            else:
                print("config files does not exist")
                
###########################################################################

       def __computeCmh0(self,file):
           CLHs = []
           CMHs = []
           
           for aoa in self.__aoaLst:
               beta= self.__mData[file][self.__markersHTPon[0][aoa]['beta']]
               # print(beta)
               
               ABW = np.dot(self.__rotMatrix([0,-1,0],float(aoa)),self.__rotMatrix([0,0,1],float(beta)))
               RearSumClift = 0
               RearSumCliftHTPoff = 0
               RearsumCmyt = 0
               RearSumCmytHTPoff = 0
               
               for idx,m in enumerate(self.__markersHTPon):
                   RearSumClift = RearSumClift + float(self.__mData[file][m][aoa]['CLift'])
                   forceBodyAxis = np.dot(ABW,
                           np.array([-float(self.__mData[file][m][aoa]['CDrag']),float(self.__mData[file][m][aoa]['CSideF']),
                                     -float(self.__mData[file][m][aoa]['CLift'])]))
                   momentBodyAxisY = forceBodyAxis[2]*self.__ABbyCref[2]+\
                                              forceBodyAxis[0]*self.__ABbyCref[2] + \
                                                  float(self.__mData[file][m][aoa]['CM_y'])
                   RearSumCmytHTPoff = rearSumCmytHTPoff + float(momentBodyAxisYHTPoff)
                   
              CLHs.append(self.__fac*RearSumClift-self.__fac*RearSumCliftHTPoff)
              CMHs.append(self.__fac*RearSumCmyt-self.__fac*RearSumCmytHTPoff)
              
        
        CLHs = np.array(CLHs)
        CMHs = np.array(CMHs)
        
        coeff = np.polyfit(CLHs,CMHs,1)
        CMHs = np.array(CMHs)
        
        coeff = np.polyfit(CLHs,CMHs,1)
        return coeff[1]
    
###########################################################################################################################################

     def __writePartData(self,ws,wb,file,markers,aoa,row,col,rowTmp,colTmp,epsac,epsr,ih0ac,cmH0,k,AR,CLH0,CDH0,soln):
         
         lenn = len(self.__addmarkers + markers)
         beta = self.__mdata[file][markers[0]][aoa]['beta']
        # print(beta)
        
        ABW=np.dot(self.__rotMatrix([0,-1,0],float(aoa)),self.__rotMatrix([0,0,1],float(beta)))
        ws.write(row,col,'Alpha')
        ws.write(row,col+6,'Lbw')
        ws.write(row,col+7,float(ABW[0,0]))
        ws.write(row,col+8,float(ABW[0,1]))
        ws.write(row,col+9,float(ABW[0,2]))
        ws.write(row,col+1,float(aoa))
        row = row+1
        alpha_row = row
        
        ws.write(row,col,'beta')
        ws.write(row,col+7,float(ABW[1,0]))
        ws.write(row,col+8,float(ABW[1,1]))
        ws.write(row,col+9,float(ABW[1,2]))
        ws.write(row,col+1,float(beta))
        row= row+1
        beta_row=row
        ws.write(row,col,'iH')
        ws.write(row,col+7,float(ABW[2,0]))
        ws.write(row,col+8,float(ABW[2,1]))
        ws.write(row,col+9,float(ABW[2,2]))
        
        if file != 'HTPoff.txt':
            ws.write(row,col+1,float(self.__ihDict[file]))
        else:
            ws.write(row,col+1,self.__ihDict[file])
            
        ws.write(row+1,col,'Solution')
        ws.write(row+1,col+1,soln)
        
        row=row+3
        
        C_values=row+2
        
        ws.write(row,col,'Surfacepart')
        ws.write(row,col+1,'name')         
        ws.write(row,col+2 ,'CLift')      
        ws.write(row,col+3 ,'CDrag')     
        ws.write(row,col +4,'CSide')       
        ws.write(row,col +5,'Area%')       
        ws.write(row,col+7 ,'C_x' )      
        ws.write(row,col +8 ,'C_y')     
        ws.write(row,col +9 ,'C_z') 
        
        RearSumClift = 0
        RearSumCdrag = 0
        RearSumCside = 0
        RearSumArea = 0
        RearSumCx   = 0
        RearSumCy   = 0
        RearSumCz   = 0
        
        RearSumCliftHTPoff = 0
        RearSumCdragHTPoff = 0
        
        
        ForwardSumClift = 0
        ForwardSumCdrag = 0
        ForwardSumCside = 0
        ForwardSumArea = 0
        ForwardSumCx   = 0
        ForwardSumCy   = 0
        ForwardSumCz   = 0
        
        
        ForwardSumCliftHTPoff = 0
        ForwardSumCdragHTPoff = 0
        
        RearSumCmx = 0
        RearSumCmy = 0
        RearSumCmz = 0
        RearSumCmxt = 0
        RearSumCmyt   = 0
        RearSumCmzt   = 0
        
        RearSumCmytHTPoff = 0
        
        ForwardSumCmx = 0
        ForwardSumCmy = 0
        ForwardSumCmz = 0
        ForwardSumCmxt = 0
        ForwardSumCmyt  = 0
        ForwardSumCmzt   = 0
        
        ForwardSumCmyHTPoff = 0
        
        
        for idx,m in enumerate(self.__fwdMarkers):
            forceBodyAxis = np.dot(ABW,
                    np.array([-float(self.__mData[file][m][aoa]['CDrag']),float(self.__mData[file][m][aoa]['CSidef']),
                              -float(self.__mData[file][m][aoa]['CLift'])]))
            
            momentBodyAxisX = forceBodyAxis[1]*self.__ABbyCref[2] - \
                                            forceBodyAxis[2]*self.__ABbyCref[1] - \
                                                  float(self.__mdata[file][m][aoa]['CM_x'])/float(self.__dictt['cref_XZ']) 
                                                  
             momentBodyAxisY = forceBodyAxis[2]*self.__ABbyCref[0] - \
                                             forceBodyAxis[0]*self.__ABbyCref[2] - \
                                                   float(self.__mdata[file][m][aoa]['CM_y']) 
                                                   
            momentBodyAxisZ = forceBodyAxis[0]*self.__ABbyCref[1] - \
                                            forceBodyAxis[1]*self.__ABbyCref[0] - \
                                                  float(self.__mdata[file][m][aoa]['CM_z'])/float(self.__dictt['cref_XZ']) 
                                                  
        # print("len of markers::",len(marker))
        
        RearSumClift =RearSumClift + float(self.__mData[file][m][aoa]['CLift'])
        RearSumCdrag =RearSumCdrag + float(self.__mData[file][m][aoa]['CDrag'])
        RearSumCside =RearSumCside+ float(self.__mData[file][m][aoa]['CSideF'])                                          
        RearSumArea =RearSumArea + float(self.__mData[file][m][aoa]['Area'])                                           
        RearSumCx =RearSumCx + float(forceBodyAxis[0])   
        RearSumCy =RearSumCy + float(forceBodyAxis[1])                                         
        RearSumCz =RearSumCz + float(forceBodyAxis[2]) 
        
        RearSumCmx =RearSumCmx + float(self.__mData[file][m][aoa]['CM_x'])
        RearSumCmy =RearSumCmy + float(self.__mData[file][m][aoa]['CM_y'])
        RearSumCmz =RearSumCmz + float(self.__mData[file][m][aoa]['CM_z'])
        RearSumCmxt =RearSumCmxt + float(momentBodyAxisX)
        RearSumCmyt =RearSumCmyt + float(momentBodyAxisY)
        RearSumCmzt =RearSumCmzt + float(momentBodyAxisZ)
        
        
    for idx,m in enumerate(self.__markersHTPoff):
        RearSumCliftHTPoff = RearSumCliftHTPoff +float(self.__mData['HTPoff.txt'][m][aoa]['CLift'])
        RearSumCdragHTPoff = RearSumCdragHTPoff +float(self.__mData['HTPoff.txt'][m][aoa]['CDrag'])
        
        forceBodyAxisHTPoff = np.dot(ABW,
                    np.array([-float(self.__mData['HTPoff.txt'][m][aoa]['CDrag']),float(self.__mData['HTPoff.txt'][m][aoa]['CSideF']),
                              -float(self.__mData['HTPoff.txt'][m][aoa]['CLift'])]))
        momentBodyAxisYHTPoff = forceBodyAxisHTPoff[2]*self.__ABbyCref[0] - \
                                        forceBodyAxisHTPoff[0]*self.__ABbyCref[2] + \
                                            float(self.__mdata['HTPoff.txt'][m][aoa]['CM_y'])
                                            
        RearsumCmyHTPoff = RearSumCmytHTPoff + float(momentBodyAxisYHTpoff)
        
    row = row+1
    
    for idx,m in enumerate(self.__addmarkers + markers):
        ws.write(row+idx,col,'body_part')
        ws.write(row+idx,col+1,m)
        ws.write(row+idx,col+2,round(float(self.__mData[file][m][aoa]['CLift']),8))
        ws.write(row+idx,col+3,round(float(self.__mData[file][m][aoa]['CDrag']),8))
        ws.write(row+idx,col+4,round(float(self.__mData[file][m][aoa]['CSideF']),8))
        ws.write(row+idx,col+5,round(float(self.__mData[file][m][aoa]['Area']),8))
        forceBodyAxis = np.dot(ABW,
                np.array([-float(self.__mData[file][m][aoa]['CDrag']),float(self.__mData[file][m][aoa]['CSideF']),
                          -float(self.__mData[file][m][aoa]['CLift'])])) 
        ws.write(row+idx,col+7,round(forceBodyAxis[0],8))
        ws.write(row+idx,col+8,round(forceBodyAxis[1],8))
        ws.write(row+idx,col+9,round(forceBodyAxis[2],8))
    errorClift = float(self.mData[file]['Total'][aoa]['CLift']) - ForwardSumClift - RearSumClift
    errorClift = float(self.mData[file]['Total'][aoa]['CDrag']) - ForwardSumCDrag - RearSumCDrag
    errorClift = float(self.mData[file]['Total'][aoa]['CSideF']) - ForwardSumCSide - RearSumCSide
    errorClift = float(self.mData[file]['Total'][aoa]['Area']) -  ForwardSumArea - RearSumArea
    
    Totalc = np.dot(ABW,
                np.array([-float(self.__mdata[file]['Total'][aoa]['CDrag']),float(self.__mData[file]['Total'][aoa]['CSideF']),
                          -float(self.__mdata[file]['Total'][aoa]['CLift']]))
            
     TotalcHTPoff = np.dot(ABW,
                         np.array([-float(self.__mdata['HTPoff.txt']['Total'][aoa]['CDrag']),float(self.__mData['HTPoff.txt']['Total'][aoa]['CSideF']),
                                   -float(self.__mdata['HTPoff.txt']['Total'][aoa]['CLift']]))
                         
    errorcx = Total [0]  - ForwardSumCx - RearSumCx
    errorcy = Total [1]  - ForwardSumCx - RearSumCy
    errorcz = Total [2]  - ForwardSumCx - RearSumCz
    
    ws.write(row + lenn +2,col+1,'Forward')
    ws.write(row + lenn +3,col+1,'Rear')
    ws.write(row + lenn +4,col+1,'Error')
    fwd_value = row + lenn + 3
    rear_value = row + lenn +4
    
    ws.write(row + lenn +2, col+2,ForwardSumClift)
    ws.write(row + lenn +2, col+3,ForwardSumCdrag)
    ws.write(row + lenn +2, col+4,ForwardSumCside)
    ws.write(row + lenn +2, col+5,ForwardSumArea)
    ws.write(row + lenn +2, col+7,ForwardSumCx)
    ws.write(row + lenn +2, col+8,ForwardSumCy)
    ws.write(row + lenn +2, col+9,ForwardSumCz)
    
              
    ws.write(row + lenn +3, col+2,RearSumClift)
    ws.write(row + lenn +3, col+3,RearSumCdrag)
    ws.write(row + lenn +3, col+4,ReardSumCside)
    ws.write(row + lenn +3, col+5,RearSumArea)
    ws.write(row + lenn +3, col+7,RearSumCx)
    ws.write(row + lenn +3, col+8,RearSumCy)
    ws.write(row + lenn +3, col+9,RearSumCz)
    
    
    ws.write(row + lenn +4, col+2,errorClift)
    ws.write(row + lenn +4, col+3,errorCdrag)
    ws.write(row + lenn +4, col+4,errorCside)
    ws.write(row + lenn +4, col+5,errorArea)
    ws.write(row + lenn +4, col+7,errorCx)
    ws.write(row + lenn +4, col+8,errorCy)
    ws.write(row + lenn +4, col+9,errorCz)
    
    
    row = row + lenn +7
    
    ws.write(row,col,'Surfacepart')
    ws.write(row,col+1,'name')         
    ws.write(row,col+2 ,'CMx')      
    ws.write(row,col+3 ,'CMy')     
    ws.write(row,col +4,'CMz')       
    ws.write(row,col +5,'Area%')       
    ws.write(row,col+7 ,'CM_x' )      
    ws.write(row,col +8 ,'CM_y')     
    ws.write(row,col +9 ,'CM_z') 
    
       
    row row+1
    CM_values = row+1
    for idx,m in enumerate(self.__addMarkers + Markers):
        # print(idx,m)
        
        marker_len=len(self.__addMarkers + markers)
        ws.write(row+idx,col,'bdy_part')
        ws.write(row+idx,col+1,m)
        ws.write(row+idx,col+2,round(float(self.mData[file][m][aoa]['CM_x']),8))
        ws.write(row+idx,col+3,round(float(self.mData[file][m][aoa]['CM_y']),8))
        ws.write(row+idx,col+4,round(float(self.mData[file][m][aoa]['CM_z']),8))
        ws.write(row+idx,col+5,round(float(self.mData[file][m][aoa]['Area']),8))
        
        forceBodyAxis = np.dot(ABW,
                    np.array([-float(self.__mdata[file][m][aoa]['CDrag']),float(self.__mData[file][m][aoa]['CSideF']),
                              -float(self.__mData[file][m][aoa]['CLift'])]))
        
       momentBodyAxisX = forceBodyAxis[1]*self.__ABbyCref[2] - \
                                      forceBodyAxis[2]*self.__ABbyCref[1] - \
                                          float(self.__mData[file][m][aoa]['CM_x'])/float(self.__dictt['cref_XZ'])
                                          
        momentBodyAxisY = forceBodyAxis[2]*self.__ABbyCref[0] - \
                                       forceBodyAxis[1]*self.__ABbyCref[0] - \
                                           float(self.__mData[file][m][aoa]['CM_y'])
                                           
                                           
        momentBodyAxisZ = forceBodyAxis[0]*self.__ABbyCref[1] - \
                                       forceBodyAxis[0]*self.__ABbyCref[0] - \
                                           float(self.__mData[file][m][aoa]['CM_z'])/float(self.__dictt['cref_XZ'])
                                           
        
        
        ws.write(row+idx,col+7,round(momentBodyAxisX,8))
        ws.write(row+idx,col+8,round(momentBodyAxisY,8))
        ws.write(row+idx,col+9,round(momentBodyAxisZ,8))
        
        
        errorCmx = float(self.__mData[file]['Total'][aoa]['CM_x']) - ForwardSumCmx -RearSumCmx
        errorCmy = float(self.__mData[file]['Total'][aoa]['CM_y']) - ForwardSumCmy -RearSumCmy
        errorCmz = float(self.__mData[file]['Total'][aoa]['CM_z']) - ForwardSumCmz -RearSumCmz
        
        
        momentBodyAxisXc = Totalc[1]*self.__ABbyCref[2] - \
                                          Totalc[2]*self.__ABbyCref[1] - \
                                              float(self.__mData[file]['Total'][aoa]['CM_x'])/float(self.dictt['cref_XZ'])
        
        
        momentBodyAxisYc = Totalc[2]*self.__ABbyCref[0] - \
                                          Totalc[0]*self.__ABbyCref[2] - \
                                              float(self.__mData[file]['Total'][aoa]['CM_y'])
        
        
        
        momentBodyAxisZc = Totalc[0]*self.__ABbyCref[1] - \
                                          Totalc[1]*self.__ABbyCref[0] - \
                                              float(self.__mData[file]['Total'][aoa]['CM_z'])/float(self.dictt['cref_XZ'])
        
        
        
        momentBodyAxisYcHTPoff = TotalcHTPoff[2]*self.__ABbyCref[0] - \
                                          TotalcHTPoff[0]*self.__ABbyCref[2] - \
                                              float(self.__mData['HTPoff.txt']['Total'][aoa]['CM_y'])
                                              
                                              
        errorcmxt = momentBodyAxisXc - ForwardSumCmxt -RearSumCmxt
        errorcmyt = momentBodyAxisYc - ForwardSumCmyt -RearSumCmyt
        errorcmzt = momentBodyAxisZc - ForwardSumCmzt -RearSumCmzt
        
        ws.write(row + lenn + 2,col+1,'Forward')
        ws.write(row + lenn + 3,col+1,'Rear')
        ws.write(row + lenn + 4,col+1,'Error')
        
        cm_fwd_val =row + lenn +3
        cm_rear_val = row +lenn +4
        
        
        ws.write(row + lenn + 2,col+2,round(ForwardSumCmx,8))
        ws.write(row + lenn + 2,col+3,round(ForwardSumCmy,8))
        ws.write(row + lenn + 2,col+4,round(ForwardSumCmz,8))
        ws.write(row + lenn + 2,col+5,round(ForwardSumArea,8))
        ws.write(row + lenn + 2,col+7,round(ForwardSumCmxt,8))
        ws.write(row + lenn + 2,col+8,round(ForwardSumCmyt,8))
        ws.write(row + lenn + 2,col+9,round(ForwardSumCmzt,8))
        
        ws.write(row + lenn + 3,col+2,round(RearSumCmx,8))
        ws.write(row + lenn + 3,col+3,round(RearSumCmy,8))
        ws.write(row + lenn + 3,col+4,round(RearSumCmz,8))
        ws.write(row + lenn + 3,col+5,round(RearSumArea,8))
        ws.write(row + lenn + 3,col+7,round(RearSumCmxt,8))
        ws.write(row + lenn + 3,col+8,round(RearSumCmyt,8))
        ws.write(row + lenn + 3,col+9,round(RearSumCmzt,8))
        
        ws.write(row + lenn + 4,col+2,round(errorCmx,8))
        ws.write(row + lenn + 4,col+3,round(errorCmy,8))
        ws.write(row + lenn + 4,col+4,round(errorCmz,8))
        ws.write(row + lenn + 4,col+5,round(errorArea,8))
        ws.write(row + lenn + 4,col+7,round(errorCmxt,8))
        ws.write(row + lenn + 4,col+8,round(errorCmyt,8))
        ws.write(row + lenn + 4,col+9,round(errorCmzt,8))
        
        row = row + lenn + 7
        
        rowTmp = rowTmp+1
        ws.write(rowTmp,colTmp +15,float(aoa))
        # print(float(aoa))
        ws.write(rowTmp,colTmp +16,float(beta))
        
        if file != 'HTPoff.txt':
            ws.write(rowTmp,colTmp+17,float(self.__ihDict[file]))
        else:
            ws.write(rowTmp,colTmp+17,(self.__ihDict[file]))
            
        
        ws.write(rowTmp,colTmp+18,round(self.__fac*float(self.__mData[file]['Total'][aoa]['CLift']),8))
        ws.write(rowTmp,colTmp+19,round(self.__fac*float(self.__mData[file]['Total'][aoa]['CDrag']),8))
        ws.write(rowTmp,colTmp+20,round(self.__fac*float(self.__mData[file]['Total'][aoa]['CSideF']),8))
        ws.write(rowTmp,colTmp+21,round(float(self.__mData[file]['Total'][aoa]['Area']),8))
        ws.write(rowTmp,colTmp+22,round(self.__fac*10000*float(self.__mData[file]['Total'][aoa]['CDrag']),8))
        ws.write(rowTmp,colTmp+23,round(self.__fac*Totalc[0],8))
        ws.write(rowTmp,colTmp+24,round(self.__fac*Totalc[1],8))
        ws.write(rowTmp,colTmp+25,round(self.__fac*Totalc[2],8))
        ws.write(rowTmp,colTmp+26,round(self.__fac*momentBodyAxisXc,8))
        ws.write(rowTmp,colTmp+27,round(self.__fac*momentBodyaxisYc,8))
        ws.write(rowTmp,colTmp+28,round(self.__fac*momentBodyAxisZc,8))
        
        CLHs=self.__fac*float(self.__mData[file]['Total'][aoa]['CLift'])-self.__fac*float(self.__mData['HTPoff.txt']['Total'][aoa]['CLift'])
        CDHs=self.__fac*float(self.__mData[file]['Total'][aoa]['CDrag'])-self.__fac*float(self.__mData['HTPoff.txt']['Total'][aoa]['CDrag'])
        
        ws.write(rowTmp,colTmp+30,round(CLHs,8))
        # print(rowTmp,colTmp+30,round(CLHs,8))
        ws.write(rowTmp,colTmp+31,round(CDHs,8))
        ws.write(rowTmp,colTmp+32,round(self.__fac*momentBodyAxisYc-self.__fac*momentBodyAxisYcHTPoff,8))
        ws.write(rowTmp,colTmp+34,round(epsac,8))
        
        
        vecac = np.dot(self.__rotMatrix([0,0,1],epsac),np.array([CDHs,CLHs,0]))
        
        CDHac = vecac[0]*float(self.__dictt['SW'])/float(self.__dictt['SHTP'])
        
        CLHs1=self.__fac*RearSumClift-self.__fac*RearSumCliftHTPoff
        CMys1=self.__fac*RearSumCmyt-self.__fac*RearSumCmytHTPoff
        CDHs1=self.__fac*RearSumCdrag-self.__fac*RearSumCdragHTPoff
        vecr = np.dot(self.__rotMatrix([0,0,1],epsr),np.array([CDHs1,CLHs1,0]))
        CDHr = vecr[0]*float(self.__dictt['SW'])/float(self.dictt['SHTP'])
        CLHr = vecr[1]*float(self.__dictt['SW'])/float(self.dictt['SHTP'])
        
        try:
            alpha_Hac = float(aoa) - epsac +float(self.__ihDict[file])
            # print(alpha_Hac)
            alpha_Hr = float(aoa) - epsr +float(self.__ihDict[file])
        
            CLHexp = 0
            for m in self.__markersHTP:
                CLHexp = CLHexp + float(self.__mData[file][m][aoa]['CLift'])
            
            CLHexpSH = CLHexp*float(self.__dictt['SW'])/float(self.__dictt['SHTP'])
            CDHana= CDH0 + (k/(np.pi*AR))*(CLHr-CLH0)**2
        except:
            alpha_Hac = "NA"
            alpha_Hr = "NA"
            CLHexp = "NA"
            CLHexpSH = "NA"
            CDHana = "NA"
            
            
        CDmCLsbyPiAR = self.__fac*float(self.__mData[file]['Total'][aoa]['CDrag']) - \
            ((self.__fac*float(self.__mData[file]['Total'][aoa]['CLift']))**2/(np.pi*float(self.__dictt['AspectRatio'])))
            
        ws.write(rowTmp,colTmp+36,round(vecac[0],8))
        ws.write(rowTmp,colTmp+37,round(vecac[1],8))        
        ws.write(rowTmp,colTmp+39,round(CDHac,8))
        # print(CDHac)
        ws.write(rowTmp,colTmp+40,round(CLHac,8))
        ws.write(rowTmp,colTmp+41,round(CDmCLsbyPiAR,8))
        
        
        if file != "HTPoff.txt":
            lHbyCref = -(CMys1-cmH0)/CLHs1
            VH = lHbyCref*float(self.__dictt['SHTP'])/float(self.__dictt['SW'])
        else:
            lHbyCref = "NA"
            VH = "NA"
            
        rowTmp = rowTmp + len(self._aoaLst) + 5
        length_aoaLst = len(self.__aoaLst) + 4
        ws.write(rowTmp,colTmp+15,float(aoa))
        ws.write(rowTmp,colTmp+16,float(beta))
        
        if file!= 'HTPoff.txt':
            ws.write(rowTmp,colTmp+17,float(self.__ihDict[file]))
        else:
            ws.write(rowTmp,colTmp+17,self.__ihDict[file])
            
        ws.write(rowTmp,colTmp+18,round(self.__fac*RearSumClift,8))
        ws.write(rowTmp,colTmp+19,round(self.__fac*RearSumCDrag,8))
        ws.write(rowTmp,colTmp+20,round(self.__fac*RearSumCside,8))         
        ws.write(rowTmp,colTmp+21,round(RearSumArea,8))       
        ws.write(rowTmp,colTmp+22,round(self.__fac*10000*RearSumCdrag,8))        
        ws.write(rowTmp,colTmp+23,round(self.__fac*RearSumCx,8))       
        ws.write(rowTmp,colTmp+24,round(self.__fac*RearSumCy,8))         
        ws.write(rowTmp,colTmp+25,round(self.__fac*RearSumCz,8))  
        ws.write(rowTmp,colTmp+26,round(self.__fac*RearSumCmXt,8))          
        ws.write(rowTmp,colTmp+27,round(self.__fac*RearSumCmyt,8))          
        ws.write(rowTmp,colTmp+28,round(self.__fac*RearSumCmzt,8)) 
        
        
        ws.write(rowTmp,colTmp+30,round(CLHs1,8)         
        ws.write(rowTmp,colTmp+31,round(CDHs1,8)        
        ws.write(rowTmp,colTmp+32,round(CMys1,8)       
        ws.write(rowTmp,colTmp+34,round(epsr,8)       
        ws.write(rowTmp,colTmp+35,alpha_Hr)        
        ws.write(rowTmp,colTmp+36,round(vecr[0],8))         
        ws.write(rowTmp,colTmp+37,round(vecr[1],8))       
        ws.write(rowTmp,colTmp+39,round(CDHr,8))
        ws.write(rowTmp,colTmp+40,round(CLHr,8))
        
        try:
            ws.write(rowTmp,colTmp+41,round(self.__fac*CLHexp,8))
            ws.write(rowTmp,colTmp+42,round(VH,8))
            ws.write(rowTmp,colTmp+43,round(lHbyCref,8))
            ws.write(rowTmp,colTmp+44,round(self.__fac*CLHexpSH,8))
            ws.write(rowTmp,colTmp+45,round(CDHana,8))
        else:
            ws.write(rowTmp,colTmp+41,'NA')
            ws.write(rowTmp,colTmp+42,'NA')
            ws.write(rowTmp,colTmp+43,'NA')
            ws.write(rowTmp,colTmp+44,'NA')
            ws.write(rowTmp,colTmp+45,'NA')
            
      rowTmp = rowTmp + len(self.__aoaLst) + 5
      length_aoaLst = len(self.__aoaLst) + 4
      ws.write(rowTmp,colTmp+15,float(aoa))
      ws.write(rowTmp,colTmp+16,float(beta))
      
      if file != 'HTPoff.txt':
          ws.write(rowTmp,colTmp+17,self.__ihDict[file])
          
      ws.write(rowTmp,colTmp+18,round(self.__fac*ForwardSumClift,8))
      ws.write(rowTmp,colTmp+19,round(self.__fac*ForwardSumCdrag,8))
      ws.write(rowTmp,colTmp+20,round(self.__fac*ForwardSumCside,8))
      ws.write(rowTmp,colTmp+21,round(ForwardSumArea,8))
      ws.write(rowTmp,colTmp+22,round(self.__fac*10000*ForwardSumCdrag,8))
      ws.write(rowTmp,colTmp+23,round(self.__fac*ForwardSumCx,8))
      ws.write(rowTmp,colTmp+24,round(self.__fac*ForwardSumCy,8))
      ws.write(rowTmp,colTmp+25,round(self.__fac*ForwardSumCz,8))
      ws.write(rowTmp,colTmp+26,round(self.__fac*ForwardSumCmxt,8))
      ws.write(rowTmp,colTmp+27,round(self.__fac*ForwardSumCmyt,8))
      ws.write(rowTmp,colTmp+28,round(self.__fac*ForwardSumCmzt,8))
      ws.write(rowTmp,colTmp+30,round(self.__fac*ForwardSumClift-self.__fac*ForwardSumCliftHTPoff,8))
      ws.write(rowTmp,colTmp+31,round(self.__fac*ForwardSumCdrag-self.__fac*ForwardSumCdragHTPoff,8))
      ws.write(rowTmp,colTmp+32,round(self.__fac*ForwardSumCmy-self.__fac*ForwardSumCmyHTPoff,8))
      
      
      return row,col
      
 ##################################################################################

      def __addPlots(self,wb,ws,file):
          
          lno = 10
          offset = 5
          laoa = len(self.__aoaLst)
          rlno = lno + laoa + offset
          flno = lno + 2*laoa +2 *offset
          # print(laoa)
          
          chart1 = wb.add_chart({'type' : 'line'})
          chart2 = wb.add_chart({'type' : 'line'})
          chart3 = wb.add_chart({'type' : 'line'})
          chart4 = wb.add_chart({'type' : 'line'})
          chart5 = wb.add_chart({'type' : 'line'})
          chart6 = wb.add_chart({'type' : 'line'})
          chart7 = wb.add_chart({'type' : 'line'})
          chart8 = wb.add_chart({'type' : 'line'})
          
          chart1.add_series({'name':'CL', 'categories':file + '!$Q$' + str(lno) +':$Q$' + str(lno+laoa-1),'values' : file + '!$T$' +str(lno) + ':$T$' +str(lno+laoa-1),'markers':{'type':'square'}})
          chart1.add_series({'name':'CZ', 'categories':file + '!$Q$' + str(lno) +':$Q$' + str(lno+laoa-1),'values' : file + '!$AA$' +str(lno) + ':$AA$' +str(lno+laoa-1),'markers':{'type':'square'}})
          chart2.add_series({'name':'CD', 'categories':file + '!$Q$' + str(lno) +':$Q$' + str(lno+laoa-1),'values' : file + '!$U$' +str(lno) + ':$U$' +str(lno+laoa-1),'markers':{'type':'square'}})
          chart2.add_series({'name':'CX', 'categories':file + '!$Q$' + str(lno) +':$Q$' + str(lno+laoa-1),'values' : file + '!$Y$' +str(lno) + ':$Y$' +str(lno+laoa-1),'markers':{'type':'square'}})
          chart3.add_series({'name':'CS', 'categories':file + '!$Q$' + str(lno) +':$Q$' + str(lno+laoa-1),'values' : file + '!$V$' +str(lno) + ':$V$' +str(lno+laoa-1),'markers':{'type':'square'}})
          chart3.add_series({'name':'CY', 'categories':file + '!$Q$' + str(lno) +':$Q$' + str(lno+laoa-1),'values' : file + '!$Z$' +str(lno) + ':$Z$' +str(lno+laoa-1),'markers':{'type':'square'}})
          chart4.add_series({'name':'CMx, 'categories':file + '!$Q$' + str(lno) +':$Q$' + str(lno+laoa-1),'values' : file + '!$AB$' +str(lno) + ':$AB$' +str(lno+laoa-1),'markers':{'type':'square'}})
          chart5.add_series({'name':'CMy', 'categories':file + '!$Q$' + str(lno) +':$Q$' + str(lno+laoa-1),'values' : file + '!$AC$' +str(lno) + ':$AC$' +str(lno+laoa-1),'markers':{'type':'square'}})
          chart6.add_series({'name':'CMz', 'categories':file + '!$Q$' + str(lno) +':$Q$' + str(lno+laoa-1),'values' : file + '!$AD$' +str(lno) + ':$AD$' +str(lno+laoa-1),'markers':{'type':'square'}})
          chart7.add_series({'name':'CLH*', 'categories':file + '!$Q$' + str(lno) +':$Q$' + str(lno+laoa-1),'values' : file + '!$AF$' +str(lno) + ':$AF$' +str(lno+laoa-1),'markers':{'type':'square'}})
          chart8.add_series({'name':'CLH', 'categories':file + '!$Q$' + str(lno) +':$Q$' + str(lno+laoa-1),'values' : file + '!$AC$' +str(lno) + ':$AC$' +str(lno+laoa-1),'markers':{'type':'square'}})
          
          
          chart1.set_x_axis({'name':'Alpha(deg)','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
          chart1.set_y_axis({'name' :'CL,CZ'})
          chart2.set_x_axis({'name':'Alpha(deg)','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
          chart2.set_y_axis({'name' :'CD,CX'})
          chart3.set_x_axis({'name':'Alpha(deg)','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
          chart3.set_y_axis({'name' :'CS,CY'})
          chart4.set_x_axis({'name':'Alpha(deg)','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
          chart4.set_y_axis({'name' :'CMx'})
          chart5.set_x_axis({'name':'Alpha(deg)','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
          chart5.set_y_axis({'name' :'CMy'})
          chart6.set_x_axis({'name':'Alpha(deg)','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
          chart6.set_y_axis({'name' :'CMz'})
          chart7.set_x_axis({'name':'Alpha(deg)','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
          chart7.set_y_axis({'name' :'CLH*'})
          chart8.set_x_axis({'name':'Alpha(deg)','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
          chart8.set_y_axis({'name' :'Fwd CMy'})
          
          plotStartNo = lno +(laoa+1)*3 +2*offset + 2
          
          
          ws.insert_chart('Q' + str(plotStartNo),chart1)
          ws.insert_chart('Q' + str(plotStartNo+16),chart2)
          ws.insert_chart('Q' + str(plotStartNo+32),chart3)
          ws.insert_chart('Z' + str(plotStartNo),chart4)
          ws.insert_chart('Z' + str(plotStartNo+16),chart5)
          ws.insert_chart('Z' + str(plotStartNo+32),chart6)
          ws.insert_chart('Z' + str(plotStartNo+48),chart7)
          ws.insert_chart('AI' + str(plotStartNo+48),chart8)
          
          if file != "HTPoff.txt":
              chart9 = wb.add_chart({'type':'line'})
              chart9.add_series({'name':'CLHexp', 'categories':file + '!$AK$' + str(rlno) +':$AK$' + str(rlno+laoa-1),'values' : file + '!$AP$' +str(rlno) + ':$AP$' +str(rlno+laoa-1),'markers':{'type':'square'}})
              
              chart9.set_x_axis({'name':'AlphaH(deg)','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
              chart9.set_y_axis({'name' :'Fwd CLH'})
              
              ws.insert_chart('Q' + str(plotStartNo+48),chart9)

###############################################################################################################################

       def __addHTPoffPlots(self,wb,ws,ihoAC,ih0R,coeffAC,coeffR,epsilon_altepAC,epsilon_altepR):
           
           lno = 10
           offset = 5
           laoa = len(self.__aoaLst)
           rlno = lno + laoa + offset
           flno = lno + 2*laoa +2 *offset
           
           AR_AC = float(self.__dictt['AspectRatio'])
           a_AC = coeffAC[2]
           b_AC = coeffAC[1]
           c_AC = coeffAC[0]
           
           k_AC = a_AC*np.pi*AR_AC
           CL0 = -b_AC*np.pi*AR_AC/(2*k_AC)
           CD0 = c_AC - (k_AC/(np.pi*AR_AC))*CL0*2
           
           AR_R = float(self.__dictt['AspectRatioTail'])
           a_R = coeffR[2]
           b_R = coeffR[1]
           c_R = coeffR[0]
           
           k_R = a_R*np.pi*AR_R
           CLH0 = -b_R*np.pi*AR_R/(2*k_R)
           CDH0 = c_R - (k_R/np.pi*AR_R))*CLH0**2
                             
           ws.write('AV9','ih0AC')                 
           ws.write('AT9','ih0R')
           ws.write('AX9','CLH-CDH(ax2+bx+c)')
           ws.write_column('AX' +str(lno),['c','b','a','rsq'])
           ws.write_column('BA' +str(lno), ['AR','k','CL0','CD0'])
           ws.write_column('AX' +str(rlno), ['c','b','a','rsq'])
           ws.write_column('BA' +str(rlno),['AR','k','CLH0','CDH0'])
           ws.write('BD9','eps_Alt_AC')
           ws.write('BE9','eps_Alt_REAR')
           
           ws.write_column('AV' +str(lno),ih0AC)
           ws.write_column('AT' +str(lno),ih0R)
           ws.write_column('AY' +str(lno),coeffAc)
           ws.write_column('BB' +str(lno),[AR_AC,k_AC,CL0,CD0]
           ws.write_column('AY' +str(rlno),coeffR)
           ws.write_column('BB' +str(rlno),[AR_R,k_R,CLH0,CDH0])
           ws.write_column('BD' +str(lno), epsilon_altepAC)              
           ws.write_column('BE' +str(lno), epsilon_altepR)
           
           chart1 = wb.add_chart({'type' : 'line'})
           chart2 = wb.add_chart({'type' : 'line'})
           chart3 = wb.add_chart({'type' : 'line'})
           chart4 = wb.add_chart({'type' : 'line'})
           chart5 = wb.add_chart({'type' : 'line'})
           chart6 = wb.add_chart({'type' : 'line'})
           chart7 = wb.add_chart({'type' : 'line'})
           chart8 = wb.add_chart({'type' : 'line'})
           chart9 = wb.add_chart({'type' : 'line'})
           chart10 = wb.add_chart({'type' : 'line'})
           chart11 = wb.add_chart({'type' : 'scatter'})
           chart12 = wb.add_chart({'type' : 'scatter'})
           chart13 = wb.add_chart({'type' : 'scatter'})
           
           for file in self.__files:
               chart1.add_series({'name':'file', 'categories':file + '!$Q$' + str(lno) +':$Q$' + str(lno+laoa-1),'values' : file + '!$AC$' +str(lno) + ':$AC$' +str(lno+laoa-1),'markers':{'type':'square'}})
               chart2.add_series({'name':'file', 'categories':file + '!$Q$' + str(lno) +':$Q$' + str(lno+laoa-1),'values' : file + '!$T$' +str(lno) + ':$T$' +str(lno+laoa-1),'markers':{'type':'square'}})
               chart3.add_series({'name':'file', 'categories':file + '!$Q$' + str(rlno) +':$Q$' + str(rlno+laoa-1),'values' : file + '!$T$' +str(rlno) + ':$T$' +str(rlno+laoa-1),'markers':{'type':'square'}})
               chart4.add_series({'name':'file', 'categories':file + '!$Q$' + str(rlno) +':$Q$' + str(rlno+laoa-1),'values' : file + '!$AF$' +str(rlno) + ':$AF$' +str(rlno+laoa-1),'markers':{'type':'square'}})
               chart5.add_series({'name':'file', 'categories':file + '!$T$' + str(lno) +':$T$' + str(lno+laoa-1),'values' : file + '!$AC$' +str(lno) + ':$AC$' +str(lno+laoa-1),'markers':{'type':'square'}})
               chart6.add_series({'name':'file', 'categories':file + '!$T$' + str(lno) +':$T$' + str(lno+laoa-1),'values' : file + '!$AP$' +str(lno) + ':$AP$' +str(lno+laoa-1),'markers':{'type':'square'}})
               chart7.add_series({'name':'file', 'categories':file + '!$Q$' + str(lno) +':$Q$' + str(lno+laoa-1),'values' : file + '!$U$' +str(lno) + ':$U$' +str(lno+laoa-1),'markers':{'type':'square'}})
               chart8.add_series({'name':'file', 'categories':file + '!$Q$' + str(rlno) +':$Q$' + str(rlno+laoa-1),'values' : file + '!$U$' +str(rlno) + ':$U$' +str(rlno+laoa-1),'markers':{'type':'square'}})
               chart9.add_series({'name':'file', 'categories':file + '!$Q$' + str(lno) +':$Q$' + str(lno+laoa-1),'values' : file + '!$AG$' +str(lno) + ':$AG$' +str(lno+laoa-1),'markers':{'type':'square'}})
               chart9.add_series({'name':'file', 'categories':file + '!$Q$' + str(rlno) +':$Q$' + str(rlno+laoa-1),'values' : file + '!$AG$' +str(rlno) + ':$AG$' +str(rlno+laoa-1),'markers':{'type':'square'}})
               chart10.add_series({'name':'file', 'categories':file + '!$Q$' + str(rlno) +':$Q$' + str(rlno+laoa-1),'values' : file + '!$AJ$' +str(rlno) + ':$AJ$' +str(rlno+laoa-1),'markers':{'type':'square'}})
               
               chart11.add_series({'name':'file'+"_AC", 'categories':file + '!$AK$' + str(lno) +':$AK$' + str(lno+laoa-1),'values' : file + '!$AP$' +str(lno) + ':$AP$' +str(lno+laoa-1),'markers':{'type':'square'}})
               chart11.add_series({'name':'file'+"_R", 'categories':file + '!$AK$' + str(rlno) +':$AK$' + str(rlno+laoa-1),'values' : file + '!$AP$' +str(rlno) + ':$AP$' +str(rlno+laoa-1),'markers':{'type':'square'}})
               chart12.add_series({'name':'file'+"_AC", 'categories':file + '!$AP$' + str(lno) +':$AP$' + str(lno+laoa-1),'values' : file + '!$AO$' +str(lno) + ':$AO$' +str(lno+laoa-1),'markers':{'type':'square'}})
               chart12.add_series({'name':'file'+"_R", 'categories':file + '!$AP$' + str(rlno) +':$AP$' + str(rlno+laoa-1),'values' : file + '!$AO$' +str(rlno) + ':$AO$' +str(rlno+laoa-1),'markers':{'type':'square'}})
               chart13.add_series({'name':'file'+"_AC", 'categories':file + '!$AF$' + str(lno) +':$AF$' + str(lno+laoa-1),'values' : file + '!$AH$' +str(lno) + ':$AH$' +str(lno+laoa-1),'markers':{'type':'square'}})
               chart13.add_series({'name':'file'+"_R", 'categories':file + '!$AF$' + str(rlno) +':$AF$' + str(rlno+laoa-1),'values' : file + '!$AH$' +str(rlno) + ':$AH$' +str(rlno+laoa-1),'markers':{'type':'square'}})
               
               
               chart1.set_x_axis({'name':'Alpha(deg)','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
               chart1.set_y_axis({'name' :'CMy'})
               chart2.set_x_axis({'name':'Alpha(deg)','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
               chart2.set_y_axis({'name' :'CL'})
               chart3.set_x_axis({'name':'Alpha(deg)','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
               chart3.set_y_axis({'name' :'CLrear'})
               chart4.set_x_axis({'name':'Alpha(deg)','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
               chart4.set_y_axis({'name' :'CLH*'})
               chart5.set_x_axis({'name':'CL','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
               chart5.set_y_axis({'name' :'CMy'})
               chart6.set_x_axis({'name':'CL','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
               chart6.set_y_axis({'name' :'CLH'})
               chart7.set_x_axis({'name':'Alpha(deg)','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
               chart7.set_y_axis({'name' :'CD'})
               chart8.set_x_axis({'name':'Alpha(deg)','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
               chart8.set_y_axis({'name' :'CDrear'})
               chart9.set_x_axis({'name':'Alpha(deg)','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
               chart9.set_y_axis({'name' :'CDH*'})
               chart10.set_x_axis({'name':'Alpha(deg)','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
               chart10.set_y_axis({'name' :'EPS(Rear'})
               chart11.set_x_axis({'name':'Alpha(deg)','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
               chart11.set_y_axis({'name' :'CLH'})
               chart12.set_x_axis({'name':'CLH','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
               chart12.set_y_axis({'name' :'CDH'})
               chart13.set_x_axis({'name':'CLH*','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
               chart13.set_y_axis({'name' :'CMH*'})
               

               
               plotStartNo = lno +(laoa+1)*3 +2*offset + 2
               
               ws.insert_chart('AH' + str(plotStartNo),chart1)
               ws.insert_chart('AH' + str(plotStartNo+16),chart2)
               ws.insert_chart('AH' + str(plotStartNo+32),chart3)
               ws.insert_chart('AH' + str(plotStartNo+48),chart4)
               ws.insert_chart('AH' + str(plotStartNo+64),chart5)
               ws.insert_chart('AH' + str(plotStartNo+80),chart6)
               ws.insert_chart('AQ' + str(plotStartNo),chart7)
               ws.insert_chart('AQ' + str(plotStartNo+16),chart8)
               ws.insert_chart('AQ' + str(plotStartNo+32),chart9)
               ws.insert_chart('AQ' + str(plotStartNo+48),chart10)
               ws.insert_chart('AZ' + str(plotStartNo),chart11)
               ws.insert_chart('AZ' + str(plotStartNo+16),chart12)
               ws.insert_chart('AZ' + str(plotStartNo+32),chart13)
               
###########################################################################################





#################################################################################
      def __addPlotss(self,wb,ws):
          lno = 10
          offset = 5
          laoa = len(self.__aoaLst)
          rlno = lno + laoa + offset
          flno = lno + 2*laoa +2 *offset
          
          
          chart1 = wb.add_chart({'type' : 'scatter'})
          chart2 = wb.add_chart({'type' : 'scatter'})
          chart3 = wb.add_chart({'type' : 'scatter'})
          
          for file in self.__files:
              print(files)
              
              chart1.add_series({'name':'file'+"_AC", 'categories':file + '!$AK$' + str(lno) +':$AK$' + str(lno+laoa-1),'values' : file + '!$AP$' +str(lno) + ':$AP$' +str(lno+laoa-1),'markers':{'type':'square'}})
              chart1.add_series({'name':'file'+"_R", 'categories':file + '!$AK$' + str(rlno) +':$AK$' + str(rlno+laoa-1),'values' : file + '!$AP$' +str(rlno) + ':$AP$' +str(rlno+laoa-1),'markers':{'type':'square'}})
              chart2.add_series({'name':'file'+"_AC", 'categories':file + '!$AP$' + str(lno) +':$AP$' + str(lno+laoa-1),'values' : file + '!$AO$' +str(lno) + ':$AO$' +str(lno+laoa-1),'markers':{'type':'square'}})
              chart2.add_series({'name':'file'+"_R", 'categories':file + '!$AP$' + str(rlno) +':$AP$' + str(rlno+laoa-1),'values' : file + '!$AO$' +str(rlno) + ':$AO$' +str(rlno+laoa-1),'markers':{'type':'square'}})
              chart3.add_series({'name':'file'+"_AC", 'categories':file + '!$AF$' + str(lno) +':$AF$' + str(lno+laoa-1),'values' : file + '!$AH$' +str(lno) + ':$AH$' +str(lno+laoa-1),'markers':{'type':'square'}})
              chart3.add_series({'name':'file'+"_R", 'categories':file + '!$AF$' + str(rlno) +':$AF$' + str(rlno+laoa-1),'values' : file + '!$AH$' +str(rlno) + ':$AH$' +str(rlno+laoa-1),'markers':{'type':'square'}})
              
              
          chart1.set_x_axis({'name':'Alpha(deg)','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
          chart1.set_y_axis({'name' :'CLH'})
          chart2.set_x_axis({'name':'CLH','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
          chart2.set_y_axis({'name' :'CDH'})
          chart3.set_x_axis({'name':'CLH*','major_gridlines' : {'visible' : True,'line' : {'width': 0.1}}, 'minor_gridlines' : {'visible' : True, 'line':{'width' : 0.01}}})
          chart3.set_y_axis({'name' :'CMH*'})
          
          ws.insert_chart('B' + str(plotStartNo),chart1)
          ws.insert_chart('B' + str(plotStartNo+16),chart2)
          ws.insert_chart('B' + str(plotStartNo+32),chart3)



#####################################################################
       def generateExcel(self):
           self.__ihDict                  = self.__getIH()
           wb                             =xl.Workbook(self.__outputPath+"/"+self.__dictt['name'] + "_M_"+self.__dictt['Mach']+"NF"+".xlsx",{'use_future_functions':True})
           
           
           wsIH                           = [wb.add_worksheet(name=string) for string in self.__files]
           self.__markersHTPon            = [val.strip() for va in self.__dictt['Rear_HTPon_markers'].split(',')]
           self.__markersHTPoff            = [val.strip() for va in self.__dictt['Rear_HTPoff_markers'].split(',')]
           
           self.markersHTP                = list(set(self.__markersHTPon)^set(self.markersHTPoff))
           self.__addMarkers              = ['Total']
           self.__dictt['Additional_Markers'] = self.__addMarkers
           
           # print(self.__ihDict)
           
           for m in self.__markersHTPon:
               if m in self.__fwdMarkers:
                   self.__fwdMarkers.remove(m)
                   
          # print(self.__fwdMarkers)
          
           self.__getAOAlst()
           cfdOrg                        = np.array([float(val)for val in self.__dictt['FrameOriginCFD'].split(',')])
           postOrg                        = np.array([float(val)for val in self.__dictt['FrameOriginPost'].split(',')])
           self.__ABbyCref                = (cfdOrg - postOrg)/float(self.__dictt['cref_Y'])
           self.__ABbyCref                = np.array([-self.__ABbyCref[0],self.ABbyCref[1]-self.__ABbyCref[2]])
           
           for idx,ws in enumerate(wsIH):
               # print(idx,ws)
               
               ws.write('A2','Sref')
               ws.write('A3','cref')
               ws.write('A5','SH')
               ws.write('A6','AR')
               ws.write('A7','CH')
               ws.write('F2','FrameOriginCFD')
               ws.write('F3','FrameOriginPost')
               ws.write('F4','MomentArm/Cref')
               
               ws.write('B2',float(self.__dictt['SW']))
               ws.write('B3',float(self.__dictt['cref_Y']))
               ws.write('B5',float(self.__dictt['SHTP']))
               ws.write('B6',float(self.__dictt['AspectRatio']))
               ws.write('B7',float(self.__dictt['cHTP']))
               
               ws.write_row('G2',cfdOrg)
               ws.write_row('G3',postOrg)
               ws.write_row('G4',self.__ABbyCref)
               
            if self.__fles[idx] == 'HTPoff.txt':
                self.mData[self.__files[idx]] = {}
                self.mData[self.__files[idx]] = self.getIHdata(self.__outputPath + "/" +self.__files[idx],self.__addMarkers + self.__fwdMarkers + self.__markersHTPoff)
            else:
                self.mData[self.__files[idx]] = {}
                self.mData[self.__files[idx]] = self.getIHdata(self.__outputPath + "/" +self.__files[idx],self.__addMarkers + self.__fwdMarkers + self.__markersHTPon)
           
            # print(self.__mData)
            
            HTPmainInpFilesAC                       = {}
            HTPmainInpFilesREAR                      = {}
            
            for file in self.__files:
                print(file)
                
                HTPmainInpFilesAC[file]            = self.__createHTPmainInpFiles(file,"AC")
                HTPmainInpFilesREAR[file]            = self.__createHTPmainInpFiles(file,"REAR")
                # print(HTPmainInpFilesAC[file])
                
            self.__createConfigFile(HTPmainInpFilesAC,"AC_NF")
            self.__createConfigFile(HTPmainInpFilesREAR,"REAR_NF")
            
            epsilonAC,ihoAC,coeffAC,epsilon_altepAC = self.__runHTPmain("AC_NF")
            epsilonR,ihoR,coeffR,epsilon_altepR = self.__runHTPmain("REAR_NF")
            
            self.__mData['EPSAC']             = epsilonAC
            self.__mData['EPSR']             = epsilonR
            
            self.__mData['ihoAC']             = ihoAC
            self.__mData['ihoR']             = ihoR   
                
            self.__deleteHTPmainFiles(HTPmainInpFilesAC) 
            self.__deleteHTPmainFiles(HTPmainInpFilesREAR) 
            self.__deleteConfigFiles()
            
            cmH0
            for fil in self.__files:
                # print(fil)
                if fil != "HTPoff.txt":
                    cmH0[fil]               = self.__computeCmH0(fil)
                    
            for idx,ws in enumerate(wsIH):
                if self.__files[idx]== "HTPoff.txt":
                    self.__writeIHdata(wb,ws,self.__files[idx],self.__markersHTPoff,'NA',coeffR)
                else:
                    self.__writeIHdata(wb,ws,self.__files[idx],self.__markersHTPon,cmH0[self.__files[idx]],coeffR)
                    
            wsFwdChk                         = wb.add_worksheet(name="Check Forward")
            spotData                         = wb.add_worksheet(name="ConcatData")
            
            
            # New1                             =wb.add_worksheet(name="AlphaH vs CLH")
            
            
            self.__addFwdChkPlots(wb,wsFwdChk)
            self.__addPlotss(wb,splotData)
            
            
            self.__addHTPoffPlots(wb,wb.get_worksheet_by_name("HTPoff.txt"),ihoAC,ihoR,coeffAC,coeffR,epsilon_altepAC,epsilon_altepR)
            
                    
            wb.close()  
            print("near field excel file created")
               
               
               
               
               
               
               
               
               
               
           
      
      
      
      
      
      
          
            
            
            
            
            
            
            
            
           