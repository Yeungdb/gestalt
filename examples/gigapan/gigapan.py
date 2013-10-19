# Forked from DFUnitVM Oct 2013

#------IMPORTS-------
from gestalt import nodes
from gestalt import interfaces
from gestalt import machines
from gestalt import functions
from gestalt.machines import elements
from gestalt.machines import kinematics
from gestalt.machines import state
from gestalt.utilities import notice
from gestalt.publish import rpc	#remote procedure call dispatcher
import time
import cv2.cv as cv
import sys

#------VIRTUAL MACHINE------
class virtualMachine(machines.virtualMachine):

        def __init__(self,camnum):
                self.camnum = camnum
                cv.NamedWindow("camera", 1)
                self.capture = cv.CaptureFromCAM(self.camnum)
                self.PORT = '/dev/ttyUSB0'
                self.HEXFILE = '../../../086-005/086-005a.hex'
                # tune this depending on how many frames are captured during the move
                self.NUMCAMERAREADS = 15
                
                # TODO check and store undistortion info
                self.undistortinfo = False

	def initInterfaces(self):
		if self.providedInterface: self.fabnet = self.providedInterface		#providedInterface is defined in the virtualMachine class.
		else: self.fabnet = interfaces.gestaltInterface('FABNET', interfaces.serialInterface(baudRate = 115200, interfaceType = 'ftdi', portName = self.PORT))
		
	def initControllers(self):
		self.xAxisNode = nodes.networkedGestaltNode('X Axis', self.fabnet, filename = '086-005a.py', persistence = self.persistence)
		self.yAxisNode = nodes.networkedGestaltNode('Y Axis', self.fabnet, filename = '086-005a.py', persistence = self.persistence)
		self.zAxisNode = nodes.networkedGestaltNode('Z Axis', self.fabnet, filename = '086-005a.py', persistence = self.persistence)
		self.xyzNode = nodes.compoundNode(self.xAxisNode, self.yAxisNode, self.zAxisNode)

	def initCoordinates(self):
		self.position = state.coordinate(['mm','mm','mm'])	#X,Y,Z
	
	def initKinematics(self):
		self.xAxis = elements.elementChain.forward([elements.microstep.forward(4), elements.stepper.forward(1.8), elements.leadscrew.forward(2), elements.invert.forward(True)])
		self.yAxis = elements.elementChain.forward([elements.microstep.forward(4), elements.stepper.forward(1.8), elements.leadscrew.forward(2), elements.invert.forward(True)])
		self.zAxis = elements.elementChain.forward([elements.microstep.forward(4), elements.stepper.forward(1.8), elements.leadscrew.forward(2), elements.invert.forward(False)])

		self.stageKinematics = kinematics.direct(3)	#direct drive on all three axes
	
	def initFunctions(self):
		self.move = functions.move(virtualMachine = self, virtualNode = self.xyzNode, axes = [self.xAxis, self.yAxis, self.zAxis], kinematics = self.stageKinematics, machinePosition = self.position,planner = 'null')
		self.jog = functions.jog(self.move)	#an incremental wrapper for the move function
		pass
		
	def initLast(self):
#		self.machineControl.setMotorCurrents(aCurrent = 0.8, bCurrent = 0.8, cCurrent = 0.8)
#		self.xyzNode.setVelocityRequest(0)	#clear velocity on nodes. Eventually this will be put in the motion planner on initialization to match state.
		pass
	
	def publish(self):
#		self.publisher.addNodes(self.machineControl)
		pass
	
	def getPosition(self):
		return {'position':self.position.future()}
                
	def setPosition(self, position  = [None, None, None]):
		self.position.future.set(position)
        
        def setLightIntensity(self):
                pass

	def autofocus(self):
		pass

        def captureUndistortMap():
                pass

        def initUndistort()
                #load camera intrinsic params
                #get optimal camera matrix (cv2 equiv)
                #init undistorm rectify map (cv2 equiv)
                #store it
                pass

        def correctImage(self,img):
                if(not undistortmap):
                        #capture undistort map
                        #init undistort map
                        undistortmap = True
                #remap image
                return img

	def takePhoto(self):
       		for i in range(NUMCAMERAREADS):
                        img = cv.QueryFrame(self.capture)
                return correctImg(img)

	def takeGigapan(self):
                #move to each location and take image
                #nadya did this already?
		pass

        def stitchGigapan(self,gigastack):
                #rectify/correct all images
                #create large canvas
                #place all images in canvas
                #blending?
                pass

        def bar(self):
		gigapan_status = self.xAxisNode.spinStatusRequest()
		while gigapan_status['stepsRemaining'] > 0:
			time.sleep(0.1)
			gigapan_status = self.xAxisNode.spinStatusRequest()
			# don't stall the UI while waiting
    			if cv.WaitKey(10) == 27:
        			break
        
        def barMove(self,pos):
                curr = self.getPosition()
                #this is stupid but I can't remember map syntax w/o google
                a = curr['position']
                for i in range(len(pos)):
                        pos[i]+=a[i]
                barMoveAbs(pos)

        def barMoveAbs(self,pos):
                setPosition(pos)
                bar()

        def takeFocalStack(self,rangetop,rangebottom,nstack):
                r = rangetop-rangebottom
                step = r/nstack
                focalstack = []
                self.barMove((0,0,-r/2));
                for pos in range(1,nstack):
                        self.barMove([0,0,step])
                        focalstack.append(self.takePhoto())
                return focalstack


#------IF RUN DIRECTLY FROM TERMINAL------
if __name__ == '__main__':
	gigapan = virtualMachine(persistenceFile = "test.vmp", camnum = 2)
#	gigapan.xyzNode.setMotorCurrent(1.1)
#	gigapan.xyzNode.loadProgram(HEXFILE)
	gigapan.xyzNode.setVelocityRequest(2)
	gigapan.xyzNode.setMotorCurrent(1)
	fileReader = rpc.fileRPCDispatch()
	fileReader.addFunctions(('move',gigapan.move), ('jog', gigapan.jog))	#expose these functions on the file reader interface.


	# remote procedure call initialization
	#rpcDispatch = rpc.httpRPCDispatch(address = '0.0.0.0', port = 27272)
	#notice(gigapan, 'Started remote procedure call dispatcher on ' + str(rpcDispatch.address) + ', port ' + str(rpcDispatch.port))
	#rpcDispatch.addFunctions(('move',gigapan.move),
	#			('position', gigapan.getPosition),
	#			('jog', gigapan.jog),
	#			('disableMotors', gigapan.xyzNode.disableMotorsRequest),
	#			('loadFile', fileReader.loadFromURL),
	#			('runFile', fileReader.runFile),
	#			('setPosition', gigapan.setPosition))	#expose these functions on an http interface
	#rpcDispatch.addOrigins('http://tq.mit.edu', 'http://127.0.0.1:8000')	#allow scripts from these sites to access the RPC interface
	#rpcDispatch.allowAllOrigins()
	#rpcDispatch.start()

	while True:
                img = gigapan.getCurrentFrame()
    		cv.ShowImage("camera", img)
		gigapan.barMove([-1.2,0,0])

    		if cv.WaitKey(10) == 27:
        		break
