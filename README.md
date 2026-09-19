# SeatSEAT

**SeatSEAT** is a Jupyter notebook and Excel template you can use to allocate season tickets fairly and optimally among a group of sports fans without going through a draft or auction.
* The algorithm is based on Thomas Grandine's "Assigning season tickets fairly." Interfaces 28, no. 4 (1998): 15-20.
* The Jupyter notebook is called "AllocateTickets.ipynb" and can found in the top folder.
* The Excel template is called "Full Name - [Team] [Season].xlsx" and can be found in the examples folders.

Organizer Instructions
======================
1. Download a copy of AllocateTickets.ipynb
2. Change the value of directory at the beginning of the notebook to a file directory where you plan to store the Excel template and fan picks.
3. Download a copy of "Full Name - [Team] [Season].xlsx" to your target directory and rename it to reflect the desired team and season.
4. Fill out the Date, Time, Opponent, and Type columns in the template with your home game schedule. The Day column is calculated automatically. The Type column indicates the type of ticket which maps to a ticket price (see step 8). If all your game tickets have the same price, just put "A" in the Type column for every game.
5. Fill out the Promotions column in the template with whatever promotions have been announced, if any.
6. The other game columns are calculated automatically--please don't change them. If you accidentally change them, you may need to start over.
7. Fill out the FullName, Pairs, and Quads columns with the full names of your season ticket group and how many pairs and quads of tickets each fan has signed up to purchase for the coming season. The other columns are calculated automatically. If you only have two tickets per game, leave the Quads column(s) blank or zero.
8. Fill out the Type and Price table under the FullName table with each type of ticket and how much one ticket of that type costs. If all your game tickets have the same price, just put an "A" for the Type and the price per ticket for the Price.
9. Send your season ticket group members the FullName table (copy/paste it into a message), asking them to verify the spelling of their names and their allocation of pairs and quads. Adjust the FullName table as needed.
10. Double check your game, fan, and ticket pricing information in your template. When everything seems proper, send the full template to your season ticket group along with the "Ticket Selection Instructions" below. Be sure to fill out the stadium name, seat location info, seat location description, and deadline date in the instructions before sending.
11. As you receive filled out templates from members of your season ticket group, verify the file names have been changed properly and save the files in your target directory.
12. Once you have received all the templates, run your copy of of AllocateTickets.ipynb. Feel free to use the generated markup to share the resulting ticket allocation and amount owed tables with your group. Ask if there are any mistakes, broken constraints, or missing information. If so, make the desired changes to the templates as needed and repeat until you have a fair and optimal ticket allocation. Often a single run is sufficient. Enjoy the season!

Ticket Selection Instructions
=============================
Our seats at [*stadium name*] are located in Section [*XXX*], Row [*XX*], Seats [*XX-XX*].  These are located [*location description*].  The prices are indicated on the attached game schedule spreadsheet.

Tickets are only available in pairs, so you may not purchase an odd number of tickets to any game during the regular season.

Here is the procedure for ticket selection:

1. Rename the attached spreadsheet, replacing "Full Name" with your full name exactly as listed in the far right "FullName" table. If the number of pairs and/or quads for you are incorrect in that table, please notify me (the organizer) immediately.
2. Do not change anything in the sheet other than the Rank column (and optionally the QuadRank column), the Comments column, the tiebreaker rule, and any optional constraints you select.
3. Known game day promotions are listed.  There may be additional giveaways and special events.
4. Enter your numerical rank for each game for the entire Rank column (the lowest rank is your top choice). You can give groupings of similar games the same rank. For example, say your top priority are fireworks nights, your second priority are Sunday games, your third priority are division games, your fourth priority are all other games, and your last priority are games your can't (or won't) attend. You can rank the fireworks nights 1, the Sunday games 2, the remaining division games 3, the games you can't attend 5, and all the remaining games 4. Any numerical rank is acceptable, including decimals (though whole numbers are preferred). 
5. If your quad ranks differ from your pair ranks, also fill out the entire QuadRank column, otherwise leave that column blank. 
6. Select your desired tiebreaking rule for games with the same rank. There are three rules:
   - **Random**: Games with the same rank are randomly ordered in priority.
   - **Prefer earlier dates**: Games with the same rank that are earlier in the season are given priority over other games with that same rank.
   - **Prefer later dates**: Games with the same rank that are later in the season are given priority over other games with that same rank.
   -  Your final pick order after the tiebreaker is automatically calculated and shown in the Pick column. To tweak the pick order, change your rank values (or the tiebreaking rule).
7. If desired, select from the constraints listed. Normally, you will not need to use the (pairs) and (quads) constraints unless you need to achieve different spacings between games for pairs and quads.
8. Custom sort the games list by day, time, and type before submitting (ignore if you never resorted the list).
9. The deadline for sending me (the organizer) your renamed spreadsheet is [*deadline date*]. This deadline allows me to provide everyone ticket assignments early enough for people to plan vacations, business trips, etc., without interfering with their ticketed games.
10. Once tickets are allocated, pay the balance due, take delivery of your tickets, and enjoy the season!