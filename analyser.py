import time
import sys

#given a list of user-role check if any user has the goal role r_g 
def goal_found(ua_to_check, goal):
	for ua in ua_to_check:
		for role in ua:
			if(role[1] == goal):
				return True
	return False

#given a list of user-role return a dictionary that has users as keys and their roles as values
def user_role_dict(ur):
	res = {}
	for elem in ur:
		if(elem[0] in res):
			res[elem[0]].append(elem[1])
		else:
			res[elem[0]] = [elem[1]]
	return res

#function that takes as input a CA = (ra, Rp, Rn, rt) and a list of user-role
#and return the list of users that can recive the role rt
def can_assign_role(ca, ur):
	res = []

	for ua in ur:
		if(ua[1] == ca[0]):								#(ua, ra) ∈ UR
			ur_dict = user_role_dict(ur)

			for u in ur_dict:
				roles = set(ur_dict[u]) 				#UR(ut)
				rp = set(ca[1])
				rn = set(ca[2])

				#Rp ⊆ UR(ut) and Rn ∩ UR(ut) = ∅ and not( rt ∈ UR(ut) )
				if( (roles & rp) == rp and len(list(roles & rn)) == 0 and not(ca[-1] in roles) ):
					res.append(u)
			break

	return res

#function that takes as input a CR = (ra, rt) and a list of user-role
#and return the list of users that can lose the role rt
def can_revoke_role(cr, ur):
	res = []

	for ua in ur:
		if(ua[1] == cr[0]):								#(ua, ra) ∈ UR
			for ut in ur:
				if(ut[1] == cr[1]):						#rt ∈ UR(ut)
					res.append(ut[0])
		break

	return res

roles = []
users = []
ua = []     #user-role
cr = []     #can-revoke rules
ca = []     #can-assign rules
goal = ""   #r_g
count = 0

#read from stdin
for line in sys.stdin:
	if(count == 0):
		roles = line.split()[1:-1]
	elif(count == 2):
		users = line.split()[1:-1]
	elif(count == 4):
		ua = [ [u_a.split(",")[0][1:], u_a.split(",")[1][:-1]] for u_a in line.split()[1: -1] ] #[u, r]
	elif(count == 6):
		cr = [ [c_r.split(",")[0][1:], c_r.split(",")[1][:-1]] for c_r in line.split()[1: -1] ] #[ra, rt]
	elif(count == 8):
		for c_a in line.split()[1: -1]:
			ca.append( [ c_a.split(",")[0][1:], [], [], c_a.split(",")[-1][:-1] ] )     #[ra, Rp, Rn, rt]
			if(c_a.split(",")[1] != "TRUE"):
				for s in c_a.split(",")[1].split("&"):
					if(s[0] == "-"):
						ca[-1][2].append(s[1:])
					else:
						ca[-1][1].append(s)
	elif(count == 10):
		goal = line.split()[1]
	count += 1


#BACKWARD SLICING

s = [goal]                                                                  #intial state
fixed_point = False

while(not fixed_point):                                                     #iterate while the fixed point S* isn't reached
	s_next = s                                                              #initialize the next state with the previous

	for c in ca:                                                            #iterate all can-assign rules
		if(c[-1] in s):                                                     #if rt is in the previous state
			s_next = list( set(s_next) | set(c[1]) | set(c[2]) | {c[0]} )   #S_i = S_i−1 ∪ { Rp ∪ Rn ∪ {ra} }

	if(s_next == s):
		fixed_point = True                                                  #if s_i == s_i-1 we reach the fixed point
	else:
		s = s_next                                                          #otherwise assign s_i to s_i-1 and repeat

roles = s

ca_sliced = []
for c in ca:
	if(c[-1] in roles):
		ca_sliced.append(c)		#remove from CA all the rules that revoke a role in R \ S*
ca = ca_sliced

cr_sliced = []
for c in cr:
	if(c[-1] in roles):
		cr_sliced.append(c)		#remove from CR all the rules that revoke a role in R \ S*
cr = cr_sliced


#ROLE REACHABILITY

timeout = time.time() + 60					#set timout to force the termination
ua_track = [set(tuple(x) for x in ua)]		#track of user-to-role assignments already explored, prevents from the same part of the search space multiple times and looping
ua_to_check = [ua]							#list that contains the user-to-role lists that could constain the goal

while( time.time() < timeout and len(ua_to_check) and not( goal_found(ua_to_check, goal) )) :	#iterate while the timeout is reached or there are user-to-role lists to check or the goal isn't assigned
	new_ua_to_check = []								#list of list of user-to-role to check

	for ur in ua_to_check:								#iterate all the user-role list already checked
		ur_to_add = []
		for c in ca:									#for each CA
			users_to_add = can_assign_role(c, ur)		#create the list of users that can recive the role rt
			for u in users_to_add:
				ur_to_add.append([u, c[-1]])			#from the list just created, create the list of user-role to add to the list already checked

		for u in ur_to_add:
			new_ur = ur.copy()
			new_ur.append(u)
			new_ur_set = set(tuple(x) for x in new_ur)

			if( not (new_ur_set in ua_track) ):			#if, by adding the user-role to the list, the new user-to-role list isn't in the track
				new_ua_to_check.append(new_ur)			#add the list to the user-to-role to check
				ua_track.append(new_ur_set)				#add the list to the track

		ur_to_revoke = []
		for c in cr:									#for each CR
			user_to_revoke = can_revoke_role(c, ur)		#create the list of users that can lose the role rt
			for u in user_to_revoke:
				ur_to_revoke.append([u, c[-1]])			#from the list just created, create the list of user-role to remove from the list already checked

		for u in ur_to_revoke:
			new_ur = ur.copy()
			new_ur.remove(u)
			new_ur_set = set(tuple(x) for x in new_ur)

			if( not (new_ur_set in ua_track) ):			#if, by removing the user-role from the list, the new user-to-role list isn't in the track
				new_ua_to_check.append(new_ur)			#add the list to the user-to-role to check
				ua_track.append(new_ur_set)				#add the list to the track

	ua_to_check = new_ua_to_check

if(goal_found(ua_to_check, goal)):
	print(1)
else:
	print(0)