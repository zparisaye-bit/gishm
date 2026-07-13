# coding=utf-8

import clr
import sys
import System.Math as Math
clr.AddReference('System')
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')
clr.AddReference('ZedGraph')
clr.AddReference('MapCalculate')

from MapCalculate import Map

from ZedGraph import GraphPane,ZoomState, Fill, FillType, SymbolType, AxisType,BarType, ZedGraphControl, PointPairList, DateUnit, XDate, ScaleState

from System.Windows.Forms import *

from System.Drawing import *
from System import *
from System.ComponentModel import *
from System import DateTime
from System.Diagnostics  import *
from System.Threading import *

class Progress(Form):
    def __init__(self):
        self.Canceled=None
        self.loadpage()

    def Button_cancel(self, sender, e):
        if (self.Canceled != None):
            self.Canceled(sender, e)

    def loadpage(self):
        self._progressBar_progress = ProgressBar()
        self._label_progress = Label()
        self._button_progress = Button()
        self.SuspendLayout()
        #
        # progressBar_progress
        #
        self._progressBar_progress.Location = Point(12, 34)
        self._progressBar_progress.Name = "progressBar_progress"
        self._progressBar_progress.Size = Size(331, 23)
        self._progressBar_progress.TabIndex = 0
        self._progressBar_progress.Minimum = 0
        self._progressBar_progress.Maximum = 100
        #
        # label_progress
        #
        self._label_progress.Location = Point(12, 12)
        self._label_progress.Name = "label_progress"
        self._label_progress.Size = Size(331, 19)
        self._label_progress.TabIndex = 1
        #
        # button_progress
        #
        self._button_progress.Location = Point(138, 63)
        self._button_progress.Name = "button_progress"
        self._button_progress.Size = Size(76, 23)
        self._button_progress.TabIndex = 2
        self._button_progress.Text = "Cancel"
        self._button_progress.UseVisualStyleBackColor = True
        self._button_progress.Click += self.Button_cancel
        #
        # MainForm
        #
        self.ClientSize = Size(354, 92)
        self.Controls.Add(self._button_progress)
        self.Controls.Add(self._label_progress)
        self.Controls.Add(self._progressBar_progress)
        self.Name = "MainForm"
        self.Text = "progress"
        self.ResumeLayout(False)

class Model(Form):
    def __init__(self):
        self.loadpage()


        self.backWork=BackgroundWorker()
        self.backWork.DoWork += DoWorkEventHandler(self.preprocess_work)
        self.backWork.ProgressChanged += ProgressChangedEventHandler(self.backWork_progressChanged)
        self.backWork.RunWorkerCompleted += RunWorkerCompletedEventHandler(self.backWork_complete)
        self.backWork.WorkerReportsProgress = True
        self.backWork.WorkerSupportsCancellation = True

        self.backWork2 = BackgroundWorker()
        self.backWork2.DoWork += DoWorkEventHandler(self.run_work)
        self.backWork2.ProgressChanged += ProgressChangedEventHandler(self.backWork_progressChanged2)
        self.backWork2.RunWorkerCompleted += RunWorkerCompletedEventHandler(self.backWork_complete2)
        self.backWork2.WorkerReportsProgress = True
        self.backWork2.WorkerSupportsCancellation = True


    def errorHandling(self,text):
        if (self.backWork.IsBusy):
            self.backWork.CancelAsync()
            self.progress_form.Close()
        if (self.backWork2.IsBusy):
            self.backWork2.CancelAsync()
            self.progress_form.Close()
        MessageBox.Show(text, "Error",
                        MessageBoxButtons.OK, MessageBoxIcon.Error)
    def intersectWithTc(self,map):
        l=[]
        tcWithmap=map.intersect_count(self.map_tc)
        mapCounts=map.count()
        i=0
        for x in self.tcCounts:
            l.append(0)
            for y in mapCounts:
                try:
                    l[i]=l[i] + tcWithmap[y.Key+","+x.Key] * float(y.Key)
                except Collections.Generic.KeyNotFoundException:
                    pass
            l[i]=l[i] / x.Value
            i=i+1
        return l
    def preprocess_work(self, sender, e):
####################################################reading maps
        if (self.backWork.CancellationPending):#
            e.Cancel = True#
            return#
        self.progress_text="Reading Maps"#
        self.backWork.ReportProgress(1)#
        try:
            self.map_tc = Map(self._textBox_Isochron.Text)
        except:
            self.errorHandling('Isochron map not exists or corrupted')
            return
        try:
            map_dem=Map(self._textBox_Demmap.Text)
        except:
            self.errorHandling('Elevation map not exists or corrupted')
            return

        try:
            map_p=Map(self._textBox_ThiessenP.Text)
        except:
            self.errorHandling('Thiessen_P map not exists or corrupted')
            return
        try:
            map_t=Map(self._textBox_ThiessenT.Text)
        except:
            self.errorHandling('Thiessen_T map not exists or corrupted')
            return

        try:
            map_landuse=Map(self._textBox__Landusemap.Text)
        except:
            self.errorHandling('Landuse map not exists or corrupted')
            return
        try:
            map_soil = Map(self._textBox_Soilmap.Text)
        except:
            self.errorHandling('Soil map not exists or corrupted')
            return

        tcWithp=map_p.intersect_count(self.map_tc)
        tcWitht=map_t.intersect_count(self.map_tc)
        self.tcCounts=self.map_tc.count() #maybe need to sum from tcWith

        self.H = self.intersectWithTc(map_dem)
        self.lat=map_dem.lat()
##########################################################################end of reading maps

##########################################################################reading files
        if (self.backWork.CancellationPending):
            e.Cancel = True
            return
        self.progress_text = "Reading Files"
        self.backWork.ReportProgress(15)
        try:
            p_file=Map.readFile(self._textBox_Precipitation.Text)
        except:
            self.errorHandling('Precipitation timeseries not exists or corrupted')
            return
        try:
            tmin_file=Map.readFile(self._textBox_MinTemp.Text)
        except:
            self.errorHandling('Tmin timeseries not exists or corrupted')
            return
        try:
            tmax_file = Map.readFile(self._textBox_MaxTemp.Text)
        except:
            self.errorHandling('Tmax timeseries not exists or corrupted')
            return
        try:
            q_obs_file=Map.readFile(self._textBox__ObservedRunoff.Text)
        except:
            self.errorHandling('Q_obs timeseries not exists or corrupted')
            return

        try:
            landuse_file=Map.readFile("Sample Data\\Inputs\\tables\\landuse.tbl")
            soil_file=Map.readFile("Sample Data\\Inputs\\tables\\soil.tbl")

        except:
            self.errorHandling('Landuse and Soil Table is not in setup folder')
            return
##########################################################################end of reading files
##########################################################################lookups map

        if (self.backWork.CancellationPending):
            e.Cancel = True
            return
        self.progress_text = "Calculate h0p"
        self.backWork.ReportProgress(17)
        try:
            code=[]
            value=[]
            for i in range(3,len(p_file)):
                code.append(str(i-2))
                value.append(p_file[i][0])
            map_hp=map_p.lookup(Array[str](code), Array[str](value))
            self.H0p = self.intersectWithTc(map_hp)


            if (self.backWork.CancellationPending):
                e.Cancel = True
                return
            self.progress_text = "Calculate h0t"
            self.backWork.ReportProgress(19)
            code = []
            value = []
            for i in range(3, len(tmax_file)):
                code.append(str(i - 2))
                value.append(tmax_file[i][0])
            map_ht=map_t.lookup(Array[str](code), Array[str](value))
            self.H0t = self.intersectWithTc(map_ht)

            if (self.backWork.CancellationPending):
                e.Cancel = True
                return

            if not IO.Directory.Exists(self._textBox_OutputDirectory.Text + "\\maps"):
                IO.Directory.CreateDirectory(self._textBox_OutputDirectory.Text + "\\maps")

            self.progress_text = "Calculate CP"
            self.backWork.ReportProgress(21)
            code = []
            value = []
            for i in range(1,len(landuse_file[0])):
                code.append(landuse_file[0][i])
                value.append(landuse_file[6][i])
            map_cp=map_landuse.lookup(Array[str](code), Array[str](value))
            map_cp.toMap(self._textBox_OutputDirectory.Text+"\\maps\\CP.asc")
            self.cp=self.intersectWithTc(map_cp)

            if (self.backWork.CancellationPending):
                e.Cancel = True
                return
            self.progress_text = "Calculate LAIavg"
            self.backWork.ReportProgress(23)
            code = []
            value = []
            for i in range(1, len(landuse_file[0])):
                code.append(landuse_file[0][i])
                value.append(landuse_file[7][i])
            map_LAI=map_landuse.lookup(Array[str](code), Array[str](value))
            map_LAI.toMap(self._textBox_OutputDirectory.Text + "\\maps\\LAIavg.asc")
            self.LAIavg = self.intersectWithTc(map_LAI)



            if (self.backWork.CancellationPending):
                e.Cancel = True
                return
            self.progress_text = "Calculate LAImax"
            self.backWork.ReportProgress(24)
            code = []
            value = []
            for i in range(1, len(landuse_file[0])):
                code.append(landuse_file[0][i])
                value.append(landuse_file[8][i])
            map_LAImax=map_landuse.lookup(Array[str](code), Array[str](value))
            map_LAImax.toMap(self._textBox_OutputDirectory.Text + "\\maps\\LAImax.asc")
            self.LAImax = self.intersectWithTc(map_LAImax)


            if (self.backWork.CancellationPending):
                e.Cancel = True
                return

            self.progress_text = "Calculate CNavg"
            self.backWork.ReportProgress(25)
            map_cn=map_landuse.intersect(map_soil)
            dict=map_cn.crossed
            code = []
            value = []
            for x in dict:
                code.append(str(x.Value))
                list=x.Key.split(",")
                letter=soil_file[2][int(list[1])]
                if(letter=="A"):
                    column=2
                elif(letter=="B"):
                    column=3
                elif(letter=="C"):
                    column=4
                elif(letter=="D"):
                    column=5
                else:
                    self.errorHandling('Faild to recognize soil type')
                    return
                value.append(landuse_file[column][int(list[0])])
            map_cn=map_cn.lookup(Array[str](code), Array[str](value))
            map_cn.toMap(self._textBox_OutputDirectory.Text + "\\maps\\CNavg.asc")
            self.CNavg=self.intersectWithTc(map_cn)
#######################################################################end lookups
#######################################################################inputs for each day
            if (self.backWork.CancellationPending):
                e.Cancel = True
                return
            self.progress_text = "Prepare Inputs For Each Day"
            self.backWork.ReportProgress(30)
            self.tc=[]
            self.area=[]

            self.P = []
            self.Tmin = []
            self.Tmax = []

            self.year = []
            self.month = []
            self.day = []
            self.Q_obs = []


            i=0
            for x in self.tcCounts:
                self.tc.append(float(x.Key))
                self.area.append(x.Value*((self.map_tc.cell_size/1000)**2))
                self.P.append([])
                self.Tmin.append([])
                self.Tmax.append([])
                for j in range(1,len(p_file[0])):
                    self.P[i].append(0)
                    self.Tmin[i].append(0)
                    self.Tmax[i].append(0)
                    for k in range(3,len(p_file)):
                        try:
                            self.P[i][j-1] = self.P[i][j-1] + (tcWithp[str(k-2)+","+x.Key] * float(p_file[k][j]))
                        except Collections.Generic.KeyNotFoundException:
                            pass
                        try:
                            self.Tmin[i][j-1] = self.Tmin[i][j-1] + (tcWitht[str(k-2)+","+x.Key] * float(tmin_file[k][j]))
                            self.Tmax[i][j-1] = self.Tmax[i][j-1] + (tcWitht[str(k-2)+","+x.Key] * float(tmax_file[k][j]))
                        except Collections.Generic.KeyNotFoundException:
                            pass


                    self.P[i][j-1]=self.P[i][j-1] / x.Value
                    self.Tmin[i][j-1] = self.Tmin[i][j-1] / x.Value
                    self.Tmax[i][j-1] = self.Tmax[i][j-1] / x.Value

                if (self.backWork.CancellationPending):
                    e.Cancel = True
                    return
                self.progress_text = "Prepare Inputs For Each Day"
                self.backWork.ReportProgress(30+i*67/len(self.tcCounts))
                i=i+1

            if (self.backWork.CancellationPending):
                e.Cancel = True
                return
            self.progress_text = "Prepare Inputs For Each Day"
            self.backWork.ReportProgress(98)
            for j in range(1, len(p_file[0])):
                self.year.append(float(p_file[0][j]))
                self.month.append(float(p_file[1][j]))
                self.day.append(float(p_file[2][j]))
                self.Q_obs.append(float(q_obs_file[3][j]))
            self.progress_text = "Prepare Inputs For Each Day"
            self.backWork.ReportProgress(99)
            self.p_total=[]
            for i in range(len(self.P[0])):
                sum=0
                for j in range(len(self.P)):
                    sum+=self.P[j][i]
                self.p_total.append(sum)

            self._checkBox_prepro.Checked = False
            if (self.backWork.CancellationPending):
                e.Cancel = True
                return
            self.progress_text = "done!(preprocess)"
            self.backWork.ReportProgress(100)
