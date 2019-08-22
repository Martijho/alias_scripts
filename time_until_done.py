from datetime import datetime, timedelta

def sec_to_hms(total_s):
    h_left = (total_s / 60) // 60
    m_left = (total_s - 60*60*h_left) // 60
    s_left = total_s % 60
    return h_left, m_left, s_left

sec_in_day = 60*60*24

total_steps = int(input('Number of total steps: '))
completed = int(input('Number of completed computations: '))
h = int(input('Number of elapsed hours: '))
m = int(input('Number of elapsed minutes: '))
s = int(input('Number of elapsed seconds: '))
print()

total_s = 60*60*h + 60*m + s
steps_pr_s = completed / total_s

total_s_left = (total_steps-completed) / steps_pr_s
d = 0
if total_s_left > sec_in_day:
    d = total_s_left // sec_in_day
    total_s_left = total_s_left % sec_in_day
    print('\t', int(d), 'days, ', end='')

h, m, s = sec_to_hms(total_s_left)
clock = format(datetime.now() + timedelta(hours=int(h)) + timedelta(minutes=int(m)) + timedelta(seconds=int(s)), '%H:%M:%S')

print(int(h), 'hours,', int(m), 'minutes and', int(s), 'seconds')

print('\t Done at', clock)
print('\t Steps pr sec:', steps_pr_s)
