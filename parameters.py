# These should be constant between runs and are considered global

seats_left   = 3 #
seats_right  = 3 # To change these four, one should make sure
aisle_width  = 1 # that the rest of the code does not break.
aisle_y      = 0 #
plane_length = 16
plane_width  = seats_left + aisle_width + seats_right

seats_per_row= seats_left + seats_right
total_seats  = plane_length * seats_per_row
max_shuffle  = max(seats_left, seats_right)-1

# Space for waiting before boarding|shuffles at the back of the plane
board_before = total_seats + 1 # x=-1 is critical area for some strategies
board_after  = max_shuffle
board_length = board_before + plane_length + board_after
board_width  = plane_width
# valid indices range between
valid_xs = range(-seats_right, aisle_width+seats_left)
valid_ys = range(-board_before, plane_length+board_after)

walk_tick_cnt= 5
skip_tick_cnt= 2


display_width = 2*max_shuffle + plane_length
display_height= plane_width
display_scale = 64
display_framerate = 15

# Controlled by a passed parameter:
# # no_shuffles = False
# # no_stowing = False
# # mu = 10
sigma = 4/3

# this value can be changed by the test boarding methods
total_agents = total_seats