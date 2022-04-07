
#encoding=utf-8
import os,time

import piexif
from PIL.Image import open as imgOpen
from multiprocessing import Pool
from multiprocessing import Manager

from tkinter import *
import tkinter
import tkinter.messagebox as messagebox
import tkinter.filedialog as dialog

class ImageCompress(Frame):
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.pack()
		self.createWidgets()

	def createWidgets(self):
		# Input labels
		Label(self, text="输入地址:", font=("微软雅黑", 12), width=8, height=1).grid(row=0)
		Label(self, text="输出地址:", font=("微软雅黑", 12), width=8, height=1).grid(row=1)
		Label(self, text="JPEG质量(1-95):", font=("微软雅黑", 12), width=12, height=1).grid(row=2)
		Label(self, text="进程数量:", font=("微软雅黑", 12), width=8, height=1).grid(row=3)
		# Label(self, text="处理进度:", font=("微软雅黑", 12), width=8, height=1).grid(row=4)
		# self.processedFiles = Label(self, text="0", font=("微软雅黑", 12), width=6, height=1)
		# self.processedFiles.grid(row=4,column=2)
		# Label(self, text="/", font=("微软雅黑", 12), width=1, height=1).grid(row=4,column=3)
		# self.totalFiles = Label(self, text="0", font=("微软雅黑", 12), width=6, height=1)
		# self.totalFiles.grid(row=4,column=4)
		self.keepExif = IntVar()
		self.keepExifCheckBox=Checkbutton(self,text="保留Exif",font=("微软雅黑", 12),variable=self.keepExif, onvalue =1,offvalue=0,height=1)
		self.keepExifCheckBox.grid(row=4)

		self.keepStruct = IntVar()
		self.keepStructCheckBox=Checkbutton(self,text="保持目录结构",font=("微软雅黑", 12),variable=self.keepStruct, onvalue =1,offvalue=0,height=1)
		self.keepStructCheckBox.grid(row=4,column=2)
		
		self.inDirInput = Entry(self,width=30)
		self.outDirInput = Entry(self,width=30)
		self.imgQualityInput = Entry(self,width=5)
		self.maxProcessesInput = Entry(self,width=5)

		self.inDirInput.grid(row=0,column=1,columnspan=3)
		self.outDirInput.grid(row=1,column=1,columnspan=3)
		self.imgQualityInput.grid(row=2,column=1)
		self.maxProcessesInput.grid(row=3,column=1)

		# Set default quality and processes
		self.imgQualityInput.insert(END,75)
		self.maxProcessesInput.insert(END,2)

		# Add buttons
		self.inButton = Button(self, text='选择', command=lambda: self.selectDir('input'))
		self.outButton = Button(self, text='选择', command=lambda: self.selectDir('output'))
		self.excuteButton = Button(self, text='输出', command=self.imageCompress)

		self.inButton.grid(row=0,column=5)
		self.outButton.grid(row=1,column=5)
		self.excuteButton.grid(row=2,column=5)

	def selectDir(self,section):
		if(section=='input'):
			self.inDirInput.delete(0,END)
			self.inDirInput.insert(END,dialog.askdirectory())

		if(section=='output'):
			self.outDirInput.delete(0,END)
			self.outDirInput.insert(END,dialog.askdirectory())

		pass

	# Use mapDir instead
	# def getFileList(self,inDir):
	# 	fileList = glob.glob(inDir+'/*.*')
	# 	fileNum = len(fileList)
	# 	# self.totalFiles['text']=str(fileNum)
	# 	return fileNum,fileList

	def makeDirs(self,outDir,dirList):
		for directory in dirList:
			try:
				os.makedirs(os.path.join(outDir,directory))
			except:
				pass
		pass

	def mapDir(self,inDir):
		dirNames=[]
		fileNames=[]
		for dName, dNames, fNames in os.walk(inDir):
			for subDirName in dNames:
				#print(os.path.join(dName, subdirname))
				dirNames.append(subDirName)
			for fileName in fNames:
				fileNames.append(os.path.join(dName,fileName))
		return dirNames,fileNames

	def imageCompress(self):
		inDir= self.inDirInput.get()
		outDir=self.outDirInput.get()

		# Detect dir input if null
		if (inDir=='' or outDir==''):
			messagebox.showerror(title='错误',message='输入或输出文件夹不能为空')
			return

		# Normalize input dir format
		inDir = inDir.replace('\\','/').rstrip('/')
		outDir = outDir.replace('\\','/').rstrip('/')

		# Get running time
		startTime=time.time()

		# Get files list
		dirList,fileList=self.mapDir(inDir)
		fileNum=len(fileList)
		print("Total: "+str(fileNum))

		# Prepare options
		imgQuality=int(self.imgQualityInput.get())
		keepExif=int(self.keepExif.get())
		keepStruct=int(self.keepStruct.get())

		# If need to keep directory structure
		if(keepStruct):
			self.makeDirs(outDir,dirList)

		# Multi process queue
		# print(1)
		manager=Manager()
		queue=manager.Queue()
		processedNum=manager.Value('i',0)
		for i in fileList:
			queue.put(i)
		processesNum = int(self.maxProcessesInput.get())
		pool = Pool(processesNum)
		# print(2)
		for i in range(processesNum):
			# print(2.01)
			pool.apply_async(compress,(outDir,imgQuality,keepExif,keepStruct,queue,processedNum))
			# print(2.02)
		# pool.map(self.compress,range(processesNum))
		pool.close()
		pool.join()
		# jobs = []
		# for i in range(processesNum):
		# 	p = Process(target=compress)
		# 	jobs.append(p)
		# 	p.start()
		# 	p.join()
		# print(3)

		# Get running time
		stopTime=time.time()
		totalTime=round(stopTime-startTime, 3)

		messagebox.showinfo(title='提示',message='处理完成'+str(fileNum)+'项，耗时'+str(totalTime)+'s')
		print('处理完成'+str(fileNum)+'项，耗时'+str(totalTime)+'s')
		pass

	def reloadNum():
		global processesNum
		self.processedFiles['text']=str(processesNum.value)

