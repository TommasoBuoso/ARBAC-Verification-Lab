# ARBAC-Verification-Lab
ARBAC analyser for small policies. 

As recommended by the professor, I decided to implement the analyser using the backward slicing for simplify the instances of the role reachability problem.

After parsing the policy, contained in the 'policies' directory, and after pruning the instances with the backward slicing method I start with the role reachability problem.

Starting from the user-to-role set taken from the policy, I save it in a list to take track of the sets already explored, then I try to apply all the Can-Assign and Can-Revoke rules, and for each new user-to-role set obtained by applying this rules I add it to the track of user-to-role set and I check if some user now has the role goal assigned. At the second iteration, for each of the user-to-role set created in the first iteration I try again to apply all the Can-Assign and Can-Revoke rules, and for each new user-to-role set obtained by applying this rules, if it isn't already in the track, I add it to the track of user-to-role set and I check if some user now has the role goal assigned. This process is repeated until the goal is found or there are no more user-to-role set to check or the iteration lasts more than a minute.

The program returns 1 if the goal role is reachable, 0 otherwise.

By analysing all the policies with this analyser 

```
$ python3 analyser.py < policies/policy1.arbac
```

I have obtained the flag: 10110110.