#################################################################################
        except:
            self.errorHandling('Your input data is corrupted or missing. Check your data!')
            return
    def run_work(self, sender, e):
        if (self.backWork2.CancellationPending):
            e.Cancel = True
            return
        self.progress_text = "Set Time Steps"
        self.backWork2.ReportProgress(1)
        try:
            startStep = int(self._textBox_Starttimestep.Text) - 1
            finalStep = int(self._textBox_Finaltimestep.Text) - 1
            nStep = int(self._textBox__Notimestep.Text)
        except:
            self.errorHandling('Steps are incorrect')
            return

        year = []
        month = []
        day = []
        P = []
        Tmin = []
        Tmax = []
        Q_obs = []
        if (self.backWork2.CancellationPending):
            e.Cancel = True
            return
        self.progress_text = "Cut Data To Match Time Step"
        self.backWork2.ReportProgress(2)

        for i in range(len(self.P)):
            P.append([])
            Tmin.append([])
            Tmax.append([])
            for j in range(startStep, finalStep + 1, nStep):
                P[i].append(self.P[i][j])
                Tmin[i].append(self.Tmin[i][j])
                Tmax[i].append(self.Tmax[i][j])

        for i in range(startStep, finalStep + 1, nStep):
            year.append(self.year[i])
            month.append(self.month[i])
            day.append(self.day[i])
            Q_obs.append(self.Q_obs[i])

        if (self.backWork2.CancellationPending):
            e.Cancel = True
            return
        self.progress_text = "Set Constants"
        self.backWork2.ReportProgress(5)
        try:
            BFinit = (Q_obs[0] * 0.3)/len(P)
            Csnow = float(self._textBox_Csnow.Text)
            To = float(self._textBox_To.Text)
            Clai = float(self._textBox_Clai.Text)
            d = float(self._textBox_d.Text)
            Cmin = float(self._textBox_Cmin.Text)
            k = float(self._textBox_k_cn.Text)
            landa = float(self._textBox_landa.Text)
            X = float(self._textBox_X.Text)
            Ket = float(self._textBox_Ket.Text)
            alfaET = float(self._textBox_alfa.Text)
            gamaET = float(self._textBox_gama.Text)
            contrib = float(self._textBox_contribution.Text)
            beta = float(self._textBox_beta.Text)
        except:
            self.errorHandling('Invalid or Missing Parameters')
            return
        radiation = self.lat
        SRx = []
        SnowPack = []
        RealSnow = []
        M = []
        BF_res = []


        discharge = []
        BF=[]
        SRfinal=[]

        LAI=[]
        Intcp=[]
        RealMelt=[]
        CNlai=[]
        PET=[]
        AET=[]
        Infil=[]
        if (self.backWork2.CancellationPending):
            e.Cancel = True
            return
        self.progress_text = "Start Model For Each Day"
        self.backWork2.ReportProgress(6)
        for i in range(len(P)):
            discharge.append([])
            BF.append([])
            SRfinal.append([])

            LAI.append([])
            Intcp.append([])
            RealMelt.append([])
            CNlai.append([])
            PET.append([])
            AET.append([])
            Infil.append([])

            SRx.append(0)
            SnowPack.append(0)
            RealSnow.append(0)
            M.append(0)
            BF_res.append(0)
        try:
            for i in range(len(year)):
                j = self.J(i, year[i], month[i], day[i])
                for w in range(len(P)):
                    Tmin[w][i], Tmax[w][i], P[w][i] = self.Gradian(i, Tmin[w][i], Tmax[w][i],
                                                                                  P[w][i], self.H[w], self.H0t[w],
                                                                                  self.H0p[w])
                    Tmean=self.Temperature(i, Tmin[w][i], Tmax[w][i])
                    Snow, Rain = self.SnowandRain(i, P[w][i], Tmean, To)
                    LAI[w].append(self.LeafAreaIndex(i, j, self.LAIavg[w], Clai, d, self.LAImax[w]))
                    
                    RainSnowMelt, M[w], SnowPack[w], RealSnow[w], temp = self.Snowmelt(i, Tmean, Snow, Rain, To, Csnow, M[w],SnowPack[w],RealSnow[w])
                    RealMelt[w].append(temp)
                    CNlai[w].append(self.CurveNumber(i, self.CNavg[w], LAI[w][i], Cmin, k))
                    SR = self.SurfaceRunoff(i, RainSnowMelt, CNlai[w][i], landa)
                    temp, SRx[w] = self.Routing(i, SR, X, self.area[w], SRx[w])
                    SRfinal[w].append(temp)
                    PET[w].append(self.PotentialEvapotranspiration(i, Tmin[w][i], Tmax[w][i], Tmean, j, Ket, radiation))
                    AET[w].append(self.ActualEvapotranspiration(i, PET[w][i], RainSnowMelt, alfaET, gamaET))
                    Infil[w].append(self.Infiltration(i, RainSnowMelt, SRx[w], AET[w][i]))
                    temp, BF_res[w] = self.Baseflow(i, Infil[w][i], self.area[w], contrib, beta, BFinit, BF_res[w])
                    BF[w].append(temp)
                    discharge[w].append(self.TotalDischarge(i, SRfinal[w][i], BF[w][i]))
                if (self.backWork2.CancellationPending):
                    e.Cancel = True
                    return
                self.progress_text = "Start Model For Each Day"
                self.backWork2.ReportProgress(6+i*71/len(year))
        except:
            self.errorHandling('Faild to run model')
            return

        if (self.backWork2.CancellationPending):
            e.Cancel = True
            return
        self.progress_text = "Summing Up Result"
        self.backWork2.ReportProgress(77)

        def addToList(l, index, value):
            if (len(l) - 1 < index):
                for i in range(index - len(l)):
                    l.append(0)
                l.append(value)
            else:
                l[index] += value

        def sumWithLag(l):
            result=[]
            for i in range(len(l)):
                tlag = self.tc[i] * 0.6
                for j in range(len(l[i])):
                    addToList(result, j + int(tlag / 24), l[i][j])
            return result
        def sumNormal(l):
            result=[]
            for i in range(len(l[0])):
                sum=0
                for j in range(len(l)):
                    sum+=l[j][i]
                result.append(sum)
            return result


        self.discharge = sumWithLag(discharge)
        for i in range(len(self.discharge) - len(Q_obs)):
            self.discharge.pop()
        SRfinal_final=sumWithLag(SRfinal)
        # SRfinal_final = sumNormal(SRfinal)
        BF_final=sumWithLag(BF)
        # BF_final = sumNormal(BF)

        if (self.backWork2.CancellationPending):
            e.Cancel = True
            return
        self.progress_text = "Summing Up Result"
        self.backWork2.ReportProgress(79)

        LAI_final=sumNormal(LAI)
        RealMelt_final=sumNormal(RealMelt)
        CNlai_final=sumNormal(CNlai)
        PET_final=sumNormal(PET)
        AET_final=sumNormal(AET)
        Infil_final=sumNormal(Infil)

        if (self.backWork2.CancellationPending):
            e.Cancel = True
            return
        self.progress_text = "Summing Up Result"
        self.backWork2.ReportProgress(80)
        headers = "year\tmonth\tday\ttSnowMelt(mm)\tCN\tSR(m3/s)\tPET(mm)\tAET(mm)\tInfil(mm)\tBF(m3/s)\tDischarge(m3/s)"
        try:
            Map.writeFile(
                self._textBox_OutputDirectory.Text + "\\" + self._textBox_resultsname.Text + ".tbl",
                headers, False)
        except:
            self.errorHandling('Invalid Adress For Output Or File Is Open')
            return
        for i in range(len(self.discharge)):
            col = str(year[i]) + "\t" + str(month[i]) + "\t" + str(day[i]) + "\t" + str(RealMelt_final[i]/len(P)) + "\t" + str(CNlai_final[i]/len(P)) + "\t" + str(
                SRfinal_final[i]) + "\t" + str(PET_final[i]/len(P)) + "\t" + str(AET_final[i]/len(P)) + "\t" + str(
                Infil_final[i]/len(P)) + "\t" + str(BF_final[i]) + "\t" + str(self.discharge[i]) + "\t"
            try:
                Map.writeFile(self._textBox_OutputDirectory.Text+"\\"+self._textBox_resultsname.Text +".tbl", col, True)
            except:
                self.errorHandling('Invalid Adress For Output Or File Is Open')
                return
            if (self.backWork2.CancellationPending):
                e.Cancel = True
                return
            self.progress_text = "Summing Up Result"
            self.backWork2.ReportProgress(80+i * 17 / len(year))


        if (self.backWork2.CancellationPending):
            e.Cancel = True
            return
			
        self.progress_text = "Calculate NASH"
        self.backWork2.ReportProgress(97)
		
        r2 = self.R2(self.discharge, Q_obs)
        ns = self.NS(self.discharge, Q_obs)
        mb = self.MB(self.discharge, Q_obs)
        br2 = self.BR2(Q_obs, self.discharge)
        KGE, KGEprime = self.KGE(self.discharge, Q_obs)
        self._textBox_R2.Text = str(r2)
        self._textBox__NS.Text = str(ns)
        self._textBox_bias.Text = str(mb)
        self._textBox_bR2.Text = str(br2)
        self._textBox_KGE.Text = str(KGE)
        self._textBox_modifiedKGE.Text = str(KGEprime)

        if (self.backWork2.CancellationPending):
            e.Cancel = True
            return
        self.progress_text = "Drawing Hydrograph"
        self.backWork2.ReportProgress(98)

        self._pictureBox_Hydrograph.GraphPane.CurveList.Clear()
        self._pictureBox_Hydrograph.GraphPane.GraphObjList.Clear()

        pane = self._pictureBox_Hydrograph.GraphPane
        pane.Title.Text = "Hydrograph"
        pane.XAxis.Title.Text = "Time(day)"
        pane.YAxis.Title.Text = "Q(m3/s)"
        pane.Y2Axis.IsVisible = True
        pane.Y2Axis.Title.Text="P(mm)"
        pane.Y2Axis.Scale.IsReverse = True


        pane.Legend.FontSpec.Size = 18
        pane.Legend.Border.IsVisible = False


        pane.XAxis.Type = AxisType.Date
        pane.XAxis.Scale.Format = "dd-MMM-yy"
        pane.XAxis.Scale.MinorUnit = DateUnit.Day
        pane.XAxis.Scale.MajorUnit = DateUnit.Month

        self.firstY = int(year[0])
        self.firstM = int(month[0])
        self.firstD = int(day[0])
        pane.XAxis.Scale.Min = XDate(self.firstY, self.firstM, self.firstD)
        pane.XAxis.Scale.Max = XDate(self.firstY, self.firstM, self.firstD + 365)


        # The ZedGraph data collection class
        ppl = PointPairList()
        ppl2 = PointPairList()
        ppl3 = PointPairList()
        for i in range(len(year)):
            ppl.Add(XDate(int(year[i]), int(month[i]), int(day[i])), self.discharge[i])
            ppl2.Add(XDate(int(year[i]), int(month[i]), int(day[i])), Q_obs[i])
            if self.p_total[i]!=0:
                ppl3.Add(XDate(int(year[i]), int(month[i]), int(day[i])), self.p_total[i])

        curve = pane.AddCurve("Q_sim", ppl, Color.Red, SymbolType.None)
        curve2 = pane.AddCurve("Q_obs", ppl2, Color.Blue, SymbolType.None)
        bar = pane.AddBar("P", ppl3, Color.Aqua)
        bar.Bar.Fill = Fill(Color.Aqua)
        bar.Bar.Fill.Type = FillType.Solid
        bar.Bar.Border.IsVisible = False
        bar.IsY2Axis = True
        self._pictureBox_Hydrograph.AxisChange()
        self._pictureBox_Hydrograph.Invalidate()


        if (self.backWork2.CancellationPending):
            e.Cancel = True
            return
        self.progress_text = "done!"
        self.backWork2.ReportProgress(100)

    def preprocessed(self):
        try:
            if len(self.P) > 0 and len(self.P[0]) > 0:
                return True
            else:
                return False
        except:
            return False

    def Button_Run_Click(self, sender, e):
        if self.preprocessed() == False or self._checkBox_prepro.Checked==True:
            if (not self.backWork.IsBusy):
                self.progress_form = Progress()
                self.progress_form.Canceled = self.Button_cancel
                self.progress_form.TopLevel = False
                self.progress_form.FormBorderStyle = FormBorderStyle.None
                self.progress_form.Parent = self
                self.progress_form._progressBar_progress.Value = 0

                self.progress_form.Show()
                self.progress_form.Location = Point(self.ClientSize.Width / 2 - self.progress_form.Width / 2,
                                                    self.ClientSize.Height / 2 - self.progress_form.Height / 2)
                self.progress_form.BringToFront()

                # self.preprocess_work()

                self.backWork.RunWorkerAsync()
        else:
            if (not self.backWork2.IsBusy):
                self.progress_form = Progress()
                self.progress_form.Canceled=self.Button_cancel2
                self.progress_form.TopLevel = False
                self.progress_form.FormBorderStyle = FormBorderStyle.None
                self.progress_form.Parent = self
                self.progress_form._progressBar_progress.Value = 0
                self.progress_form.Show()
                self.progress_form.Location = Point(self.ClientSize.Width / 2 - self.progress_form.Width / 2,
                                                    self.ClientSize.Height / 2 - self.progress_form.Height / 2)
                self.progress_form.BringToFront()

                # self.preprocess_work()

                self.backWork2.RunWorkerAsync()

    def backWork_progressChanged2(self, sender, e):
        self.progress_form._label_progress.Text=self.progress_text
        self.progress_form._progressBar_progress.Value = e.ProgressPercentage
    def backWork_progressChanged(self, sender, e):
        self.progress_form._label_progress.Text=self.progress_text
        self.progress_form._progressBar_progress.Value = e.ProgressPercentage
    def backWork_complete2(self, sender, e):
        if e.Cancelled:
            self._tabControl_Input_Output.SelectedTab = self._tabPage_Parameters
            self.progress_form.Close()
        elif e.Error != None:
            self._tabControl_Input_Output.SelectedTab = self._tabPage_Parameters
            self.progress_form.Close()
            self.errorHandling(e.Error)
        else:
            self._tabControl_Input_Output.SelectedTab = self._tabPage_Display
            self.progress_form.Close()
    def backWork_complete(self, sender, e):
        if e.Cancelled:
            self._tabControl_Input_Output.SelectedTab = self._tabPage_Parameters
            self.progress_form.Close()
        elif e.Error != None:
            self._tabControl_Input_Output.SelectedTab = self._tabPage_Parameters
            self.progress_form.Close()
            self.errorHandling(e.Error)

        else:
            self.progress_form.Close()
            if (not self.backWork2.IsBusy):
                self.progress_form = Progress()
                self.progress_form.Canceled=self.Button_cancel2
                self.progress_form.TopLevel = False
                self.progress_form.FormBorderStyle = FormBorderStyle.None
                self.progress_form.Parent = self
                self.progress_form._progressBar_progress.Value = 0
                self.progress_form.Show()
                self.progress_form.Location = Point(self.ClientSize.Width / 2 - self.progress_form.Width / 2,
                                                    self.ClientSize.Height / 2 - self.progress_form.Height / 2)
                self.progress_form.BringToFront()

                # self.preprocess_work()

                self.backWork2.RunWorkerAsync()

        # self.resetEvent.Set()
    # +++++++++++++++++++++++++++++++++++++++++++++++++ Hydrological Processes ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # +++++++++++++++++++++++++++++++++++++++++++++++++ calculation of J(year,month,day):
    def is_leap_year(self, year):
        """ if year is a leap year return True
            else return False """
        if year % 100 == 0:
            return year % 400 == 0
        return year % 4 == 0

    def J(self, STEP, year, month, day):
        i = str(STEP)
        try:

            if self.is_leap_year(year):
                K = 1
            else:
                K = 2
            j = int((275 * month) / 9.0) - K * int((month + 9) / 12.0) + day - 30
            return j
        except:
            self.errorHandling('An error happened while calculating J at step '+i)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++gradian
    def Gradian(self, STEP, Tmin, Tmax, P,H ,h0t,h0p):
        i = str(STEP)
        try:
            Tmin_new =Tmin - (0.005 * (H - h0t))
            Tmax_new =Tmax - (0.005 * (H - h0t))
            P_new = P
            return Tmin_new, Tmax_new, P_new
        except:
            self.errorHandling('An error happened while calculating Gradian at step '+i)
    # +++++++++++++++++++++++++++++++++++++++++++++++++ calculation of Temperature
    def Temperature(self, STEP, Tmin, Tmax):
        i = str(STEP)
        try:
            Tmean = (Tmin + Tmax) / 2
            return Tmean
        except:
            self.errorHandling('An error happened while calculating Temperature at step '+i)

    # +++++++++++++++++++++++++++++++++++++++++++++++++ calculation of SnowandRain
    def SnowandRain(self, STEP, Precip, Tmean, To):
        i = str(STEP)
        try:

            if Tmean <= To:
                Snow = Precip
            else:
                Snow = 0
            if Tmean > To:
                Rain = Precip
            else:
                Rain = 0
            # Snow=Precip / (((s1 ** Tmean) *s2) + 1)
            # Rain = Precip - Snow
            return Snow, Rain
        except:
            self.errorHandling('An error happened while calculating SnowAndRain at step '+i)

    # +++++++++++++++++++++++++++++++++++++++++++++++++ calculation of LeafAreaIndex
    def LeafAreaIndex(self, STEP, j, LAIave, Clai, d, LAImax):
        i = str(STEP)
        try:

            LAI = LAIave + (Clai * Math.Cos((d * j) + (LAImax)))
            return LAI

        except:
            self.errorHandling('An error happened while calculating LAI at step '+i)

    # +++++++++++++++++++++++++++++++++++++++++++++++++ calculation of Interception
    #def Interception(self, STEP, Rain, LAI, Cp):
     #   i = str(STEP)
      #  try:
