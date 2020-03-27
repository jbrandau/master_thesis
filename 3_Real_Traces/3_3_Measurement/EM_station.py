import serial
import msvcrt
import time

class EM_station:

# EM station setup and object handling

	def __init__(self,port='COM31',step_width=1000,analysis_steps_x=10,analysis_steps_y=10,analysis_steps_z=10):	
		self.port=port
		self.step_width=step_width
		self.analysis_steps_x=analysis_steps_x
		self.analysis_steps_y=analysis_steps_y
		self.analysis_steps_z=analysis_steps_z
		self.cur_analysis_step_x=0
		self.cur_analysis_step_y=0
		self.cur_analysis_step_z=0
		self.stored_pos_A=bool(False)
		self.stored_pos_B=bool(False)
		self.analysis_map_exist=bool(False)
		self.cur_pos=[0,0,0]
		self.pos_A=[0,0,0]
		self.pos_B=[0,0,0]
		self.connect();
		self.set_cur_pos(self.get_cur_probe_pos());
		self.toggle=bool(False)
		return;
   
	def __del__(self):
		self.disconnect();
		return;
   
	def connect(self):
		self.ser=serial.Serial(self.port)
		return;

	def get_connected_port(self):
		return self.port;
		
	def is_connected(self):
		return self.ser.isOpen();
	
	def disconnect(self):
		self.ser.close()
		return;

	def set_step_width(self,step_width):
		self.step_width=step_width;
		return;
		
	def get_step_width(self):
		return self.step_width;
		return;
		
	def set_analysis_steps_x(self,analysis_steps_x):
		self.analysis_steps_x=analysis_steps_x;
		return;
		
	def get_analysis_steps_x(self):
		return self.analysis_steps_x;
		return;
		
	def set_analysis_steps_y(self,analysis_steps_y):
		self.analysis_steps_y=analysis_steps_y;
		return;
		
	def get_analysis_steps_y(self):
		return self.analysis_steps_y;
		return;
	
	def set_analysis_steps_z(self,analysis_steps_z):
		self.analysis_steps_z=analysis_steps_z;
		return;
		
	def get_analysis_steps_z(self):
		return self.analysis_steps_z;
		return;

		
		
