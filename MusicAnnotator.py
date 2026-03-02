import sys
import numpy as np
import sounddevice as sd
import librosa
from PyQt6.QtGui import QPainter, QPen, QBrush
from PyQt6.QtCore import QRectF, Qt, QPointF, QTimer, QUrl
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QWidget, QPushButton,QSlider, QVBoxLayout,QMainWindow,QLabel
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QSoundEffect


class Staff(QGraphicsItem):
    def boundingRect(self):
        return QRectF(0, 0, 800, 100)

    def paint(self, painter, option, widget):
        pen = QPen(Qt.GlobalColor.black)
        painter.setPen(pen)

        # Draw 5 staff lines
        for i in range(5):
            y = 20 + i * 14
            painter.drawLine(0, y, 800, y)

class Note(QGraphicsItem):
    allNotes=[]
    noteArr=['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab','A', 'Bb','B']
    effectArr=[]


    for i in range(7):
            noteEffect=[]
            for note in range(12):
                effect = QSoundEffect()
                effect.setSource(QUrl.fromLocalFile(f"notes/{noteArr[note]}{i+1}.wav"))
                effect.setVolume(0.6)
                noteEffect.append(effect)
            effectArr.append(noteEffect)

    def changeLabel(self,val):
        self.noteLabel.setText(f"Note length is {val}")

    def __init__(self, x, y,label):

        super().__init__()
        self.note='C'
        self.index=0
        self.octave=4
        self.prevY=35
        self.prevOct=0
        self.prevInd=0
        self.noteLabel=label
        self.color=Qt.GlobalColor.black
        self.posToIndexDict = {
                                0: 0,
                                7: 1,
                                14: 3,
                                21: 4,
                                28: 6,
                                35: 8,
                                42: 10,
                            }
        self.indexToPos = {
            1:2
        }
        self.shiftHeld=False
        self.setPos(x, y)
        self.rect = QRectF(0, 0, 12, 14)
        
        self.dura=120
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        Note.allNotes.append(self)
        self.changeLabel(self.rect.width())
        
    def mousePressEvent(self, event):
        # Store where inside the item we clicked
        self.drag_offset = event.pos()
        
        super().mousePressEvent(event)
    def setDura(self,val):
        self.dura=val
        print("Duration stored ",val)
        self.changeLabel(val/10)
        self.prepareGeometryChange()
        self.rect.setWidth(int(self.dura/10))

    def focusInEvent(self, event):
        self.playSound(self.octave,self.index)
        self.changeLabel(self.dura)
        
    def mouseMoveEvent(self, event):
        # Move item so click point stays under cursor
        if (not self.shiftHeld): # indicates i am moving the note
            new_pos = event.scenePos() - self.drag_offset

            flag = True
            # check if moving would overlap me
            ourNoteXL = new_pos.x()
            ourNoteXR = ourNoteXL+self.rect.width()
            for note in Note.allNotes:
                if (note is self):
                    continue
                lBound = note.pos().x()
                rBound = note.pos().x()+note.rect.width()
                if (ourNoteXR>=lBound and ourNoteXL<=rBound):
                    flag = False
                    rBoundDist = abs(ourNoteXL-rBound)
                    lBoundDist = abs(ourNoteXR-lBound)
                    yval=self.pos().y()
                    if (rBoundDist>lBoundDist):

                        self.setPos(QPointF(lBound-self.rect.width(),yval))
         
                    else:
       
                        self.setPos(QPointF(rBound,yval))
                       
                    break

            if (flag):
               self.setPos(QPointF(new_pos.x(),self.pos().y()))

        else:
                flag = True
                ourNoteXL = self.pos().x()
                ourNoteXR = ourNoteXL+event.pos().x()
                for note in Note.allNotes:
                    if (note is self):
                        continue
                    lBound = note.pos().x()
                    rBound = note.pos().x()+note.rect.width()

                    if (ourNoteXR>lBound and ourNoteXL<rBound):
                        flag = False

                        break

                if (flag):
                    


                    self.prepareGeometryChange()
                    dist = event.pos().x() 
                    
                    if (dist>1):
                        self.rect.setWidth(dist)
                        self.dura=self.rect.width()*10
                        self.changeLabel(self.dura)

 
    def playSound(self,oct,ind):
        Note.effectArr[self.prevOct][self.prevInd].stop()
        print(f"Playing {Note.noteArr[ind]}{oct}")
        Note.effectArr[oct][ind].play()

    def keyPressEvent(self, event):
        if (event.key()==Qt.Key.Key_Shift):
            self.shiftHeld=True
        if (event.key()==Qt.Key.Key_Up): 
            self.prevInd=self.index
            if (self.index==11):
                self.octave+=1
                self.index=0
            else:
                self.index+=1


            if (len(Note.noteArr[self.index])==2):

                self.color=(Qt.GlobalColor.darkCyan)
                self.update()
            else:
                self.color=(Qt.GlobalColor.black)
                self.update()

            if (Note.noteArr[self.prevInd][0]!=Note.noteArr[self.index][0]):
                self.setPos(QPointF(self.pos().x(),self.pos().y()-7))


            self.playSound(self.octave,self.index)
        if (event.key() in (Qt.Key.Key_E,Qt.Key.Key_Q)):
            self.clearFocus()
        if (event.key()==Qt.Key.Key_Down):
            self.prevInd=self.index
            if (self.index==0):
                self.octave-=1
                self.index=11
            else:
                self.index-=1

            if (len(Note.noteArr[self.index])==2):

                self.color=(Qt.GlobalColor.darkCyan)

            else:
                self.color=(Qt.GlobalColor.black)

            if (Note.noteArr[self.prevInd][0]!=Note.noteArr[self.index][0]):
                self.setPos(QPointF(self.pos().x(),self.pos().y()+7))

            self.update()
        
            self.playSound(self.octave,self.index)

    def keyReleaseEvent(self, event):
        if (event.key()==Qt.Key.Key_Shift):
            self.shiftHeld=False
       

    def boundingRect(self):
        return self.rect.adjusted(-1, -1, 1, 1)

    def paint(self, painter, option, widget):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(self.color))
        painter.drawRect(self.rect)