#
 #           Smax = 0.935 + (0.498 * LAI) - (0.00575 * (LAI ** 2))
  #          k = 0.065 * LAI
   #         Intcp = Cp * Smax * (1 - Math.Exp(-1 * k * (Rain / Smax)))
    #        return Intcp
     #   except:
      #      self.errorHandling('An error happened while calculating Interception at step '+i)

    # +++++++++++++++++++++++++++++++++++++++++++++++++ calculation of Snowmelt(step,Tmean,Snow,Rain,Intcp,To,Csnow,prevM,prevSnowPack,prevRealSnow):
    def Snowmelt(self, STEP, Tmean, Snow, Rain, To, Csnow, prevM, prevSnowPack, prevRealSnow):
        i = str(STEP)
        try:

            Rainnew = Rain
            M = max(0, ((Csnow * (Tmean - To))))
            SnowPack = (Snow + prevSnowPack) if STEP > 0 else 0
            RealSnow = Snow + max(0, prevRealSnow - prevM) if STEP > 0 else 0
            if (RealSnow > 0):
                RealMelt = min(RealSnow, M)
            else:
                RealMelt = 0
            RainSnowMelt = Rainnew + RealMelt
            return RainSnowMelt, M, SnowPack, RealSnow,RealMelt
        except:
            self.errorHandling('An error happened while calculating SnowMelt at step '+i)

    # +++++++++++++++++++++++++++++++++++++++++++++++++ calculation of CurveNumber(CNave,LAI,Cmin,k):
    def CurveNumber(self, STEP, CNave, LAI, Cmin, k):
        i = str(STEP)
        try:

            CNlai = ((Cmin * CNave) + (100 - (Cmin * CNave)) * Math.Exp(-1 * k * LAI))
            return CNlai
        except:
            self.errorHandling('An error happened while calculating CurveNumber at step '+i)

    # +++++++++++++++++++++++++++++++++++++++++++++++++ calculation of SurfaceRunoff(RainSnowMelt,CNlai,landa):
    def SurfaceRunoff(self, STEP, RainSnowMelt, CNlai, landa):
        i = str(STEP)
        try:

            S = (25400 / CNlai) - 254
            if RainSnowMelt > (landa * S):
                SR = (((RainSnowMelt - (landa * S)) ** 2) / (RainSnowMelt + ((1 - landa) * S)))
            else:
                SR = 0
            return SR

        except:
            self.errorHandling('An error happened while calculating SR at step '+i)

    # +++++++++++++++++++++++++++++++++++++++++++++++++ calculation of Routing(step,SR,X,area,prevSRx):
    def Routing(self, STEP, SR, X, area, prevSRx):
        i = str(STEP)
        try:

            SRx = X * prevSRx + (1 - X) * SR if STEP > 0 else SR
            SRfinal = SRx * 0.001 * (area * 1000000) / (24 * 3600)
            return SRfinal, SRx
        except:
            self.errorHandling('An error happened while calculating Routing at step '+i)

    # +++++++++++++++++++++++++++++++++++++++++++++++++ calculation of PotentialEvapotranspiration(Tmin,Tmax,Tmean,j,Ket,radiation):
    def PotentialEvapotranspiration(self, STEP, Tmin, Tmax, Tmean, j, Ket, radiation):
        i = str(STEP)
        try:

            dr = 1 + (0.033 * Math.Cos((2 * Math.PI / 365) * j))
            teta = 0.409 * Math.Sin(((2 * Math.PI / 365) * j) - 1.39)
            ws = Math.Acos(-Math.Tan(radiation) * Math.Tan(teta))
            Ra = 24 * 60 / Math.PI * 0.0820 * dr * ((ws * Math.Sin(radiation) * Math.Sin(teta)) +
                                                    (Math.Cos(radiation) * Math.Cos(teta) * Math.Sin(
                                                        ws)))  # Mj/m2day    #if Ra(Mj/m2day)/2.45 or(*0.408) =Ra(mm/day)
            TD = Tmax - Tmin  # T(c)
            PET = Ket * (Ra / 2.45) * (TD ** 0.5) * (Tmean + 17.8)  # mm/day   Ra&ET

            return PET
        except:
            self.errorHandling('An error happened while calculating PET at step '+i)

    # +++++++++++++++++++++++++++++++++++++++++++++++++ calculation of ActualEvapotranspiration(PET,RainSnowMelt,alfaET,gamaET):
    def ActualEvapotranspiration(self, STEP, PET, RainSnowMelt, alfaET, gamaET):
        i = str(STEP)
        try:

            if PET == 0 or RainSnowMelt == 0:
                AET = 0
            else:
                AET = RainSnowMelt / ((alfaET + ((RainSnowMelt / PET) ** gamaET)) ** (1 / gamaET))

            return AET


        except:
            self.errorHandling('An error happened while calculating AET at step '+i)

    # +++++++++++++++++++++++++++++++++++++++++++++++++ calculation of Infiltration(RainSnowMelt,SRx,AET):
    def Infiltration(self, STEP, RainSnowMelt, SRx, AET):
        i = str(STEP)
        try:

            Infil = max((RainSnowMelt - SRx - AET), 0)
            return Infil  # mm
        except:
            self.errorHandling('An error happened while calculating Infiltration at step '+i)

    # +++++++++++++++++++++++++++++++++++++++++++++++++ calculation of Baseflow(step,Infil,area,contrib,beta,BFinit,prevBaseflow):
    def Baseflow(self, STEP, Infil, area, contrib, beta, BFinit, prevBaseflow):
        i = str(STEP)
        try:
            Vinfil = Infil * 0.001 * contrib * (area * 1000000) / (24 * 3600)  # m3/s
            BF = beta * prevBaseflow + (1 - beta) * Vinfil if STEP > 0 else BFinit
            return BF,BF  # m3/s
        except:
            self.errorHandling('An error happened while calculating BaseFlow at step'+i)

    # +++++++++++++++++++++++++++++++++++++++++++++++++ calculation of TotalDischarge(SRfinal,BF):
    def TotalDischarge(self, STEP, SRfinal, BF):
        i = str(STEP)
        try:

            discharge = SRfinal + BF
            return discharge
        except:
            self.errorHandling('An error happened while calculating TotalDischarge at step'+i)

    # +++++++++++++++++++++++++++++++++++++++++++++++++ calculation of R2
    def R2(self, S, O):  ##R2
        try:
            O_AV = sum(O) / len(O)
            S_AV = sum(S) / len(S)
            numerator = 0.0
            sumO = 0.0
            sumS = 0.0
            for i in range(len(O)):
                numerator = numerator + ((O[i] - O_AV) * (S[i] - S_AV))
                sumO = sumO + ((O[i] - O_AV) ** 2)
                sumS = sumS + ((S[i] - S_AV) ** 2)
            R2 = (numerator ** 2) / (sumO * sumS)
            return R2
        except:
            self.errorHandling('An error happened while calculating R2')

    # +++++++++++++++++++++++++++++++++++++++++++++++++ calculation of nash
    def NS(self, S, O):  ##Nash-Sutcliffe efficiency
        try:
            O_AV = sum(O) / len(O)
            numerator = 0.0
            denominator = 0.0
            for i in range(len(O)):
                numerator = numerator + ((S[i] - O[i]) ** 2)
                denominator = denominator + ((O[i] - O_AV) ** 2)
            NS = 1 - (numerator / denominator)
            return NS
        except:
            self.errorHandling('An error happened while calculating NS')

    # +++++++++++++++++++++++++++++++++++++++++++++++++ calculation of model bias
    def MB(self, S, O):
        try:
            sumSO = 0.0
            sumO = 0.0
            for i in range(len(O)):
                sumSO = sumSO + (S[i] - O[i])
                sumO = sumO + O[i]
            MB = sumSO / sumO
            return MB
        except:
            self.errorHandling('An error happened while calculating MB')

    # +++++++++++++++++++++++++++++++++++++++++++++++++ calculation of model bR2
    def BR2(self, O, S):
        try:
            # number of observations/points
            n = len(O)

            # mean of x and y vector
            m_x, m_y = sum(O) / len(O), sum(S) / len(S)

            # calculating cross-deviation and deviation about x
            SS_xy = sum([a * b for a, b in zip(S, O)]) - n * m_y * m_x
            SS_xx = sum([a * b for a, b in zip(O, O)]) - n * m_x * m_x

            # calculating regression coefficients
            b = SS_xy / SS_xx
            if (b <= 1):
                return Math.Abs(b) * self.R2(S, O)
            else:
                return 1 / Math.Abs(b) * self.R2(S, O)
        except:
            self.errorHandling('An error happened while calculating BR2')

    # +++++++++++++++++++++++++++++++++++++++++++++++++ calculation of standard deviation
    def STD(self, list):
        try:
            s = 0
            avg = sum(list) / len(list)
            for i in range(len(list)):
                s = s + (list[i] - avg) ** 2
            div = s / (len(list) - 1)
            return Math.Sqrt(div)
        except:
            self.errorHandling('An error happened while calculating STD')

    # +++++++++++++++++++++++++++++++++++++++++++++++++ calculation of KGE and modefied KGE
    def KGE(self, S, O):
        try:
            avgS = sum(S) / len(S)
            avgO = sum(O) / len(O)
            stdS = self.STD(S)
            stdO = self.STD(O)
            cvS = stdS / avgS
            cvO = stdO / avgO
            r = Math.Sqrt(self.R2(S, O))
            alpha = stdS / stdO
            beta = avgS / avgO
            gama = cvS / cvO
            KGE = 1 - (Math.Sqrt(((r - 1) ** 2) + ((alpha - 1) ** 2) + ((beta - 1) ** 2)))
            KGEprime = 1 - (Math.Sqrt(((r - 1) ** 2) + ((gama - 1) ** 2) + ((beta - 1) ** 2)))
            return KGE, KGEprime
        except:
            self.errorHandling('An error happened while calculating KGE')

    # +++++++++++++++++++++++++++++++++++++++++++++++++ End of Hydrological Processes ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # +++++++++++++++++++++++++++++++++++++++++++++++++ Model Interface Link
    def Button_cancel(self, sender, e):
        if (self.backWork.IsBusy):
            self.backWork.CancelAsync()
            self.progress_form.Close()
    def Button_cancel2(self, sender, e):
        if (self.backWork2.IsBusy):
            self.backWork2.CancelAsync()
            self.progress_form.Close()

    def Text_WorkDirectChange(self, sender, e):
        self.AutoLoad(sender.Text)
        self._textBox_OutputDirectory.Text = sender.Text + "\\Outputs"
    def Text_Change(self,sender, e):
        self._checkBox_prepro.Checked=True
    def Button_WorkDirectClick(self, sender, e):
        self.folderBrowserDialog1 = FolderBrowserDialog()
        if self.folderBrowserDialog1.ShowDialog() == DialogResult.OK:
            self._textBox_WorkDirect.Text = self.folderBrowserDialog1.SelectedPath
            self.AutoLoad(self.folderBrowserDialog1.SelectedPath)
            self._textBox_OutputDirectory.Text = self.folderBrowserDialog1.SelectedPath + "\\Outputs"

    def AutoLoad(self, tagetpath):
        if IO.Directory.Exists(tagetpath + "\\Inputs\\"):
            for FL in IO.Directory.GetFiles(tagetpath + "\\Inputs\\maps"):
                FIL = IO.Path.GetFileNameWithoutExtension(FL).lower()
                Exten = IO.Path.GetExtension(FL).lower()

                if str(Exten).endswith(".asc") or str(Exten).endswith(".txt"):
                    if str(FIL).startswith("elevation"):
                        self._textBox_Demmap.Text = FL
                    if str(FIL).startswith("isochron"):
                        self._textBox_Isochron.Text=FL
                    elif str(FIL).startswith("landuse"):
                        self._textBox__Landusemap.Text = FL
                    elif str(FIL).startswith("soil"):
                        self._textBox_Soilmap.Text = FL
                    elif str(FIL).startswith("thiessen") and "_p" in str(FIL):
                        self._textBox_ThiessenP.Text=FL
                    elif str(FIL).startswith("thiessen") and "_t" in str(FIL):
                        self._textBox_ThiessenT.Text=FL

            for FL in IO.Directory.GetFiles(tagetpath + "\\Inputs\\timeseries\\"):
                FIL = IO.Path.GetFileNameWithoutExtension(FL).lower()
                Exten = IO.Path.GetExtension(FL).lower()

                if str(Exten).endswith(".tbl") or str(Exten).endswith(".txt"):
                    if str(FIL).startswith("p"):
                        self._textBox_Precipitation.Text = FL
                    elif str(FIL).startswith("tmax"):
                        self._textBox_MaxTemp.Text = FL
                    elif str(FIL).startswith("tmin"):
                        self._textBox_MinTemp.Text = FL
                    elif str(FIL).startswith("q"):
                        self._textBox__ObservedRunoff.Text = FL

    def Button_DemClick(self, sender, e):
        self.openFileDialog1.Filter = "ESRI ASCII files (*.asc)|*.asc|txt files (*.txt)|*.txt|All files (*.*)|*.*"
        if self.openFileDialog1.ShowDialog() == DialogResult.OK:
            self._textBox_Demmap.Text = self.openFileDialog1.FileName

    def Button_SoilClick(self, sender, e):
        self.openFileDialog1.Filter = "ESRI ASCII files (*.asc)|*.asc|txt files (*.txt)|*.txt|All files (*.*)|*.*"
        if self.openFileDialog1.ShowDialog() == DialogResult.OK:
            self._textBox_Soilmap.Text = self.openFileDialog1.FileName

    def Button_LanduseClick(self, sender, e):
        self.openFileDialog1.Filter = "ESRI ASCII files (*.asc)|*.asc|txt files (*.txt)|*.txt|All files (*.*)|*.*"
        if self.openFileDialog1.ShowDialog() == DialogResult.OK:
            self._textBox__Landusemap.Text = self.openFileDialog1.FileName

    def Button_ThiessenPClick(self, sender, e):
        self.openFileDialog1.Filter = "ESRI ASCII files (*.asc)|*.asc|txt files (*.txt)|*.txt|All files (*.*)|*.*"
        if self.openFileDialog1.ShowDialog() == DialogResult.OK:
            self._textBox_ThiessenP.Text = self.openFileDialog1.FileName
    def Button_ThiessenTClick(self, sender, e):
        self.openFileDialog1.Filter = "ESRI ASCII files (*.asc)|*.asc|txt files (*.txt)|*.txt|All files (*.*)|*.*"
        if self.openFileDialog1.ShowDialog() == DialogResult.OK:
            self._textBox_ThiessenT.Text = self.openFileDialog1.FileName
    def Button_IsochronClick(self, sender, e):
        self.openFileDialog1.Filter = "ESRI ASCII files (*.asc)|*.asc|txt files (*.txt)|*.txt|All files (*.*)|*.*"
        if self.openFileDialog1.ShowDialog() == DialogResult.OK:
            self._textBox_Isochron.Text = self.openFileDialog1.FileName

    def Button_PrecipitationClick(self, sender, e):
        self.openFileDialog1.Filter = "Table files (*.tbl)|*.tbl|txt files (*.txt)|*.txt|All files (*.*)|*.*"
        if self.openFileDialog1.ShowDialog() == DialogResult.OK:
            self._textBox_Precipitation.Text = self.openFileDialog1.FileName

    def Button_MaxTempClick(self, sender, e):
        self.openFileDialog1.Filter = "Table files (*.tbl)|*.tbl|txt files (*.txt)|*.txt|All files (*.*)|*.*"
        if self.openFileDialog1.ShowDialog() == DialogResult.OK:
            self._textBox_MaxTemp.Text = self.openFileDialog1.FileName

    def Button_MinTempClick(self, sender, e):
        self.openFileDialog1.Filter = "Table files (*.tbl)|*.tbl|txt files (*.txt)|*.txt|All files (*.*)|*.*"
        if self.openFileDialog1.ShowDialog() == DialogResult.OK:
            self._textBox_MinTemp.Text = self.openFileDialog1.FileName

    def Button_ObservedRunoffClick(self, sender, e):
        self.openFileDialog1.Filter = "Table files (*.tbl)|*.tbl|txt files (*.txt)|*.txt|All files (*.*)|*.*"
        if self.openFileDialog1.ShowDialog() == DialogResult.OK:
            self._textBox__ObservedRunoff.Text = self.openFileDialog1.FileName

    def Button_OutputDirectoryClick(self, sender, e):
        if self.folderBrowserDialog1.ShowDialog() == DialogResult.OK:
            self._textBox_OutputDirectory.Text = self.folderBrowserDialog1.SelectedPath + "\\"

        # Above function closes current page but we need finalizClose() to exit all  Application
    def Zoom_Event(self,control, oldstate, newstate):
        pass
    def loadpage(self):
        # FolderBrowserDialog
        self.folderBrowserDialog1 = FolderBrowserDialog()
        # openFileDialog
        self.openFileDialog1 = OpenFileDialog()

        self._tabPage_About = TabPage()
        self._tabPage_Display = TabPage()
        self._tabPage_Parameters = TabPage()
        self._tabPage_Inputs = TabPage()
        self._groupBox_Input = GroupBox()
        self._label_WorkDirect = Label()
        self._textBox_WorkDirect = TextBox()
        self._button_WorkDirect = Button()
        self._groupBox_InputMaps = GroupBox()
        self._label_Demmap = Label()
        self._textBox_Demmap = TextBox()
        self._button_Demmap = Button()
        self._label_Landusemap = Label()
        self._textBox__Landusemap = TextBox()
        self._button_Landusemap = Button()
        self._label_Soilmap = Label()
        self._textBox_Soilmap = TextBox()
        self._button__Soilmap = Button()
        self._groupBox_Simulationtimes = GroupBox()
        self._label_Finaltimestep = Label()
        self._label_Starttimestep = Label()
        self._label_Notimestep = Label()
        self._textBox_Starttimestep = TextBox()
        self._textBox_Finaltimestep = TextBox()
        self._textBox__Notimestep = TextBox()
        self._groupBox_Output = GroupBox()
        self._label_OutputDirectory = Label()
        self._textBox_OutputDirectory = TextBox()
        self._button_OutputDirectory = Button()
        self._label_resultsname = Label()
        self._textBox_resultsname = TextBox()
        self._tabControl_Input_Output = TabControl()
        self._groupBox_Snowmelt = GroupBox()
        self._groupBox_PET = GroupBox()
        self._textBox_To = TextBox()
        self._label_Specifymodelparameters = Label()
        self._groupBox_AET = GroupBox()
        self._groupBox_SurfaceRunoff = GroupBox()
        self._groupBox_Baseflow = GroupBox()
        self._button_Run = Button()
        self._textBox_Csnow = TextBox()
        self._textBox_gama = TextBox()
        self._textBox_alfa = TextBox()
        self._textBox_Ket = TextBox()
        self._textBox_landa = TextBox()
        self._textBox_X = TextBox()
        self._groupBox_LAI = GroupBox()
        self._groupBox_CN = GroupBox()
        self._textBox_beta = TextBox()
        self._textBox_contribution = TextBox()
        self._textBox_Cmin = TextBox()
        self._textBox_k_cn = TextBox()
        self._textBox_Clai = TextBox()
        self._textBox_d = TextBox()
        self._label_To = Label()
        self._label_Csnow = Label()
        self._label_alfa = Label()
        self._label_gama = Label()
        self._label_Beta = Label()
        self._label_Contribution = Label()
        self._label_Ket = Label()
        self._label_landa = Label()
        self._label_X = Label()
        self._label_Clai = Label()
        self._label_d = Label()
        self._label_k_cn = Label()
        self._label_Cmin = Label()
        self._label_aboutmodel_Titr = Label()
        self._label_aboutmodel = Label()
        self._groupBox_Hydrograph = GroupBox()
        self._groupBox_Evaluationcriteria = GroupBox()
        self._pictureBox_Hydrograph = ZedGraphControl()
        self._textBox__NS = TextBox()
        self._textBox_R2 = TextBox()
        self._textBox_KGE = TextBox()
        self._textBox_modifiedKGE = TextBox()
        self._textBox_bias = TextBox()
        self._textBox_bR2 = TextBox()
        self._label_NS = Label()
        self._label_KGE = Label()
        self._label3_modifiedKGE = Label()
        self._label_bias = Label()
        self._label_R2 = Label()
        self._label_bR2 = Label()
        self._checkBox_prepro = CheckBox()
        self._button_ThiessenP = Button()
        self._textBox_ThiessenP = TextBox()
        self._label_ThiessenP = Label()
        self._textBox_Isochron = TextBox()
        self._label_Isochron = Label()
        self._button_ThiessenT = Button()
        self._textBox_ThiessenT = TextBox()
        self._label_ThiessenT = Label()
        self._button_Isochron = Button()
        self._groupBox_InputTimeseries = GroupBox()
        self._label_Precipitation = Label()
        self._textBox_Precipitation = TextBox()
        self._button_Precipitation = Button()
        self._label_MaxTemp = Label()
        self._textBox_MaxTemp = TextBox()
        self._button_MaxTemp = Button()
        self._label_MinTemp = Label()
        self._textBox_MinTemp = TextBox()
        self._button_MinTemp = Button()
        self._label_ObservedRunoff = Label()
        self._textBox__ObservedRunoff = TextBox()
        self._button__ObservedRunoff = Button()
        self._tabPage_About.SuspendLayout()
        self._tabPage_Display.SuspendLayout()
        self._tabPage_Parameters.SuspendLayout()
        self._tabPage_Inputs.SuspendLayout()
        self._groupBox_Input.SuspendLayout()
        self._groupBox_InputMaps.SuspendLayout()
        self._groupBox_Simulationtimes.SuspendLayout()
        self._groupBox_Output.SuspendLayout()
        self._tabControl_Input_Output.SuspendLayout()
        self._groupBox_Snowmelt.SuspendLayout()
        self._groupBox_PET.SuspendLayout()
        self._groupBox_AET.SuspendLayout()
        self._groupBox_SurfaceRunoff.SuspendLayout()
        self._groupBox_Baseflow.SuspendLayout()
        self._groupBox_LAI.SuspendLayout()
        self._groupBox_CN.SuspendLayout()
        self._groupBox_Hydrograph.SuspendLayout()
        self._groupBox_Evaluationcriteria.SuspendLayout()
        self._groupBox_InputTimeseries.SuspendLayout()
        self.SuspendLayout()
        # 
        # tabPage_About
        # 
        self._tabPage_About.Controls.Add(self._label_aboutmodel)
        self._tabPage_About.Controls.Add(self._label_aboutmodel_Titr)
        self._tabPage_About.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                       GraphicsUnit.Point, 178)
        self._tabPage_About.Location = Point(4, 22)
        self._tabPage_About.Name = "tabPage_About"
        self._tabPage_About.Padding = Padding(3)
        self._tabPage_About.Size = Size(701, 418)
        self._tabPage_About.TabIndex = 3
        self._tabPage_About.Text = "About"
        self._tabPage_About.UseVisualStyleBackColor = True
        # 
        # tabPage_Display
        # 
        self._tabPage_Display.Controls.Add(self._groupBox_Evaluationcriteria)
        self._tabPage_Display.Controls.Add(self._groupBox_Hydrograph)
        self._tabPage_Display.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                         GraphicsUnit.Point, 178)
        self._tabPage_Display.Location = Point(4, 22)
        self._tabPage_Display.Name = "tabPage_Display"
        self._tabPage_Display.Padding = Padding(3)
        self._tabPage_Display.Size = Size(701, 418)
        self._tabPage_Display.TabIndex = 2
        self._tabPage_Display.Text = "Result/Display"
        self._tabPage_Display.UseVisualStyleBackColor = True
        # 
        # tabPage_Parameters
        # 
        self._tabPage_Parameters.Controls.Add(self._checkBox_prepro)
        self._tabPage_Parameters.Controls.Add(self._button_Run)
        self._tabPage_Parameters.Controls.Add(self._groupBox_Baseflow)
        self._tabPage_Parameters.Controls.Add(self._groupBox_SurfaceRunoff)
        self._tabPage_Parameters.Controls.Add(self._groupBox_LAI)
        self._tabPage_Parameters.Controls.Add(self._groupBox_AET)
        self._tabPage_Parameters.Controls.Add(self._label_Specifymodelparameters)
        self._tabPage_Parameters.Controls.Add(self._groupBox_PET)
        self._tabPage_Parameters.Controls.Add(self._groupBox_Snowmelt)
        self._tabPage_Parameters.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                            GraphicsUnit.Point, 178)
        self._tabPage_Parameters.Location = Point(4, 22)
        self._tabPage_Parameters.Name = "tabPage_Parameters"
        self._tabPage_Parameters.Padding = Padding(3)
        self._tabPage_Parameters.Size = Size(701, 418)
        self._tabPage_Parameters.TabIndex = 1
        self._tabPage_Parameters.Text = "Parameters/Simulation"
        self._tabPage_Parameters.UseVisualStyleBackColor = True
        # 
        # tabPage_Inputs
        # 
        self._tabPage_Inputs.Controls.Add(self._groupBox_Output)
        self._tabPage_Inputs.Controls.Add(self._groupBox_Input)
        self._tabPage_Inputs.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                        GraphicsUnit.Point, 178)
        self._tabPage_Inputs.Location = Point(4, 22)
        self._tabPage_Inputs.Name = "tabPage_Inputs"
        self._tabPage_Inputs.Padding = Padding(3)
        self._tabPage_Inputs.Size = Size(701, 418)
        self._tabPage_Inputs.TabIndex = 0
        self._tabPage_Inputs.Text = "Input/Output"
        self._tabPage_Inputs.UseVisualStyleBackColor = True
        # 
        # groupBox_Input
        # 
        self._groupBox_Input.Controls.Add(self._groupBox_Simulationtimes)
        self._groupBox_Input.Controls.Add(self._groupBox_InputTimeseries)
        self._groupBox_Input.Controls.Add(self._groupBox_InputMaps)
        self._groupBox_Input.Controls.Add(self._button_WorkDirect)
        self._groupBox_Input.Controls.Add(self._textBox_WorkDirect)
        self._groupBox_Input.Controls.Add(self._label_WorkDirect)
        self._groupBox_Input.Font = Font("Microsoft Sans Serif", 9, FontStyle.Bold,
                                                        GraphicsUnit.Point, 178)
        self._groupBox_Input.ForeColor = Color.MidnightBlue
        self._groupBox_Input.Location = Point(3, 0)
        self._groupBox_Input.Name = "groupBox_Input"
        self._groupBox_Input.Size = Size(692, 325)
        self._groupBox_Input.TabIndex = 0
        self._groupBox_Input.TabStop = False
        self._groupBox_Input.Text = "Input"
        # 
        # label_WorkDirect
        # 
        self._label_WorkDirect.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                          GraphicsUnit.Point, 178)
        self._label_WorkDirect.ForeColor = Color.Black
        self._label_WorkDirect.Location = Point(6, 20)
        self._label_WorkDirect.Name = "label_WorkDirect"
        self._label_WorkDirect.Size = Size(118, 20)
        self._label_WorkDirect.TabIndex = 0
        self._label_WorkDirect.Text = "Working Directory"
        # 
        # textBox_WorkDirect
        # 
        self._textBox_WorkDirect.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                            GraphicsUnit.Point, 178)
        self._textBox_WorkDirect.Location = Point(118, 20)
        self._textBox_WorkDirect.Name = "textBox_WorkDirect"
        self._textBox_WorkDirect.Size = Size(526, 21)
        self._textBox_WorkDirect.TabIndex = 1
        self._textBox_WorkDirect.LostFocus+=self.Text_WorkDirectChange
        # 
        # button_WorkDirect
        #
        self._button_WorkDirect.Image=Image.FromFile("icons\\folder.png")
        self._button_WorkDirect.Location = Point(650, 20)
        self._button_WorkDirect.Name = "button_WorkDirect"
        self._button_WorkDirect.Size = Size(32, 23)
        self._button_WorkDirect.TabIndex = 2
        self._button_WorkDirect.UseVisualStyleBackColor = True
        self._button_WorkDirect.Click+=self.Button_WorkDirectClick
        # 
        # groupBox_InputMaps
        # 
        self._groupBox_InputMaps.Controls.Add(self._button_Isochron)
        self._groupBox_InputMaps.Controls.Add(self._button__Soilmap)
        self._groupBox_InputMaps.Controls.Add(self._textBox_Soilmap)
        self._groupBox_InputMaps.Controls.Add(self._textBox_Isochron)
        self._groupBox_InputMaps.Controls.Add(self._label_Soilmap)
        self._groupBox_InputMaps.Controls.Add(self._button_Landusemap)
        self._groupBox_InputMaps.Controls.Add(self._label_Isochron)
        self._groupBox_InputMaps.Controls.Add(self._textBox__Landusemap)
        self._groupBox_InputMaps.Controls.Add(self._label_Landusemap)
        self._groupBox_InputMaps.Controls.Add(self._button_ThiessenT)
        self._groupBox_InputMaps.Controls.Add(self._button_Demmap)
        self._groupBox_InputMaps.Controls.Add(self._textBox_Demmap)
        self._groupBox_InputMaps.Controls.Add(self._textBox_ThiessenT)
        self._groupBox_InputMaps.Controls.Add(self._label_Demmap)
        self._groupBox_InputMaps.Controls.Add(self._label_ThiessenP)
        self._groupBox_InputMaps.Controls.Add(self._label_ThiessenT)
        self._groupBox_InputMaps.Controls.Add(self._textBox_ThiessenP)
        self._groupBox_InputMaps.Controls.Add(self._button_ThiessenP)
        self._groupBox_InputMaps.Location = Point(6, 44)
        self._groupBox_InputMaps.Name = "groupBox_InputMaps"
        self._groupBox_InputMaps.Size = Size(680, 115)
        self._groupBox_InputMaps.TabIndex = 3
        self._groupBox_InputMaps.TabStop = False
        self._groupBox_InputMaps.Text = "Input Maps"
        # 
        # label_Demmap
        # 
        self._label_Demmap.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                      GraphicsUnit.Point, 178)
        self._label_Demmap.ForeColor = Color.Black
        self._label_Demmap.Location = Point(1, 25)
        self._label_Demmap.Name = "label_Demmap"
        self._label_Demmap.Size = Size(66, 22)
        self._label_Demmap.TabIndex = 0
        self._label_Demmap.Text = "Dem map"
        # 
        # textBox_Demmap
        # 
        self._textBox_Demmap.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                        GraphicsUnit.Point, 178)
        self._textBox_Demmap.Location = Point(85, 25)
        self._textBox_Demmap.Name = "textBox_Demmap"
        self._textBox_Demmap.Size = Size(220, 21)
        self._textBox_Demmap.TabIndex = 1
        self._textBox_Demmap.TextChanged+=self.Text_Change
        # 
        # button_Demmap
        #
        self._button_Demmap.Image = Image.FromFile("icons\\file.png")
        self._button_Demmap.Location = Point(310, 25)
        self._button_Demmap.Name = "button_Demmap"
        self._button_Demmap.Size = Size(32, 23)
        self._button_Demmap.TabIndex = 2
        self._button_Demmap.UseVisualStyleBackColor = True
        self._button_Demmap.Click += self.Button_DemClick
        # 
        # label_Landusemap
        # 
        self._label_Landusemap.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                          GraphicsUnit.Point, 178)
        self._label_Landusemap.ForeColor = Color.Black
        self._label_Landusemap.Location = Point(1, 54)
        self._label_Landusemap.Name = "label_Landusemap"
        self._label_Landusemap.Size = Size(83, 22)
        self._label_Landusemap.TabIndex = 3
        self._label_Landusemap.Text = "Landuse map"
        # 
        # textBox__Landusemap
        # 
        self._textBox__Landusemap.Font = Font("Microsoft Sans Serif", 9,
                                                             FontStyle.Regular,
                                                             GraphicsUnit.Point, 178)
        self._textBox__Landusemap.Location = Point(85, 54)
        self._textBox__Landusemap.Name = "textBox__Landusemap"
        self._textBox__Landusemap.Size = Size(220, 21)
        self._textBox__Landusemap.TabIndex = 4
        self._textBox__Landusemap.TextChanged += self.Text_Change
        # 
        # button_Landusemap
        #
        self._button_Landusemap.Image = Image.FromFile("icons\\file.png")
        self._button_Landusemap.Location = Point(310, 54)
        self._button_Landusemap.Name = "button_Landusemap"
        self._button_Landusemap.Size = Size(32, 23)
        self._button_Landusemap.TabIndex = 5
        self._button_Landusemap.UseVisualStyleBackColor = True
        self._button_Landusemap.Click += self.Button_LanduseClick
        # 
        # label_Soilmap
        # 
        self._label_Soilmap.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                       GraphicsUnit.Point, 178)
        self._label_Soilmap.ForeColor = Color.Black
        self._label_Soilmap.Location = Point(1, 82)
        self._label_Soilmap.Name = "label_Soilmap"
        self._label_Soilmap.Size = Size(66, 22)
        self._label_Soilmap.TabIndex = 6
        self._label_Soilmap.Text = "Soil map"
        # 
        # textBox_Soilmap
        # 
        self._textBox_Soilmap.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                         GraphicsUnit.Point, 178)
        self._textBox_Soilmap.Location = Point(85, 82)
        self._textBox_Soilmap.Name = "textBox_Soilmap"
        self._textBox_Soilmap.Size = Size(220, 21)
        self._textBox_Soilmap.TabIndex = 7
        self._textBox_Soilmap.TextChanged += self.Text_Change
        # 
        # button__Soilmap
        #
        self._button__Soilmap.Image = Image.FromFile("icons\\file.png")
        self._button__Soilmap.Location = Point(310, 82)
        self._button__Soilmap.Name = "button__Soilmap"
        self._button__Soilmap.Size = Size(32, 23)
        self._button__Soilmap.TabIndex = 8
        self._button__Soilmap.UseVisualStyleBackColor = True
        self._button__Soilmap.Click += self.Button_SoilClick
        # 
        # groupBox_Simulationtimes
        # 
        self._groupBox_Simulationtimes.Controls.Add(self._textBox__Notimestep)
        self._groupBox_Simulationtimes.Controls.Add(self._textBox_Finaltimestep)
        self._groupBox_Simulationtimes.Controls.Add(self._textBox_Starttimestep)
        self._groupBox_Simulationtimes.Controls.Add(self._label_Notimestep)
        self._groupBox_Simulationtimes.Controls.Add(self._label_Starttimestep)
        self._groupBox_Simulationtimes.Controls.Add(self._label_Finaltimestep)
        self._groupBox_Simulationtimes.Location = Point(6, 261)
        self._groupBox_Simulationtimes.Name = "groupBox_Simulationtimes"
        self._groupBox_Simulationtimes.Size = Size(680, 55)
        self._groupBox_Simulationtimes.TabIndex = 5
        self._groupBox_Simulationtimes.TabStop = False
        self._groupBox_Simulationtimes.Text = "Simulation times"
        # 
        # label_Finaltimestep
        # 
        self._label_Finaltimestep.Font = Font("Microsoft Sans Serif", 9,
                                                             FontStyle.Regular,
                                                             GraphicsUnit.Point, 178)
        self._label_Finaltimestep.ForeColor = Color.Black
        self._label_Finaltimestep.Location = Point(257, 23)
        self._label_Finaltimestep.Name = "label_Finaltimestep"
        self._label_Finaltimestep.Size = Size(94, 22)
        self._label_Finaltimestep.TabIndex = 28
        self._label_Finaltimestep.Text = "Final time step"
        # 
        # label_Starttimestep
        # 
        self._label_Starttimestep.Font = Font("Microsoft Sans Serif", 9,
                                                             FontStyle.Regular,
                                                             GraphicsUnit.Point, 178)
        self._label_Starttimestep.ForeColor = Color.Black
        self._label_Starttimestep.Location = Point(17, 23)
        self._label_Starttimestep.Name = "label_Starttimestep"
        self._label_Starttimestep.Size = Size(93, 22)
        self._label_Starttimestep.TabIndex = 29
        self._label_Starttimestep.Text = "Start time step"
        # 
        # label_Notimestep
        # 
        self._label_Notimestep.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                          GraphicsUnit.Point, 178)
        self._label_Notimestep.ForeColor = Color.Black
        self._label_Notimestep.Location = Point(525, 23)
        self._label_Notimestep.Name = "label_Notimestep"
        self._label_Notimestep.Size = Size(93, 22)
        self._label_Notimestep.TabIndex = 30
        self._label_Notimestep.Text = "Time step"
        # 
        # textBox_Starttimestep
        # 
        self._textBox_Starttimestep.Font = Font("Microsoft Sans Serif", 9,
                                                               FontStyle.Regular,
                                                               GraphicsUnit.Point, 178)
        self._textBox_Starttimestep.Location = Point(112, 23)
        self._textBox_Starttimestep.Name = "textBox_Starttimestep"
        self._textBox_Starttimestep.Size = Size(74, 21)
        self._textBox_Starttimestep.TabIndex = 31
        self._textBox_Starttimestep.Text = "1"

        # 
        # textBox_Finaltimestep
        # 
        self._textBox_Finaltimestep.Font = Font("Microsoft Sans Serif", 9,
                                                               FontStyle.Regular,
                                                               GraphicsUnit.Point, 178)
        self._textBox_Finaltimestep.Location = Point(349, 23)
        self._textBox_Finaltimestep.Name = "textBox_Finaltimestep"
        self._textBox_Finaltimestep.Size = Size(74, 21)
        self._textBox_Finaltimestep.TabIndex = 32
        self._textBox_Finaltimestep.Text = "365"
        # 
        # textBox__Notimestep
        # 
        self._textBox__Notimestep.Font = Font("Microsoft Sans Serif", 9,
                                                             FontStyle.Regular,
                                                             GraphicsUnit.Point, 178)
        self._textBox__Notimestep.Location = Point(589, 23)
        self._textBox__Notimestep.Name = "textBox__Notimestep"
        self._textBox__Notimestep.Size = Size(74, 21)
        self._textBox__Notimestep.TabIndex = 33
        self._textBox__Notimestep.Text = "1"
        # 
        # groupBox_Output
        # 
        self._groupBox_Output.Controls.Add(self._textBox_resultsname)
        self._groupBox_Output.Controls.Add(self._label_resultsname)
        self._groupBox_Output.Controls.Add(self._button_OutputDirectory)
        self._groupBox_Output.Controls.Add(self._textBox_OutputDirectory)
        self._groupBox_Output.Controls.Add(self._label_OutputDirectory)
        self._groupBox_Output.Font = Font("Microsoft Sans Serif", 9, FontStyle.Bold,
                                                         GraphicsUnit.Point, 178)
        self._groupBox_Output.ForeColor = Color.MidnightBlue
        self._groupBox_Output.Location = Point(3, 326)
        self._groupBox_Output.Name = "groupBox_Output"
        self._groupBox_Output.Size = Size(692, 85)
        self._groupBox_Output.TabIndex = 1
        self._groupBox_Output.TabStop = False
        self._groupBox_Output.Text = "Output"
        # 
        # label_OutputDirectory
        # 
        self._label_OutputDirectory.Font = Font("Microsoft Sans Serif", 9,
                                                               FontStyle.Regular,
                                                               GraphicsUnit.Point, 178)
        self._label_OutputDirectory.ForeColor = Color.Black
        self._label_OutputDirectory.Location = Point(11, 23)
        self._label_OutputDirectory.Name = "label_OutputDirectory"
        self._label_OutputDirectory.Size = Size(118, 20)
        self._label_OutputDirectory.TabIndex = 3
        self._label_OutputDirectory.Text = "Output Directory"
        # 
        # textBox_OutputDirectory
        # 
        self._textBox_OutputDirectory.Font = Font("Microsoft Sans Serif", 9,
                                                                 FontStyle.Regular,
                                                                 GraphicsUnit.Point, 178)
        self._textBox_OutputDirectory.Location = Point(118, 23)
        self._textBox_OutputDirectory.Name = "textBox_OutputDirectory"
        self._textBox_OutputDirectory.Size = Size(526, 21)
        self._textBox_OutputDirectory.TabIndex = 4
        # 
        # button_OutputDirectory
        #
        self._button_OutputDirectory.Image = Image.FromFile("icons\\folder.png")
        self._button_OutputDirectory.Location = Point(650, 23)
        self._button_OutputDirectory.Name = "button_OutputDirectory"
        self._button_OutputDirectory.Size = Size(32, 23)
        self._button_OutputDirectory.TabIndex = 5
        self._button_OutputDirectory.UseVisualStyleBackColor = True
        self._button_OutputDirectory.Click += self.Button_OutputDirectoryClick
        # 
        # label_resultsname
        # 
        self._label_resultsname.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                           GraphicsUnit.Point, 178)
        self._label_resultsname.ForeColor = Color.Black
        self._label_resultsname.Location = Point(11, 52)
        self._label_resultsname.Name = "label_resultsname"
        self._label_resultsname.Size = Size(219, 20)
        self._label_resultsname.TabIndex = 6
        self._label_resultsname.Text = "The file name for summarized results"
        # 
        # textBox_resultsname
        # 
        self._textBox_resultsname.Font = Font("Microsoft Sans Serif", 9,
                                                             FontStyle.Regular,
                                                             GraphicsUnit.Point, 178)
        self._textBox_resultsname.Location = Point(236, 52)
        self._textBox_resultsname.Name = "textBox_resultsname"
        self._textBox_resultsname.Size = Size(408, 21)
        self._textBox_resultsname.TabIndex = 7
        self._textBox_resultsname.Text = "results"
        # 
        # tabControl_Input_Output
        # 
        self._tabControl_Input_Output.Controls.Add(self._tabPage_Inputs)
        self._tabControl_Input_Output.Controls.Add(self._tabPage_Parameters)
        self._tabControl_Input_Output.Controls.Add(self._tabPage_Display)
        self._tabControl_Input_Output.Controls.Add(self._tabPage_About)
        self._tabControl_Input_Output.Location = Point(-1, 0)
        self._tabControl_Input_Output.Name = "tabControl_Input_Output"
        self._tabControl_Input_Output.SelectedIndex = 0
        self._tabControl_Input_Output.Size = Size(709, 444)
        self._tabControl_Input_Output.TabIndex = 0
        # 
        # groupBox_Snowmelt
        # 
        self._groupBox_Snowmelt.Controls.Add(self._label_Csnow)
        self._groupBox_Snowmelt.Controls.Add(self._label_To)
        self._groupBox_Snowmelt.Controls.Add(self._textBox_Csnow)
        self._groupBox_Snowmelt.Controls.Add(self._textBox_To)
        self._groupBox_Snowmelt.Font = Font("Microsoft Sans Serif", 9, FontStyle.Bold,
                                                           GraphicsUnit.Point, 178)
        self._groupBox_Snowmelt.ForeColor = Color.MidnightBlue
        self._groupBox_Snowmelt.Location = Point(8, 45)
        self._groupBox_Snowmelt.Name = "groupBox_Snowmelt"
        self._groupBox_Snowmelt.Size = Size(338, 80)
        self._groupBox_Snowmelt.TabIndex = 0
        self._groupBox_Snowmelt.TabStop = False
        self._groupBox_Snowmelt.Text = "Snowmelt process"
        # 
        # groupBox_PET
        # 
        self._groupBox_PET.Controls.Add(self._label_Ket)
        self._groupBox_PET.Controls.Add(self._textBox_Ket)
        self._groupBox_PET.Font = Font("Microsoft Sans Serif", 9, FontStyle.Bold,
                                                      GraphicsUnit.Point, 178)
        self._groupBox_PET.ForeColor = Color.MidnightBlue
        self._groupBox_PET.Location = Point(8, 136)
        self._groupBox_PET.Name = "groupBox_PET"
        self._groupBox_PET.Size = Size(338, 55)
        self._groupBox_PET.TabIndex = 1
        self._groupBox_PET.TabStop = False
        self._groupBox_PET.Text = "Potential Evapotranspiration (PET)"
        # 
        # textBox_To
        # 
        self._textBox_To.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                    GraphicsUnit.Point, 178)
        self._textBox_To.Location = Point(258, 24)
        self._textBox_To.Name = "textBox_To"
        self._textBox_To.Size = Size(74, 21)
        self._textBox_To.TabIndex = 2
        self._textBox_To.Text = "1.99"
        # 
        # label_Specifymodelparameters
        # 
        self._label_Specifymodelparameters.Font = Font("Microsoft Sans Serif", 9.75,
                                                                      FontStyle.Bold,
                                                                      GraphicsUnit.Point, 178)
        self._label_Specifymodelparameters.ForeColor = Color.Black
        self._label_Specifymodelparameters.Location = Point(7, 14)
        self._label_Specifymodelparameters.Name = "label_Specifymodelparameters"
        self._label_Specifymodelparameters.Size = Size(328, 21)
        self._label_Specifymodelparameters.TabIndex = 2
        self._label_Specifymodelparameters.Text = "Specify the model parameters:"
        # 
        # groupBox_AET
        # 
        self._groupBox_AET.Controls.Add(self._label_gama)
        self._groupBox_AET.Controls.Add(self._label_alfa)
        self._groupBox_AET.Controls.Add(self._textBox_alfa)
        self._groupBox_AET.Controls.Add(self._textBox_gama)
        self._groupBox_AET.Font = Font("Microsoft Sans Serif", 9, FontStyle.Bold,
                                                      GraphicsUnit.Point, 178)
        self._groupBox_AET.ForeColor = Color.MidnightBlue
        self._groupBox_AET.Location = Point(8, 197)
        self._groupBox_AET.Name = "groupBox_AET"
        self._groupBox_AET.Size = Size(338, 80)
        self._groupBox_AET.TabIndex = 4
        self._groupBox_AET.TabStop = False
        self._groupBox_AET.Text = "Actual Evapotranspiration (AET)"
        # 
        # groupBox_SurfaceRunoff
        # 
        self._groupBox_SurfaceRunoff.Controls.Add(self._label_X)
        self._groupBox_SurfaceRunoff.Controls.Add(self._label_landa)
        self._groupBox_SurfaceRunoff.Controls.Add(self._groupBox_CN)
        self._groupBox_SurfaceRunoff.Controls.Add(self._textBox_X)
        self._groupBox_SurfaceRunoff.Controls.Add(self._textBox_landa)
        self._groupBox_SurfaceRunoff.Font = Font("Microsoft Sans Serif", 9,
                                                                FontStyle.Bold,
                                                                GraphicsUnit.Point, 178)
        self._groupBox_SurfaceRunoff.ForeColor = Color.MidnightBlue
        self._groupBox_SurfaceRunoff.Location = Point(354, 45)
        self._groupBox_SurfaceRunoff.Name = "groupBox_SurfaceRunoff"
        self._groupBox_SurfaceRunoff.Size = Size(338, 190)
        self._groupBox_SurfaceRunoff.TabIndex = 5
        self._groupBox_SurfaceRunoff.TabStop = False
        self._groupBox_SurfaceRunoff.Text = "Surface Runoff"
        # 
        # groupBox_Baseflow
        # 
        self._groupBox_Baseflow.Controls.Add(self._label_Contribution)
        self._groupBox_Baseflow.Controls.Add(self._label_Beta)
        self._groupBox_Baseflow.Controls.Add(self._textBox_contribution)
        self._groupBox_Baseflow.Controls.Add(self._textBox_beta)
        self._groupBox_Baseflow.Font = Font("Microsoft Sans Serif", 9, FontStyle.Bold,
                                                           GraphicsUnit.Point, 178)
        self._groupBox_Baseflow.ForeColor = Color.MidnightBlue
        self._groupBox_Baseflow.Location = Point(355, 241)
        self._groupBox_Baseflow.Name = "groupBox_Baseflow"
        self._groupBox_Baseflow.Size = Size(338, 84)
        self._groupBox_Baseflow.TabIndex = 6
        self._groupBox_Baseflow.TabStop = False
        self._groupBox_Baseflow.Text = "Base flow"
        # 
        # button_Run
        # 
        self._button_Run.BackColor = Color.Transparent
        self._button_Run.Font = Font("Microsoft Sans Serif", 9.75, FontStyle.Bold,
                                                    GraphicsUnit.Point, 178)
        self._button_Run.Image = Image.FromFile("icons\\run.png")
        self._button_Run.Location = Point(161, 373)
        self._button_Run.Name = "button_Run"
        self._button_Run.RightToLeft = RightToLeft.No
        self._button_Run.Size = Size(380, 35)
        self._button_Run.TabIndex = 7
        self._button_Run.Text = "Run"
        self._button_Run.UseVisualStyleBackColor = False
        self._button_Run.Click += self.Button_Run_Click
        # 
        # textBox_Csnow
        # 
        self._textBox_Csnow.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                       GraphicsUnit.Point, 178)
        self._textBox_Csnow.Location = Point(258, 50)
        self._textBox_Csnow.Name = "textBox_Csnow"
        self._textBox_Csnow.Size = Size(74, 21)
        self._textBox_Csnow.TabIndex = 4
        self._textBox_Csnow.Text = "2.00"
        # 
        # textBox_gama
        # 
        self._textBox_gama.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                      GraphicsUnit.Point, 178)
        self._textBox_gama.Location = Point(258, 50)
        self._textBox_gama.Name = "textBox_gama"
        self._textBox_gama.Size = Size(74, 21)
        self._textBox_gama.TabIndex = 6
        self._textBox_gama.Text = "0.80"
        # 
        # textBox_alfa
        # 
        self._textBox_alfa.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                      GraphicsUnit.Point, 178)
        self._textBox_alfa.Location = Point(258, 24)
        self._textBox_alfa.Name = "textBox_alfa"
        self._textBox_alfa.Size = Size(74, 21)
        self._textBox_alfa.TabIndex = 7
        self._textBox_alfa.Text = "0.10"
        # 
        # textBox_Ket
        # 
        self._textBox_Ket.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                     GraphicsUnit.Point, 178)
        self._textBox_Ket.Location = Point(258, 24)
        self._textBox_Ket.Name = "textBox_Ket"
        self._textBox_Ket.Size = Size(74, 21)
        self._textBox_Ket.TabIndex = 3
        self._textBox_Ket.Text = "0.0037"
        # 
        # textBox_landa
        # 
        self._textBox_landa.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                       GraphicsUnit.Point, 178)
        self._textBox_landa.Location = Point(258, 26)
        self._textBox_landa.Name = "textBox_landa"
        self._textBox_landa.Size = Size(74, 21)
        self._textBox_landa.TabIndex = 4
        self._textBox_landa.Text = "0.01"
        # 
        # textBox_X
        # 
        self._textBox_X.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                   GraphicsUnit.Point, 178)
        self._textBox_X.Location = Point(258, 55)
        self._textBox_X.Name = "textBox_X"
        self._textBox_X.Size = Size(74, 21)
        self._textBox_X.TabIndex = 5
        self._textBox_X.Text = "0.80"
        # 
        # groupBox_LAI
        # 
        self._groupBox_LAI.Controls.Add(self._label_d)
        self._groupBox_LAI.Controls.Add(self._label_Clai)
        self._groupBox_LAI.Controls.Add(self._textBox_d)
        self._groupBox_LAI.Controls.Add(self._textBox_Clai)
        self._groupBox_LAI.Font = Font("Microsoft Sans Serif", 9, FontStyle.Bold,
                                                      GraphicsUnit.Point, 178)
        self._groupBox_LAI.ForeColor = Color.MidnightBlue
        self._groupBox_LAI.Location = Point(8, 280)
        self._groupBox_LAI.Name = "groupBox_LAI"
        self._groupBox_LAI.Size = Size(338, 80)
        self._groupBox_LAI.TabIndex = 6
        self._groupBox_LAI.TabStop = False
        self._groupBox_LAI.Text = "Leaf Area Index (LAI)"
        # 
        # groupBox_CN
        # 
        self._groupBox_CN.Controls.Add(self._label_Cmin)
        self._groupBox_CN.Controls.Add(self._label_k_cn)
        self._groupBox_CN.Controls.Add(self._textBox_k_cn)
        self._groupBox_CN.Controls.Add(self._textBox_Cmin)
        self._groupBox_CN.Location = Point(7, 90)
        self._groupBox_CN.Name = "groupBox_CN"
        self._groupBox_CN.Size = Size(324, 90)
        self._groupBox_CN.TabIndex = 7
        self._groupBox_CN.TabStop = False
        self._groupBox_CN.Text = "Dynamic Curve Number (CN)"
        # 
        # textBox_beta
        # 
        self._textBox_beta.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                      GraphicsUnit.Point, 178)
        self._textBox_beta.Location = Point(258, 24)
        self._textBox_beta.Name = "textBox_beta"
        self._textBox_beta.Size = Size(74, 21)
        self._textBox_beta.TabIndex = 4
        self._textBox_beta.Text = "0.95"
        # 
        # textBox_contribution
        # 
        self._textBox_contribution.Font = Font("Microsoft Sans Serif", 9,
                                                              FontStyle.Regular,
                                                              GraphicsUnit.Point, 178)
        self._textBox_contribution.Location = Point(258, 50)
        self._textBox_contribution.Name = "textBox_contribution"
        self._textBox_contribution.Size = Size(74, 21)
        self._textBox_contribution.TabIndex = 5
        self._textBox_contribution.Text = "0.20"
        # 
        # textBox_Cmin
        # 
        self._textBox_Cmin.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                      GraphicsUnit.Point, 178)
        self._textBox_Cmin.Location = Point(246, 30)
        self._textBox_Cmin.Name = "textBox_Cmin"
        self._textBox_Cmin.Size = Size(74, 21)
        self._textBox_Cmin.TabIndex = 4
        self._textBox_Cmin.Text = "0.40"
        # 
        # textBox_k_cn
        # 
        self._textBox_k_cn.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                      GraphicsUnit.Point, 178)
        self._textBox_k_cn.Location = Point(246, 58)
        self._textBox_k_cn.Name = "textBox_k_cn"
        self._textBox_k_cn.Size = Size(74, 21)
        self._textBox_k_cn.TabIndex = 5
        self._textBox_k_cn.Text = "0.80"
        # 
        # textBox_Clai
        # 
        self._textBox_Clai.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                      GraphicsUnit.Point, 178)
        self._textBox_Clai.Location = Point(258, 24)
        self._textBox_Clai.Name = "textBox_Clai"
        self._textBox_Clai.Size = Size(74, 21)
        self._textBox_Clai.TabIndex = 4
        self._textBox_Clai.Text = "0.56"
        # 
        # textBox_d
        # 
        self._textBox_d.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                   GraphicsUnit.Point, 178)
        self._textBox_d.Location = Point(258, 50)
        self._textBox_d.Name = "textBox_d"
        self._textBox_d.Size = Size(74, 21)
        self._textBox_d.TabIndex = 5
        self._textBox_d.Text = "0.016"
        # 
        # label_To
        # 
        self._label_To.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                  GraphicsUnit.Point, 178)
        self._label_To.ForeColor = Color.Black
        self._label_To.Location = Point(6, 24)
        self._label_To.Name = "label_To"
        self._label_To.Size = Size(151, 22)
        self._label_To.TabIndex = 7
        self._label_To.Text = "base temperature (To)"
        # 
        # label_Csnow
        # 
        self._label_Csnow.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                     GraphicsUnit.Point, 178)
        self._label_Csnow.ForeColor = Color.Black
        self._label_Csnow.Location = Point(6, 50)
        self._label_Csnow.Name = "label_Csnow"
        self._label_Csnow.Size = Size(151, 22)
        self._label_Csnow.TabIndex = 8
        self._label_Csnow.Text = "melt factor (Csnow)"
        # 
        # label_alfa
        # 
        self._label_alfa.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                    GraphicsUnit.Point, 178)
        self._label_alfa.ForeColor = Color.Black
        self._label_alfa.Location = Point(6, 24)
        self._label_alfa.Name = "label_alfa"
        self._label_alfa.Size = Size(151, 22)
        self._label_alfa.TabIndex = 12
        self._label_alfa.Text = "alfa coefficient (α)"
        # 
        # label_gama
        # 
        self._label_gama.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                    GraphicsUnit.Point, 178)
        self._label_gama.ForeColor = Color.Black
        self._label_gama.Location = Point(6, 50)
        self._label_gama.Name = "label_gama"
        self._label_gama.Size = Size(151, 22)
        self._label_gama.TabIndex = 13
        self._label_gama.Text = "gama coefficient (ɣ)"
        # 
        # label_Beta
        # 
        self._label_Beta.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                    GraphicsUnit.Point, 178)
        self._label_Beta.ForeColor = Color.Black
        self._label_Beta.Location = Point(6, 24)
        self._label_Beta.Name = "label_Beta"
        self._label_Beta.Size = Size(151, 22)
        self._label_Beta.TabIndex = 13
        self._label_Beta.Text = "Beta coefficient (β) "
        # 
        # label_Contribution
        # 
        self._label_Contribution.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                            GraphicsUnit.Point, 178)
        self._label_Contribution.ForeColor = Color.Black
        self._label_Contribution.Location = Point(6, 50)
        self._label_Contribution.Name = "label_Contribution"
        self._label_Contribution.Size = Size(151, 22)
        self._label_Contribution.TabIndex = 14
        self._label_Contribution.Text = "Contribution factor (ɸ) "
        # 
        # label_Ket
        # 
        self._label_Ket.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                   GraphicsUnit.Point, 178)
        self._label_Ket.ForeColor = Color.Black
        self._label_Ket.Location = Point(6, 24)
        self._label_Ket.Name = "label_Ket"
        self._label_Ket.Size = Size(151, 22)
        self._label_Ket.TabIndex = 11
        self._label_Ket.Text = "Ket coefficient"
        # 
        # label_landa
        # 
        self._label_landa.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                     GraphicsUnit.Point, 178)
        self._label_landa.ForeColor = Color.Black
        self._label_landa.Location = Point(6, 26)
        self._label_landa.Name = "label_landa"
        self._label_landa.Size = Size(151, 22)
        self._label_landa.TabIndex = 12
        self._label_landa.Text = "lamda coefficient (λ) "
        # 
        # label_X
        # 
        self._label_X.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                 GraphicsUnit.Point, 178)
        self._label_X.ForeColor = Color.Black
        self._label_X.Location = Point(6, 55)
        self._label_X.Name = "label_X"
        self._label_X.Size = Size(151, 22)
        self._label_X.TabIndex = 13
        self._label_X.Text = "X coefficient"
        # 
        # label_Clai
        # 
        self._label_Clai.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                    GraphicsUnit.Point, 178)
        self._label_Clai.ForeColor = Color.Black
        self._label_Clai.Location = Point(6, 24)
        self._label_Clai.Name = "label_Clai"
        self._label_Clai.Size = Size(120, 22)
        self._label_Clai.TabIndex = 12
        self._label_Clai.Text = "LAI coefficient (Clai)"
        # 
        # label_d
        # 
        self._label_d.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                 GraphicsUnit.Point, 178)
        self._label_d.ForeColor = Color.Black
        self._label_d.Location = Point(6, 50)
        self._label_d.Name = "label_d"
        self._label_d.Size = Size(74, 22)
        self._label_d.TabIndex = 13
        self._label_d.Text = "d coefficient"
        # 
        # label_k_cn
        # 
        self._label_k_cn.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                    GraphicsUnit.Point, 178)
        self._label_k_cn.ForeColor = Color.Black
        self._label_k_cn.Location = Point(6, 58)
        self._label_k_cn.Name = "label_k_cn"
        self._label_k_cn.Size = Size(71, 22)
        self._label_k_cn.TabIndex = 14
        self._label_k_cn.Text = "k coefficient"
        # 
        # label_Cmin
        # 
        self._label_Cmin.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                    GraphicsUnit.Point, 178)
        self._label_Cmin.ForeColor = Color.Black
        self._label_Cmin.Location = Point(6, 30)
        self._label_Cmin.Name = "label_Cmin"
        self._label_Cmin.Size = Size(131, 22)
        self._label_Cmin.TabIndex = 15
        self._label_Cmin.Text = "reduction factor (Cmin)"
        # 
        # label_aboutmodel_Titr
        # 
        self._label_aboutmodel_Titr.Font = Font("Microsoft Sans Serif", 9, FontStyle.Bold,
                                                               GraphicsUnit.Point, 178)
        self._label_aboutmodel_Titr.Location = Point(14, 18)
        self._label_aboutmodel_Titr.Name = "label_aboutmodel_Titr"
        self._label_aboutmodel_Titr.Size = Size(104, 28)
        self._label_aboutmodel_Titr.TabIndex = 0
        self._label_aboutmodel_Titr.Text = "GISHM:"
        # 
        # label_aboutmodel
        # 
        self._label_aboutmodel.Location = Point(14, 46)
        self._label_aboutmodel.Name = "label_aboutmodel"
        self._label_aboutmodel.Size = Size(663, 200)
        self._label_aboutmodel.TabIndex = 1
        self._label_aboutmodel.Text = """GIS-based Hydrological Model (GISHM) is an object-oriented semi-distributed daily based model that have been developed for simulation of water balance components using a dynamic CN maps. The simulation components include: snowmelt, surface runoff [Based on a daily Curve Number], potential and actual evapotranspiration, grounwater recharge and base flow using daily climate data. It is required to provide input maps as ESRI-ascii grid files through Graphical User Interface (GUI). An example run file has been provided in the local installation directory of the user’s computer system to demonstrate and facilitate the model preparation to run. Further details of the model can be found in the manual (not completed yet). 
The GISHM has been developed using IronPython package and MapCalculate library. 
The GISHM and its interface are open-source and freely available upon request for academic use. This model has been developed by Zahra Parisay in collaboration with Vahedberdi Sheikh, Khodayar Abdollahi, Abdolreza Bahremand and Chooghi Bairam Komaki.
"""
        # 
        # groupBox_Hydrograph
        # 
        self._groupBox_Hydrograph.Controls.Add(self._pictureBox_Hydrograph)
        self._groupBox_Hydrograph.Font = Font("Microsoft Sans Serif", 9, FontStyle.Bold,
                                                             GraphicsUnit.Point, 178)
        self._groupBox_Hydrograph.ForeColor = Color.MidnightBlue
        self._groupBox_Hydrograph.Location = Point(3, 11)
        self._groupBox_Hydrograph.Name = "groupBox_Hydrograph"
        self._groupBox_Hydrograph.Size = Size(692, 308)
        self._groupBox_Hydrograph.TabIndex = 0
        self._groupBox_Hydrograph.TabStop = False
        self._groupBox_Hydrograph.Text = "Hydrograph"
        # 
        # groupBox_Evaluationcriteria
        # 
        self._groupBox_Evaluationcriteria.Controls.Add(self._label_bR2)
        self._groupBox_Evaluationcriteria.Controls.Add(self._label_R2)
        self._groupBox_Evaluationcriteria.Controls.Add(self._label_bias)
        self._groupBox_Evaluationcriteria.Controls.Add(self._label3_modifiedKGE)
        self._groupBox_Evaluationcriteria.Controls.Add(self._label_KGE)
        self._groupBox_Evaluationcriteria.Controls.Add(self._label_NS)
        self._groupBox_Evaluationcriteria.Controls.Add(self._textBox_bR2)
        self._groupBox_Evaluationcriteria.Controls.Add(self._textBox_bias)
        self._groupBox_Evaluationcriteria.Controls.Add(self._textBox_modifiedKGE)
        self._groupBox_Evaluationcriteria.Controls.Add(self._textBox_KGE)
        self._groupBox_Evaluationcriteria.Controls.Add(self._textBox_R2)
        self._groupBox_Evaluationcriteria.Controls.Add(self._textBox__NS)
        self._groupBox_Evaluationcriteria.Font = Font("Microsoft Sans Serif", 9,
                                                                     FontStyle.Bold,
                                                                     GraphicsUnit.Point, 178)
        self._groupBox_Evaluationcriteria.ForeColor = Color.MidnightBlue
        self._groupBox_Evaluationcriteria.Location = Point(3, 322)
        self._groupBox_Evaluationcriteria.Name = "groupBox_Evaluationcriteria"
        self._groupBox_Evaluationcriteria.Size = Size(692, 90)
        self._groupBox_Evaluationcriteria.TabIndex = 1
        self._groupBox_Evaluationcriteria.TabStop = False
        self._groupBox_Evaluationcriteria.Text = "Evaluation Criteria"
        # 
        # pictureBox_Hydrograph
        #
        self._pictureBox_Hydrograph.Location = Point(6, 20)
        self._pictureBox_Hydrograph.Name = "pictureBox_Hydrograph"
        self._pictureBox_Hydrograph.Size = Size(680, 280)
        self._pictureBox_Hydrograph.TabIndex = 0
        self._pictureBox_Hydrograph.TabStop = False
        self._pictureBox_Hydrograph.IsEnableHZoom = True
        self._pictureBox_Hydrograph.IsEnableVZoom = False
        self._pictureBox_Hydrograph.IsShowHScrollBar = True
        self._pictureBox_Hydrograph.IsAutoScrollRange = True
        self._pictureBox_Hydrograph.ScrollGrace = 0.01
        self._pictureBox_Hydrograph.ZoomEvent+=ZedGraphControl.ZoomEventHandler(self.Zoom_Event)
        # 
        # textBox__NS
        # 
        self._textBox__NS.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                     GraphicsUnit.Point, 178)
        self._textBox__NS.Location = Point(153, 25)
        self._textBox__NS.Name = "textBox__NS"
        self._textBox__NS.ReadOnly = True
        self._textBox__NS.Size = Size(74, 21)
        self._textBox__NS.TabIndex = 0
        # 
        # textBox_R2
        # 
        self._textBox_R2.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                    GraphicsUnit.Point, 178)
        self._textBox_R2.Location = Point(607, 25)
        self._textBox_R2.Name = "textBox_R2"
        self._textBox_R2.ReadOnly = True
        self._textBox_R2.Size = Size(74, 21)
        self._textBox_R2.TabIndex = 1
        # 
        # textBox_KGE
        # 
        self._textBox_KGE.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                     GraphicsUnit.Point, 178)
        self._textBox_KGE.Location = Point(450, 25)
        self._textBox_KGE.Name = "textBox_KGE"
        self._textBox_KGE.ReadOnly = True
        self._textBox_KGE.Size = Size(74, 21)
        self._textBox_KGE.TabIndex = 2
        # 
        # textBox_modifiedKGE
        # 
        self._textBox_modifiedKGE.Font = Font("Microsoft Sans Serif", 9,
                                                             FontStyle.Regular,
                                                             GraphicsUnit.Point, 178)
        self._textBox_modifiedKGE.Location = Point(450, 58)
        self._textBox_modifiedKGE.Name = "textBox_modifiedKGE"
        self._textBox_modifiedKGE.ReadOnly = True
        self._textBox_modifiedKGE.Size = Size(74, 21)
        self._textBox_modifiedKGE.TabIndex = 3
        # 
        # textBox_bias
        # 
        self._textBox_bias.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                      GraphicsUnit.Point, 178)
        self._textBox_bias.Location = Point(153, 58)
        self._textBox_bias.Name = "textBox_bias"
        self._textBox_bias.ReadOnly = True
        self._textBox_bias.Size = Size(74, 21)
        self._textBox_bias.TabIndex = 4
        # 
        # textBox_bR2
        # 
        self._textBox_bR2.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                     GraphicsUnit.Point, 178)
        self._textBox_bR2.Location = Point(607, 58)
        self._textBox_bR2.Name = "textBox_bR2"
        self._textBox_bR2.ReadOnly = True
        self._textBox_bR2.Size = Size(74, 21)
        self._textBox_bR2.TabIndex = 5
        # 
        # label_NS
        # 
        self._label_NS.Font = Font("Microsoft Sans Serif", 9, FontStyle.Bold,
                                                  GraphicsUnit.Point, 178)
        self._label_NS.ForeColor = Color.Black
        self._label_NS.Location = Point(7, 25)
        self._label_NS.Name = "label_NS"
        self._label_NS.Size = Size(139, 23)
        self._label_NS.TabIndex = 6
        self._label_NS.Text = "Nash-Sutcliffe (NSE)"
        # 
        # label_KGE
        # 
        self._label_KGE.Font = Font("Microsoft Sans Serif", 9, FontStyle.Bold,
                                                   GraphicsUnit.Point, 178)
        self._label_KGE.ForeColor = Color.Black
        self._label_KGE.Location = Point(257, 25)
        self._label_KGE.Name = "label_KGE"
        self._label_KGE.Size = Size(130, 23)
        self._label_KGE.TabIndex = 7
        self._label_KGE.Text = "Kling-Gupta (KGE)"
        # 
        # label3_modifiedKGE
        # 
        self._label3_modifiedKGE.Font = Font("Microsoft Sans Serif", 9, FontStyle.Bold,
                                                            GraphicsUnit.Point, 178)
        self._label3_modifiedKGE.ForeColor = Color.Black
        self._label3_modifiedKGE.Location = Point(257, 58)
        self._label3_modifiedKGE.Name = "label3_modifiedKGE"
        self._label3_modifiedKGE.Size = Size(189, 23)
        self._label3_modifiedKGE.TabIndex = 8
        self._label3_modifiedKGE.Text = "modified Kling-Gupta (KGE’) "
        # 
        # label_bias
        # 
        self._label_bias.Font = Font("Microsoft Sans Serif", 9, FontStyle.Bold,
                                                    GraphicsUnit.Point, 178)
        self._label_bias.ForeColor = Color.Black
        self._label_bias.Location = Point(7, 58)
        self._label_bias.Name = "label_bias"
        self._label_bias.Size = Size(96, 23)
        self._label_bias.TabIndex = 9
        self._label_bias.Text = "model bias"
        # 
        # label_R2
        # 
        self._label_R2.Font = Font("Microsoft Sans Serif", 9, FontStyle.Bold,
                                                  GraphicsUnit.Point, 178)
        self._label_R2.ForeColor = Color.Black
        self._label_R2.Location = Point(570, 25)
        self._label_R2.Name = "label_R2"
        self._label_R2.Size = Size(30, 23)
        self._label_R2.TabIndex = 10
        self._label_R2.Text = " R2"
        # 
        # label_bR2
        # 
        self._label_bR2.Font = Font("Microsoft Sans Serif", 9, FontStyle.Bold,
                                                   GraphicsUnit.Point, 178)
        self._label_bR2.ForeColor = Color.Black
        self._label_bR2.Location = Point(570, 58)
        self._label_bR2.Name = "label_bR2"
        self._label_bR2.Size = Size(37, 23)
        self._label_bR2.TabIndex = 11
        self._label_bR2.Text = "bR2"
        # 
        # checkBox_prepro
        # 
        self._checkBox_prepro.Location = Point(359, 334)
        self._checkBox_prepro.Name = "checkBox_prepro"
        self._checkBox_prepro.Size = Size(333, 24)
        self._checkBox_prepro.TabIndex = 8
        self._checkBox_prepro.Text = "Preprocessing data (uncheck in calibration phase)"
        self._checkBox_prepro.UseVisualStyleBackColor = True
        self._checkBox_prepro.Checked=True
        # 
        # button_ThiessenP
        #
        self._button_ThiessenP.Image = Image.FromFile("icons\\file.png")
        self._button_ThiessenP.Location = Point(644, 25)
        self._button_ThiessenP.Name = "button_ThiessenP"
        self._button_ThiessenP.Size = Size(32, 23)
        self._button_ThiessenP.TabIndex = 14
        self._button_ThiessenP.UseVisualStyleBackColor = True
        self._button_ThiessenP.Click += self.Button_ThiessenPClick
        # 
        # textBox_ThiessenP
        # 
        self._textBox_ThiessenP.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                           GraphicsUnit.Point, 178)
        self._textBox_ThiessenP.Location = Point(420, 25)
        self._textBox_ThiessenP.Name = "textBox_ThiessenP"
        self._textBox_ThiessenP.Size = Size(220, 21)
        self._textBox_ThiessenP.TabIndex = 13
        self._textBox_ThiessenP.TextChanged += self.Text_Change
        # 
        # label_ThiessenP
        # 
        self._label_ThiessenP.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                         GraphicsUnit.Point, 178)
        self._label_ThiessenP.ForeColor = Color.Black
        self._label_ThiessenP.Location = Point(350, 25)
        self._label_ThiessenP.Name = "label_ThiessenP"
        self._label_ThiessenP.Size = Size(70, 22)
        self._label_ThiessenP.TabIndex = 12
        self._label_ThiessenP.Text = "Thiessen P"
        # 
        # textBox_Isochron
        # 
        self._textBox_Isochron.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                          GraphicsUnit.Point, 178)
        self._textBox_Isochron.Location = Point(420, 82)
        self._textBox_Isochron.Name = "textBox_Isochron"
        self._textBox_Isochron.Size = Size(220, 21)
        self._textBox_Isochron.TabIndex = 22
        self._textBox_Isochron.TextChanged += self.Text_Change
        # 
        # label_Isochron
        # 
        self._label_Isochron.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                        GraphicsUnit.Point, 178)
        self._label_Isochron.ForeColor = Color.Black
        self._label_Isochron.Location = Point(350, 82)
        self._label_Isochron.Name = "label_Isochron"
        self._label_Isochron.Size = Size(70, 22)
        self._label_Isochron.TabIndex = 21
        self._label_Isochron.Text = "IsoChron"
        # 
        # button_ThiessenT
        #
        self._button_ThiessenT.Image = Image.FromFile("icons\\file.png")
        self._button_ThiessenT.Location = Point(644, 54)
        self._button_ThiessenT.Name = "button_ThiessenT"
        self._button_ThiessenT.Size = Size(32, 23)
        self._button_ThiessenT.TabIndex = 20
        self._button_ThiessenT.UseVisualStyleBackColor = True
        self._button_ThiessenT.Click += self.Button_ThiessenTClick
        # 
        # textBox_ThiessenT
        # 
        self._textBox_ThiessenT.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                           GraphicsUnit.Point, 178)
        self._textBox_ThiessenT.Location = Point(420, 54)
        self._textBox_ThiessenT.Name = "textBox_ThiessenT"
        self._textBox_ThiessenT.Size = Size(220, 21)
        self._textBox_ThiessenT.TabIndex = 19
        self._textBox_ThiessenT.TextChanged += self.Text_Change
        # 
        # label_ThiessenT
        # 
        self._label_ThiessenT.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                         GraphicsUnit.Point, 178)
        self._label_ThiessenT.ForeColor = Color.Black
        self._label_ThiessenT.Location = Point(350, 54)
        self._label_ThiessenT.Name = "label_ThiessenT"
        self._label_ThiessenT.Size = Size(70, 22)
        self._label_ThiessenT.TabIndex = 18
        self._label_ThiessenT.Text = "Thiessen T"
        # 
        # button_Isochron
        #
        self._button_Isochron.Image = Image.FromFile("icons\\file.png")
        self._button_Isochron.Location = Point(644, 82)
        self._button_Isochron.Name = "button_Isochron"
        self._button_Isochron.Size = Size(32, 23)
        self._button_Isochron.TabIndex = 23
        self._button_Isochron.UseVisualStyleBackColor = True
        self._button_Isochron.Click += self.Button_IsochronClick
        # 
        # groupBox_InputTimeseries
        # 
        self._groupBox_InputTimeseries.Controls.Add(self._button__ObservedRunoff)
        self._groupBox_InputTimeseries.Controls.Add(self._textBox__ObservedRunoff)
        self._groupBox_InputTimeseries.Controls.Add(self._label_ObservedRunoff)
        self._groupBox_InputTimeseries.Controls.Add(self._button_MinTemp)
        self._groupBox_InputTimeseries.Controls.Add(self._textBox_MinTemp)
        self._groupBox_InputTimeseries.Controls.Add(self._label_MinTemp)
        self._groupBox_InputTimeseries.Controls.Add(self._button_MaxTemp)
        self._groupBox_InputTimeseries.Controls.Add(self._textBox_MaxTemp)
        self._groupBox_InputTimeseries.Controls.Add(self._label_MaxTemp)
        self._groupBox_InputTimeseries.Controls.Add(self._button_Precipitation)
        self._groupBox_InputTimeseries.Controls.Add(self._textBox_Precipitation)
        self._groupBox_InputTimeseries.Controls.Add(self._label_Precipitation)
        self._groupBox_InputTimeseries.Location = Point(6, 162)
        self._groupBox_InputTimeseries.Name = "groupBox_InputTimeseries"
        self._groupBox_InputTimeseries.Size = Size(680, 95)
        self._groupBox_InputTimeseries.TabIndex = 4
        self._groupBox_InputTimeseries.TabStop = False
        self._groupBox_InputTimeseries.Text = "Input Time series"
        # 
        # label_Precipitation
        # 
        self._label_Precipitation.Font = Font("Microsoft Sans Serif", 9,
                                                             FontStyle.Regular,
                                                             GraphicsUnit.Point, 178)
        self._label_Precipitation.ForeColor = Color.Black
        self._label_Precipitation.Location = Point(1, 30)
        self._label_Precipitation.Name = "label_Precipitation"
        self._label_Precipitation.Size = Size(80, 22)
        self._label_Precipitation.TabIndex = 12
        self._label_Precipitation.Text = "Precipitation"
        # 
        # textBox_Precipitation
        # 
        self._textBox_Precipitation.Font = Font("Microsoft Sans Serif", 9,
                                                               FontStyle.Regular,
                                                               GraphicsUnit.Point, 178)
        self._textBox_Precipitation.Location = Point(102, 30)
        self._textBox_Precipitation.Name = "textBox_Precipitation"
        self._textBox_Precipitation.Size = Size(203, 21)
        self._textBox_Precipitation.TabIndex = 13
        self._textBox_Precipitation.TextChanged += self.Text_Change
        # 
        # button_Precipitation
        #
        self._button_Precipitation.Image = Image.FromFile("icons\\file.png")
        self._button_Precipitation.Location = Point(310, 30)
        self._button_Precipitation.Name = "button_Precipitation"
        self._button_Precipitation.Size = Size(32, 23)
        self._button_Precipitation.TabIndex = 14
        self._button_Precipitation.UseVisualStyleBackColor = True
        self._button_Precipitation.Click += self.Button_PrecipitationClick
        # 
        # label_MaxTemp
        # 
        self._label_MaxTemp.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                       GraphicsUnit.Point, 178)
        self._label_MaxTemp.ForeColor = Color.Black
        self._label_MaxTemp.Location = Point(350, 30)
        self._label_MaxTemp.Name = "label_MaxTemp"
        self._label_MaxTemp.Size = Size(107, 22)
        self._label_MaxTemp.TabIndex = 15
        self._label_MaxTemp.Text = "Max Temperature"
        # 
        # textBox_MaxTemp
        # 
        self._textBox_MaxTemp.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                         GraphicsUnit.Point, 178)
        self._textBox_MaxTemp.Location = Point(454, 30)
        self._textBox_MaxTemp.Name = "textBox_MaxTemp"
        self._textBox_MaxTemp.Size = Size(186, 21)
        self._textBox_MaxTemp.TabIndex = 16
        self._textBox_MaxTemp.TextChanged += self.Text_Change
        # 
        # button_MaxTemp
        #
        self._button_MaxTemp.Image = Image.FromFile("icons\\file.png")
        self._button_MaxTemp.Location = Point(644, 30)
        self._button_MaxTemp.Name = "button_MaxTemp"
        self._button_MaxTemp.Size = Size(32, 23)
        self._button_MaxTemp.TabIndex = 17
        self._button_MaxTemp.UseVisualStyleBackColor = True
        self._button_MaxTemp.Click += self.Button_MaxTempClick
        # 
        # label_MinTemp
        # 
        self._label_MinTemp.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                       GraphicsUnit.Point, 178)
        self._label_MinTemp.ForeColor = Color.Black
        self._label_MinTemp.Location = Point(350, 60)
        self._label_MinTemp.Name = "label_MinTemp"
        self._label_MinTemp.Size = Size(104, 20)
        self._label_MinTemp.TabIndex = 18
        self._label_MinTemp.Text = "Min Temperature"
        # 
        # textBox_MinTemp
        # 
        self._textBox_MinTemp.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular,
                                                         GraphicsUnit.Point, 178)
        self._textBox_MinTemp.Location = Point(454, 60)
        self._textBox_MinTemp.Name = "textBox_MinTemp"
        self._textBox_MinTemp.Size = Size(186, 21)
        self._textBox_MinTemp.TabIndex = 19
        self._textBox_MinTemp.TextChanged += self.Text_Change
        # 
        # button_MinTemp
        #
        self._button_MinTemp.Image = Image.FromFile("icons\\file.png")
        self._button_MinTemp.Location = Point(644, 60)
        self._button_MinTemp.Name = "button_MinTemp"
        self._button_MinTemp.Size = Size(32, 23)
        self._button_MinTemp.TabIndex = 20
        self._button_MinTemp.UseVisualStyleBackColor = True
        self._button_MinTemp.Click += self.Button_MinTempClick
        # 
        # label_ObservedRunoff
        # 
        self._label_ObservedRunoff.Font = Font("Microsoft Sans Serif", 9,
                                                              FontStyle.Regular,
                                                              GraphicsUnit.Point, 178)
        self._label_ObservedRunoff.ForeColor = Color.Black
        self._label_ObservedRunoff.Location = Point(1, 60)
        self._label_ObservedRunoff.Name = "label_ObservedRunoff"
        self._label_ObservedRunoff.Size = Size(104, 21)
        self._label_ObservedRunoff.TabIndex = 21
        self._label_ObservedRunoff.Text = "Observed Runoff"
        # 
        # textBox__ObservedRunoff
        # 
        self._textBox__ObservedRunoff.Font = Font("Microsoft Sans Serif", 9,
                                                                 FontStyle.Regular,
                                                                 GraphicsUnit.Point, 178)
        self._textBox__ObservedRunoff.Location = Point(102, 60)
        self._textBox__ObservedRunoff.Name = "textBox__ObservedRunoff"
        self._textBox__ObservedRunoff.Size = Size(203, 21)
        self._textBox__ObservedRunoff.TabIndex = 22
        self._textBox__ObservedRunoff.TextChanged += self.Text_Change
        # 
        # button__ObservedRunoff
        #
        self._button__ObservedRunoff.Image = Image.FromFile("icons\\file.png")
        self._button__ObservedRunoff.Location = Point(310, 60)
        self._button__ObservedRunoff.Name = "button__ObservedRunoff"
        self._button__ObservedRunoff.Size = Size(32, 23)
        self._button__ObservedRunoff.TabIndex = 23
        self._button__ObservedRunoff.UseVisualStyleBackColor = True
        self._button__ObservedRunoff.Click += self.Button_ObservedRunoffClick
        # 
        # MainForm
        # 
        self.ClientSize = Size(704, 442)
        self.Controls.Add(self._tabControl_Input_Output)
        self.Name = "MainForm"
        self.Text = "GISHM"
        self._tabPage_About.ResumeLayout(False)
        self._tabPage_Display.ResumeLayout(False)
        self._tabPage_Parameters.ResumeLayout(False)
        self._tabPage_Inputs.ResumeLayout(False)
        self._groupBox_Input.ResumeLayout(False)
        self._groupBox_Input.PerformLayout()
        self._groupBox_InputMaps.ResumeLayout(False)
        self._groupBox_InputMaps.PerformLayout()
        self._groupBox_Simulationtimes.ResumeLayout(False)
        self._groupBox_Simulationtimes.PerformLayout()
        self._groupBox_Output.ResumeLayout(False)
        self._groupBox_Output.PerformLayout()
        self._tabControl_Input_Output.ResumeLayout(False)
        self._groupBox_Snowmelt.ResumeLayout(False)
        self._groupBox_Snowmelt.PerformLayout()
        self._groupBox_PET.ResumeLayout(False)
        self._groupBox_PET.PerformLayout()
        self._groupBox_AET.ResumeLayout(False)
        self._groupBox_AET.PerformLayout()
        self._groupBox_SurfaceRunoff.ResumeLayout(False)
        self._groupBox_SurfaceRunoff.PerformLayout()
        self._groupBox_Baseflow.ResumeLayout(False)
        self._groupBox_Baseflow.PerformLayout()
        self._groupBox_LAI.ResumeLayout(False)
        self._groupBox_LAI.PerformLayout()
        self._groupBox_CN.ResumeLayout(False)
        self._groupBox_CN.PerformLayout()
        self._groupBox_Hydrograph.ResumeLayout(False)
        self._groupBox_Evaluationcriteria.ResumeLayout(False)
        self._groupBox_Evaluationcriteria.PerformLayout()
        self._groupBox_InputTimeseries.ResumeLayout(False)
        self._groupBox_InputTimeseries.PerformLayout()
        self.ResumeLayout(False)

        self.MaximumSize = self.Size
        self.MinimumSize = self.Size
        self.SizeGripStyle = SizeGripStyle.Hide
        self.FormBorderStyle = FormBorderStyle.FixedDialog
        self.MaximizeBox=False

        self.Icon = Icon("icons\\logo2.ico")


Application.EnableVisualStyles()
form = Model()
Application.Run(form)


