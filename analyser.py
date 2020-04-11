import time
import sys

def goal_found(ua_to_check, goal):
	for ua in ua_to_check:
		for role in ua:
			if(role[1] == goal):
				return True
	return False

def user_role_dict(ur):
	res = {}
	for elem in ur:
		if(elem[0] in res):
			res[elem[0]].append(elem[1])
		else:
			res[elem[0]] = [elem[1]]
	return res

def can_assign_role(ca, ur):
	res = []

	for ua in ur:
		if(ua[1] == ca[0]):
			ur_dict = user_role_dict(ur)

			for u in ur_dict:
				roles = set(ur_dict[u])
				rp = set(ca[1])
				rn = set(ca[2])

				if( (roles & rp) == rp and len(list(roles & rn)) == 0 and not(ca[-1] in roles) ):
					res.append(u)
			break

	return res

def can_revoke_role(cr, ur):
	res = []

	for ua in ur:
		if(ua[1] == cr[0]):
			for ut in ur:
				if(ut[1] == cr[1]):
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

#remove from CA all the rules that revoke a role in R \ S*
ca_sliced = []
for c in ca:
	if(c[-1] in roles):
		ca_sliced.append(c)
ca = ca_sliced

#remove from CR all the rules that revoke a role in R \ S*
cr_sliced = []
for c in cr:
	if(c[-1] in roles):
		cr_sliced.append(c)
cr = cr_sliced


#ROLE REACHABILITY

timeout = time.time() + 60
start_time = time.time()
ua_track = [set(tuple(x) for x in ua)]
ua_to_check = [ua]

while( time.time() < timeout and len(ua_to_check) and not( goal_found(ua_to_check, goal) )) :
	new_ua_to_check = []

	for ur in ua_to_check:
		ur_to_add = []
		for c in ca:
			users_to_add = can_assign_role(c, ur)
			for u in users_to_add:
				ur_to_add.append([u, c[-1]])

		for u in ur_to_add:
			new_ur = ur.copy()
			new_ur.append(u)
			new_ur_set = set(tuple(x) for x in new_ur)

			if( not (new_ur_set in ua_track) ):
				new_ua_to_check.append(new_ur)
				ua_track.append(new_ur_set)

		ur_to_revoke = []
		for c in cr:
			user_to_revoke = can_revoke_role(c, ur)
			for u in user_to_revoke:
				ur_to_revoke.append([u, c[-1]])

		for u in ur_to_revoke:
			new_ur = ur.copy()
			new_ur.remove(u)
			new_ur_set = set(tuple(x) for x in new_ur)

			if( not (new_ur_set in ua_track) ):
				new_ua_to_check.append(new_ur)
				ua_track.append(new_ur_set)

	ua_to_check = new_ua_to_check

if(goal_found(ua_to_check, goal)):
	print(1)
else:
	print(0)