import EM_station
import time
import msvcrt

"This would create first object of Employee class"
EMS = EM_station.EM_station()

print ' Press h '
print ''
input_char='H'
while (input_char.upper() != 'X'):
	input_char = msvcrt.getch()
	if input_char.upper() == 'H':
		print '***************************************'
		print 'h:	help menu'
		print 'p:	set parameter' 
		print ' '
		print 'a:	move probe to the rigth'
		print 'd:	move probe to the left'
		print 'w:	move probe into the depth'
		print 's:	move probe out of the depth'
		print 'r:	move probe up'
		print 'f:	move probe down'
		print ' '
		print 'c:	current probe position [x,y,z]'
		print '0:	move probe to position [0,0,0]'
		print '1:	store current position in A'
		print '2:	store current position in B'
		print '3:	move probe to position A'
		print '4:	move probe to position B'
		print ' '
		print 'x:	end program'
		print '***************************************'
		print ' '
	
	if input_char.upper() == 'P': 
		parameter_set = input('Set step with:')
		EMS.set_step_width(parameter_set);
		print 'Step with is set to:',EMS.get_step_width();
		
		parameter_set = input('Set Analysis step for x:')
		EMS.set_analysis_steps_x(parameter_set);
		print 'Analysis step with for x is:',EMS.get_analysis_steps_x();
		parameter_set = input('Set Analysis step for y:')
		EMS.set_analysis_steps_y(parameter_set);
		print 'Analysis step with for y is:',EMS.get_analysis_steps_y();
		parameter_set = input('Set Analysis step for z:')
		EMS.set_analysis_steps_z(parameter_set);
		print 'Analysis step with for z is:',EMS.get_analysis_steps_z();
		
	if input_char.upper() == 'W': 
		EMS.one_pos_step_y();
	if input_char.upper() == 'S': 
		EMS.one_neg_step_y();	
	if input_char.upper() == 'A': 
		EMS.one_pos_step_x();	
	if input_char.upper() == 'D': 
		EMS.one_neg_step_x();
	if input_char.upper() == 'R': 
		EMS.one_pos_step_z();
	if input_char.upper() == 'F': 
		EMS.one_neg_step_z();
	
	if input_char.upper() == 'C': 
		print EMS.get_cur_pos();
		
	if input_char == '0': 
		EMS.move_2_pos_000();
	
	if input_char == '1': 
		EMS.set_pos_A(EMS.get_cur_pos());
		print 'Stored position of A:',EMS.get_pos_A();
	
	if input_char == '2': 
		EMS.set_pos_B(EMS.get_cur_pos());
		print 'Stored position of B:',EMS.get_pos_B();
	
	if input_char == '3':
		EMS.move_2_pos(EMS.get_pos_A());
		print 'Probe is at postion A'
		
	if input_char == '4':
		EMS.move_2_pos(EMS.get_pos_B());
		print 'Probe is at postion B'

	if input_char == '5':
		EMS.gen_analysis_map();
		print 'Analysis map for x:',EMS.get_analysis_map_x();
		print 'Analysis map for y:',EMS.get_analysis_map_y();
		print 'Analysis map for z:',EMS.get_analysis_map_z();

	if input_char == '6':
		EMS.gen_analysis_map();
		EMS.move_2_pos(EMS.get_pos_A());
		while (not(EMS.is_last_analysis_map_element_x() and EMS.is_last_analysis_map_element_y() and EMS.is_last_analysis_map_element_z())):
			EMS.perform_analysis_step();
			print EMS.get_cur_pos();
		EMS.perform_analysis_step();
		print EMS.get_cur_pos();
		
	if input_char == '7':
		EMS.gen_analysis_map();
		EMS.move_2_pos(EMS.get_pos_A());
		if (EMS.get_analysis_steps_x()%2==0):
			while (not(EMS.is_first_analysis_map_element_x() and EMS.is_last_analysis_map_element_y() and EMS.is_last_analysis_map_element_z())):
				EMS.perform_analysis_step_v2();
				print EMS.get_cur_pos();
			EMS.perform_analysis_step_v2();
			print EMS.get_cur_pos();	
		else:
			while (not(EMS.is_last_analysis_map_element_x() and EMS.is_last_analysis_map_element_y() and EMS.is_last_analysis_map_element_z())):
				EMS.perform_analysis_step_v2();
				print EMS.get_cur_pos();
			EMS.perform_analysis_step_v2();
			print EMS.get_cur_pos();
		
		
		