def compress(outDir,imgQuality,keepExif,keepStruct,queue,num):
	# print(2.1)
	while(not queue.empty()):
		try:
			# print(2.2)
			source = queue.get()
			im = imgOpen(source)
		except Exception as e:
			print(e)
			continue

		# print(2.3)
		fullFileName= source.split('\\')[-1]
		fileName=fullFileName.split('.')[0]

		# If need to keep the directory structure
		if(keepStruct):
			subDir='/'.join(source.split('\\')[1:-1])
			tempOutDir=outDir+'/'+subDir
			#print(source,subDir,outDir)

		# If not a jpeg file before
		if(not fullFileName.endswith('jpg')):
			im = im.convert('RGB')

		#print(outDir+'/'+fileName+'.jpg')

		# Keep exif information or not
		if(keepExif):
			exif_dict = piexif.load(im.info["exif"])
			exif_bytes = piexif.dump(exif_dict)
			im.save(tempOutDir+'/'+fileName+'.jpg','jpeg',quality=imgQuality,progressive=True,optimize=True,exif=exif_bytes)
		else:
			im.save(tempOutDir+'/'+fileName+'.jpg','jpeg',quality=imgQuality,progressive=True,optimize=True)

		num.value+=1
		print("Finished: "+str(num.value))
		# print(2.4)
		# reloadNum()
		# global app
		# app.reloadNum()
		#self.processedNum+=1
		#self.processedFiles['text']=str(self.processedNum)
	pass

def reloadNum():
	global app
	return app.reloadNum()

if __name__=="__main__":
	app = ImageCompress()
	app.master.title('图片处理')
	app.mainloop()