# EM station probe control
		
	def set_cur_pos(self,cur_pos):
		self.cur_pos=cur_pos;
		return;
	
	def get_cur_pos(self):
		return self.cur_pos;
	
	def set_pos_A(self,pos_A):
		self.pos_A=list(pos_A);
		self.stored_pos_A=bool(True);
		return;
	
	def get_pos_A(self):
		if self.stored_pos_A:
			return self.pos_A;
		else:
			print 'NO POSITION STORED IN A!'
			return self.get_cur_pos();
		
	def set_pos_B(self,pos_B):
		self.pos_B=list(pos_B);
		self.stored_pos_B=bool(True);
		return;
		
	def get_pos_B(self):
		if self.stored_pos_B:
			return self.pos_B;
		else:
			print 'NO POSITION STORED IN B!'
			return self.get_cur_pos();

	def int32(self,x):

	  if x>0xFFFFFFFF:
		raise OverflowError
	  if x>0x7FFFFFFF:
		x=int(0x100000000-x)
		if x<2147483648:
		  return -x
		else:
		  return -2147483648
	  return x		
		
	def get_cur_probe_pos(self):
		time.sleep(0.1)
		value_fb=[0,1,2,3]
		output=[0,0,0]
		for i in xrange(3):
			checksum=(1+i+32)%256
			msg=chr(1) + chr(32) + chr(0) + chr(i) + chr(0) + chr(0) + chr(0) + chr(0) + chr(checksum)
			self.ser.write(msg)
			host_fb=ord(self.ser.read())
			target_fb=ord(self.ser.read())
			status_fb=ord(self.ser.read())
			instruction_fb=ord(self.ser.read())
			value_fb[0]=ord(self.ser.read())
			value_fb[1]=ord(self.ser.read())
			value_fb[2]=ord(self.ser.read())
			value_fb[3]=ord(self.ser.read())
			checksum_fb=ord(self.ser.read())
			checksum=(1+i+31)%256
			msg=chr(1) + chr(31) + chr(0) + chr(i) + chr(0) + chr(0) + chr(0) + chr(0) + chr(checksum)
			self.ser.write(msg)
			host_fb=ord(self.ser.read())
			target_fb=ord(self.ser.read())
			status_fb=ord(self.ser.read())
			instruction_fb=ord(self.ser.read())
			value_fb[0]=ord(self.ser.read())
			value_fb[1]=ord(self.ser.read())
			value_fb[2]=ord(self.ser.read())
			value_fb[3]=ord(self.ser.read())
			checksum_fb=ord(self.ser.read())
			output[abs(i-2)]=self.int32(sum(value_fb[i] << (abs(i-3) * 8) for i in xrange(4)));
		return output	
		
	def move_probe_abs(self,motor, value): 
		device=1
		instruction=4
		type=0
		v_array = [(value>>(8*i))&0xff for i in range(3,-1,-1)]
		checksum=(device+instruction+type+motor+v_array[0]+v_array[1]+v_array[2]+v_array[3])%256
		msg=chr(device) + chr(instruction) + chr(type) + chr(motor) + chr(v_array[0]) + chr(v_array[1]) + chr(v_array[2]) + chr(v_array[3]) + chr(checksum)
		self.ser.write(msg)
		host_fb=ord(self.ser.read())
		target_fb=ord(self.ser.read())
		status_fb=ord(self.ser.read())
		instruction_fb=ord(self.ser.read())
		value_fb=[0,1,2,3]
		value_fb[0]=ord(self.ser.read())
		value_fb[1]=ord(self.ser.read())
		value_fb[2]=ord(self.ser.read())
		value_fb[3]=ord(self.ser.read())
		checksum_fb=ord(self.ser.read())
		return self.int32(sum(value_fb[i] << (abs(i-3) * 8) for i in xrange(4)));

				
	def move_2_pos_000(self):
		temp_pos=self.get_cur_pos()
		temp_pos[0]=self.move_probe_abs(0,0)
		temp_pos[1]=self.move_probe_abs(1,0)
		temp_pos[2]=self.move_probe_abs(2,0)
		self.set_cur_pos(temp_pos)
		while (self.is_moving()):
			pass
		print 'Probe is at position [0,0,0]'
			
	def move_2_pos(self,pos):
		temp_pos=self.get_cur_pos()
		temp_pos[2]=self.move_probe_abs(0,pos[2])
		temp_pos[1]=self.move_probe_abs(1,pos[1])
		temp_pos[0]=self.move_probe_abs(2,pos[0])
		self.set_cur_pos(temp_pos)
		while (self.is_moving()):
			pass
		print 'Probe arrived'
		return;
				
	def one_pos_step_x(self):
		temp_pos=self.get_cur_pos()
		temp_pos[0]=self.move_probe_abs(2,(temp_pos[0]+self.step_width))
		self.set_cur_pos(temp_pos)
		return;
		
	def one_neg_step_x(self):
		temp_pos=self.get_cur_pos()
		temp_pos[0]=self.move_probe_abs(2,(temp_pos[0]-self.step_width))
		self.set_cur_pos(temp_pos)
		return;
	
	def one_pos_step_y(self):
		temp_pos=self.get_cur_pos()
		temp_pos[1]=self.move_probe_abs(1,(temp_pos[1]+self.step_width))
		self.set_cur_pos(temp_pos)
		return;
	
	def one_neg_step_y(self):
		temp_pos=self.get_cur_pos()
		temp_pos[1]=self.move_probe_abs(1,(temp_pos[1]-self.step_width))
		self.set_cur_pos(temp_pos)	
		return;
		
	def one_pos_step_z(self):
		temp_pos=self.get_cur_pos()
		temp_pos[2]=self.move_probe_abs(0,(temp_pos[2]+self.step_width))
		self.set_cur_pos(temp_pos)
		return;
	
	def one_neg_step_z(self):
		temp_pos=self.get_cur_pos()
		temp_pos[2]=self.move_probe_abs(0,(temp_pos[2]-self.step_width))
		self.set_cur_pos(temp_pos)
		return;
		
	def is_moving(self):
		if(self.get_cur_pos()!=self.get_cur_probe_pos()):
			return bool(True);
		else:
			return bool(False);
			
	def stop_motor(self):
		msg=chr(1) + chr(3) + chr(0) + chr(0) + chr(0) + chr(0) + chr(0) + chr(0) + chr(4)
		self.ser.write(msg)
		return;

		
		