class MainWindow(QMainWindow):
    potentialBPMSet=dict()

    def __init__(self):
        super().__init__()
        self.noteArr=['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab','A', 'Bb','B']
        self.savedDur=0
        self.lyco = QMediaPlayer()
        self.audio_output=QAudioOutput()
        self.lyco.setAudioOutput(self.audio_output)
        self.lyco.setSource(QUrl.fromLocalFile("songfile.wav"))
        self.lyco.durationChanged.connect(self.update_duration)
        self.stopPos=0

        self.speedSlider = QSlider(Qt.Orientation.Horizontal,self) 
        self.speedSlider.setRange(0,10)
        self.speedSlider.valueChanged.connect(self.updPlayback)

        self.songSlider = QSlider(Qt.Orientation.Horizontal,self) 
        self.songSlider.setRange(0, self.lyco.duration())
        self.songSlider.valueChanged.connect(self.updPos)

        self.durationLabel = QLabel()
        self.durationLabel.setText("Current duration of 0")

        self.noteLength = QLabel()

        self.saveButton = QPushButton("Change song starting position")
        self.saveButton.clicked.connect(self.saveProgress)

        self.duraButton = QPushButton("Update duration")
        self.duraButton.clicked.connect(self.preciseVal)    

        test,sr1 = librosa.load(f"song.wav")

        self.test=test
        self.sr1=sr1
        self.playRate=1
        
        self.scene = QGraphicsScene()
        shipping = QWidget()
        layedOut = QVBoxLayout()

        staff = Staff()
        
        self.scene.addItem(staff)

        note = Note(100, 35,self.noteLength)

        self.scene.addItem(note)

        view = QGraphicsView(self.scene)

        view.setRenderHints(QPainter.RenderHint.Antialiasing)
        view.resize(900, 300)
        self.currNote=note

        self.addNote = QPushButton("Add Note")
        self.playSong = QPushButton("Play Song")
        self.checkNote = QPushButton("Check Notes")
        self.checkNoteSong = QPushButton("Check Notes (no song)")
        self.addNote.clicked.connect(self.addNotes)
        self.checkNote.clicked.connect(self.checkNotes)
        self.playSong.clicked.connect(self.playSongs)
        self.checkNoteSong.clicked.connect(self.checkNoSong)

        layedOut.addWidget(view)
        self.setCentralWidget(shipping)
        shipping.setLayout(layedOut)

        layedOut.addWidget(self.addNote)
        layedOut.addWidget(self.noteLength)
        layedOut.addWidget(self.songSlider)
        layedOut.addWidget(self.speedSlider)
        layedOut.addWidget(self.playSong)
        layedOut.addWidget(self.saveButton)
        layedOut.addWidget(self.duraButton)
        layedOut.addWidget(self.durationLabel)
        layedOut.addWidget(self.checkNote)
        layedOut.addWidget(self.checkNoteSong)
        
    
    def keyPressEvent(self, event):
        if (event.key()==Qt.Key.Key_E):
            self.songSlider.setValue(self.songSlider.value()+1)
        if (event.key()==Qt.Key.Key_Q):
            self.songSlider.setValue(self.songSlider.value()-1)
        
        
    def addNotes(self):
        maxEnd=0
        for note in Note.allNotes:
            maxEnd=max(maxEnd,note.pos().x()+note.rect.width())
        note = Note(maxEnd+5, 35,self.noteLength)
        self.currNote=note
        self.scene.addItem(note)

    def playSongs(self):
        startPos=int(self.savedDur*self.sr1/1000)
        endPos = int(self.stopPos*self.sr1/1000)
        result=self.test[startPos:endPos]
        print(startPos,endPos,len(result),len(self.test))
        y_slow = librosa.effects.time_stretch(result, rate=self.playRate)
        sd.play(y_slow,self.sr1)
        

    def preciseVal(self): 
        # Attempted method of determining the BPM of a song through looking at all possible multiples of a note (quarter notes, half notes, half+quarter, etc) to see the amount of times it occurs
        # over a given amount of notes. It has proven successful only in a few cases.

        self.currNote.setDura(self.stopPos-self.savedDur)
        setDuration=(self.stopPos-self.savedDur)/1000
        baseBPM = 60/setDuration
        possNote=[0.125,0.25,0.375,0.5,0.625,0.75,0.825,1,1.125,1.25,1.375,1.5,1.625,1.75,1.875,2]
        for poss in possNote:
            newBase = baseBPM*poss
            for i in range(-5,6):
                t = int(newBase+i)
                if (t<200):
                
                    MainWindow.potentialBPMSet[t]=MainWindow.potentialBPMSet.get(t,0)+1
        print(MainWindow.potentialBPMSet)


    def playNote(self,ind=0,prevOct=0,prevInd=0):
        
        if (ind==len(self.boundArr)):
            return
        Note.effectArr[prevOct][prevInd].stop()
        note = self.boundArr[ind]
        duration = note[1]
        oct = note[2]
        index = note[3]
        Note.effectArr[oct][index].play()
        QTimer.singleShot(int(duration),Qt.TimerType.PreciseTimer,lambda: self.playNote(ind+1,oct,index))
    def saveProgress(self):
        self.savedDur=self.stopPos
        self.durationLabel.setText(f"Current duration of {0}")

    def update_duration(self, duration):
        self.songSlider.setRange(0, duration)
        print(duration)


    def checkNotes(self): # Plays the notes
            self.boundArr=[]
            for el in Note.allNotes:
                self.boundArr.append((el.pos().x(),el.dura,el.octave,el.index))
            self.boundArr.sort()
            print(self.boundArr)
         
            test,sr1 = librosa.load(f"song.wav")

            result = test
            sampCount=0
            for bounded in self.boundArr:
                note_audio, sr = librosa.load(f"notes/{self.noteArr[bounded[3]]}{bounded[2]}.wav")
                miliDuration = bounded[1]
                samples = int(sr*miliDuration/1000)
                print(sr1,sr)
                result[sampCount:sampCount+samples]+=note_audio[:samples]
                sampCount+=samples
            sd.play(result,self.sr1)


    def checkNoSong(self): # Plays the notes
            self.boundArr=[]
            for el in Note.allNotes:
                self.boundArr.append((el.pos().x(),el.dura,el.octave,el.index))
            self.boundArr.sort()
            print(self.boundArr)
            
            test,sr1 = librosa.load(f"song.wav")

            result = np.zeros(len(test))
            sampCount=0
            for bounded in self.boundArr:
                note_audio, sr = librosa.load(f"notes/{self.noteArr[bounded[3]]}{bounded[2]}.wav")
                miliDuration = bounded[1]
                samples = int(sr*miliDuration/1000)
                print(sr1,sr)
                result[sampCount:sampCount+samples]+=note_audio[:samples]
                sampCount+=samples
            sd.play(result,self.sr1)


    def updPos(self,pos):
        self.stopPos=pos
        self.durationLabel.setText(f"Current duration of {pos-self.savedDur}")


    def updPlayback(self,pos):
        self.playRate=pos/10
app = QApplication(sys.argv)


win = MainWindow()
win.show()
sys.exit(app.exec())
