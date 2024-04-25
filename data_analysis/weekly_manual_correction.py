### description from Matlab
# This script is used to analyse the level ice draft identification point by point. First, year and
# location is specified of the mooring subset to be analysed. Analysis is done by observing several figures.

# Figure 1 illustrates a whole year of draft data suplemented with level ice draft and identified keels.

# Figure 2 zoomed in section of the current week's data.

# Figure 3 has four subplots showing the following :
# SP1 : LI DM vs Mean ridge keel draft
# SP2 : Draft histogram, PDF, AM, DM
# SP3 : LI DM vs Weekly deepest ridge draft
# SP4: LI DM vs Number of ridges

# Figure 4 shows the "distogram" plot where evolution of the level ice can be seen and outliers can
# be identified more reliably

# INSTRUCTIONS FOR GOING THROUGH THE LOOP
# 
#     - Arrow right     -   Go one week forward
#     - Arrow left      -   Go one week back
#     - Arrow up        -   Go 5 weeks forward
#     - Arrow down      -   Go 5 weeks back
#     - NumPad 0        -   Select the point to be analysed in Figure 4 (only horisontal location is enogh)
#     - Enter           -   Correct the location of level ice thickness in Figure 3
#     - NumPad -        -   Delete current point
#     - Esc             -   Go forward to next season/location

# In order to close the loop completely do the following
#       First press "NumPad +" and then press "Esc"