# Analysis map generation handling
		
	def gen_analysis_map(self):
		self.toggle=False
		self.cur_analysis_step_x=0
		self.cur_analysis_step_y=0
		self.cur_analysis_step_z=0
		pos_A_x=self.get_pos_A()[0]
		pos_A_y=self.get_pos_A()[1]
		pos_A_z=self.get_pos_A()[2]
		pos_B_x=self.get_pos_B()[0]
		pos_B_y=self.get_pos_B()[1]
		pos_B_z=self.get_pos_B()[2]
		steps_x=self.get_analysis_steps_x()
		steps_y=self.get_analysis_steps_y()
		steps_z=self.get_analysis_steps_z()
		#mapping of X
		if (pos_A_x-pos_B_x)==0:
			self.analysis_map_x=[pos_A_x]
		else:
			if pos_A_x > pos_B_x:
				interval_x=(pos_A_x - pos_B_x)/(steps_x-1)
				self.analysis_map_x=range(pos_A_x,pos_B_x,-interval_x)
				self.analysis_map_x.append(pos_B_x)
			else:
				interval_x=(pos_B_x - pos_A_x)/(steps_x-1)
				self.analysis_map_x=range(pos_A_x,pos_B_x,interval_x)
				self.analysis_map_x.append(pos_B_x)
		#mapping of Y
		if (pos_A_y-pos_B_y)==0:
			self.analysis_map_y=[pos_A_y]
		else:
			if pos_A_y > pos_B_y:
				interval_y=(pos_A_y - pos_B_y)/(steps_y-1)
				self.analysis_map_y=range(pos_A_y,pos_B_y,-interval_y)
				self.analysis_map_y.append(pos_B_y)
			else:
				interval_y=(pos_B_y - pos_A_y)/(steps_y-1)
				self.analysis_map_y=range(pos_A_y,pos_B_y,interval_y)
				self.analysis_map_y.append(pos_B_y)
		#mapping of Z
		if (pos_A_z-pos_B_z)==0:
			self.analysis_map_z=[pos_A_z]
		else:
			if pos_A_z > pos_B_z:
				interval_z=(pos_A_z - pos_B_z)/(steps_z-1)
				self.analysis_map_z=range(pos_A_z,pos_B_z,-interval_z)
				self.analysis_map_z.append(pos_B_z)
			else:
				interval_z=(pos_B_z - pos_A_z)/(steps_z-1)
				self.analysis_map_z=range(pos_A_z,pos_B_z,interval_z)
				self.analysis_map_z.append(pos_B_z)
		return;
				
	def get_analysis_map_x(self):
		return self.analysis_map_x;

	def get_analysis_map_y(self):
		return self.analysis_map_y;
		
	def get_analysis_map_z(self):
		return self.analysis_map_z;
		
	def get_cur_analysis_map_element(self):
		return [self.get_analysis_map_x()[self.cur_analysis_step_x],self.get_analysis_map_y()[self.cur_analysis_step_y],self.get_analysis_map_z()[self.cur_analysis_step_z]];
	
	def next_analysis_map_element_x(self):
		max_steps_x=len(self.get_analysis_map_x())-1
		if self.cur_analysis_step_x==max_steps_x:
			self.cur_analysis_step_x=0
		else:
			self.cur_analysis_step_x=self.cur_analysis_step_x+1
			return;
	
	def next_analysis_map_element_y(self):
		max_steps_y=len(self.get_analysis_map_y())-1
		if self.cur_analysis_step_y==max_steps_y:
			self.cur_analysis_step_y=0
		else:
			self.cur_analysis_step_y=self.cur_analysis_step_y+1
			return;
	
	def next_analysis_map_element_z(self):
		max_steps_z=len(self.get_analysis_map_z())-1
		if self.cur_analysis_step_z==max_steps_z:
			self.cur_analysis_step_z=0
		else:
			self.cur_analysis_step_z=self.cur_analysis_step_z+1
			return;
	
	def prev_analysis_map_element_x(self):
		max_steps_x=len(self.get_analysis_map_x())-1
		if self.cur_analysis_step_x==0:
			self.cur_analysis_step_x=max_steps_x
		else:
			self.cur_analysis_step_x=self.cur_analysis_step_x-1
			return;
			
	def prev_analysis_map_element_y(self):
		max_steps_y=len(self.get_analysis_map_y())-1
		if self.cur_analysis_step_y==0:
			self.cur_analysis_step_y=max_steps_y
		else:
			self.cur_analysis_step_y=self.cur_analysis_step_y-1
			return;
			
	def prev_analysis_map_element_z(self):
		max_steps_z=len(self.get_analysis_map_z())-1
		if self.cur_analysis_step_z==0:
			self.cur_analysis_step_z=max_steps_z
		else:
			self.cur_analysis_step_z=self.cur_analysis_step_z-1
			return;
	
	def is_last_analysis_map_element_x(self):
		if self.cur_analysis_step_x==len(self.get_analysis_map_x())-1:
			return bool(True);
		else:
			return bool(False);
			
	def is_last_analysis_map_element_y(self):
		if self.cur_analysis_step_y==len(self.get_analysis_map_y())-1:
			return bool(True);
		else:
			return bool(False);
	
	def is_last_analysis_map_element_z(self):
		if self.cur_analysis_step_z==len(self.get_analysis_map_z())-1:
			return bool(True);
		else:
			return bool(False);
	
	def is_first_analysis_map_element_x(self):
		if self.cur_analysis_step_x==0:
			return bool(True);
		else:
			return bool(False);

	def is_first_analysis_map_element_y(self):
		if self.cur_analysis_step_y==0:
			return bool(True);
		else:
			return bool(False);
	
	def is_first_analysis_map_element_z(self):
		if self.cur_analysis_step_z==0:
			return bool(True);
		else:
			return bool(False);
		
		
# Analysis measurement		


	def perform_analysis_step(self):
		# perform measurement in x-y-z	
		self.move_2_pos(self.get_cur_analysis_map_element())
		if self.is_last_analysis_map_element_x():
			if self.is_last_analysis_map_element_y():
				self.next_analysis_map_element_z();
			self.next_analysis_map_element_y();
		self.next_analysis_map_element_x();
		return;
		
	def perform_analysis_step_v2(self):
		# perform measurements in x-y hyperplane in serpentine-wise
		self.move_2_pos(self.get_cur_analysis_map_element())
		if(self.toggle==False):
			if self.is_last_analysis_map_element_x():
				if self.is_last_analysis_map_element_y():
					self.next_analysis_map_element_z();
				self.next_analysis_map_element_y();
				self.toggle=True
			else:
				self.next_analysis_map_element_x();
		else:
			if self.is_first_analysis_map_element_x():
				if self.is_last_analysis_map_element_y():
					self.next_analysis_map_element_z();
				self.next_analysis_map_element_y();
				self.toggle=False
			else:
				self.prev_analysis_map_element_x();