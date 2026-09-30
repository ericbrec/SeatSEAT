import math
import locale
import textwrap
import numpy as np
import mip
from collections import namedtuple
import glob
import pandas as pd

# Define a class to contain constraints
class Constraint:
    def __init__(self, description, isChecked, comparator, value, gameDictionaries = None):
        self.description = description
        self.isChecked = isChecked
        self.comparator = comparator
        self.value = value
        self.gameDictionaries = list() if gameDictionaries is None else gameDictionaries

# Define a class to contain each person's preferences
class SportsFan:
    def __init__(self, GamesInPlan, name, pairs, quads, ranking, extra = None):
        self.name = name
        self.pairs = pairs
        self.quads = quads

        # Assign weights to games
        if len(ranking) != 0:
            self.ranking = ranking
        else:
            self.ranking = GamesInPlan * [GamesInPlan // 2]

        # Adjust weights to favor highly ranked games

        self.useRanking = []
        midpoint = (GamesInPlan - 1) // 2
        for wgt in self.ranking:
            if wgt <= midpoint + 1:
                self.useRanking.append(math.sqrt(wgt - 1.0))
            else:
                self.useRanking.append(2.0 * math.sqrt(midpoint) - math.sqrt(2.0 * midpoint - wgt + 1))
        if len(self.useRanking) == GamesInPlan:
            self.useRanking += [2.0 * cost for cost in self.useRanking]
        else:
            for ix in range(GamesInPlan):
                self.useRanking[GamesInPlan + ix] *= 2

        # Each person must attend correct number of games

        pairCon = Constraint(f"{self.name}: Pairs = {self.pairs}", True, '==', self.pairs, [dict([(ix, 1.0) for ix in range(GamesInPlan)])])
        quadCon = Constraint(f"{self.name}: Quads = {self.quads}", True, '==', self.quads, [dict([(ix, 1.0) for ix in range(GamesInPlan, 2 * GamesInPlan)])])

        # Save all of the constraints for this person

        self.constraints = [pairCon, quadCon]
        if extra is not None:
            self.constraints += extra

class Allocator:
    def __init__(self, directory = ""):
        self.Initialize()
        if self.directory != "":
            self.LoadSchedule(self.directory)

    def Initialize(self):
        self.directory = ""
        self.errorReport = ""
        self.mainSheet = None
        self.schedule = []
        self.GamesInPlan = 0
        self.PairsInPlan = 0
        self.MaxPairsPerGame = 0
        self.logicalMonths = {}
        self.fans = []
        self.FansInPlan = 0
        self.tixModel = None

    def LoadSchedule(self, directory):
        self.Initialize()
        self.directory = directory
        globFilename = self.directory + "/Full Name*.xls*"
        excelFiles = glob.glob(globFilename)
        if len(excelFiles) < 1 or len(excelFiles) > 1:
            self.errorReport += f"Can't find unique excel file: {globFilename}\n"
            return
        self.mainSheet = pd.read_excel(excelFiles[0])

        ##### Find the constraint row #####
        for self.constraintRow in range(len(self.mainSheet.Date)):
            if self.mainSheet.iat[self.constraintRow,2] == "At least":
                break

        ##### Read the season schedule and store it as a list of games
        locale.setlocale(locale.LC_ALL, '')
        Game = namedtuple('Game', ('weekday', 'date', 'gameDay', 'time', 'opponent', 'type', 'price', 'pairs', 'seats'))
        openingDay = self.mainSheet.Date[0]
        gamesPerMonth = {}
        totalMonths = 0
        for weekday, date, time, opponent, type, price, pairs, seats in zip(self.mainSheet.Day, self.mainSheet.Date, self.mainSheet.Time, self.mainSheet.Opponent, self.mainSheet.Type, self.mainSheet.Price, self.mainSheet.GamePairs, self.mainSheet.Seats):
            if not isinstance(weekday, str) or weekday == "" or pd.isna(date):
                break
            pairs = int(pairs)
            self.schedule.append(Game(weekday, date, (date - openingDay).days, time.strftime("%I:%M %p"), opponent, type, price, pairs, seats))
            self.GamesInPlan += 1
            self.PairsInPlan += pairs
            self.MaxPairsPerGame = max(self.MaxPairsPerGame, pairs)
            if date.month not in gamesPerMonth:
                gamesPerMonth[date.month] = 1
                totalMonths += 1
            else:
                gamesPerMonth[date.month] += 1

        # If a month has a standard deviation fewer games than average, assign it to a neighboring month
        meanGamesPerMonth = 0
        for gameCount in gamesPerMonth.values():
            meanGamesPerMonth += gameCount
        meanGamesPerMonth /= totalMonths
        varGamesPerMonth = 0
        for gameCount in gamesPerMonth.values():
            varGamesPerMonth += (gameCount - meanGamesPerMonth) ** 2
        sigma = math.sqrt(varGamesPerMonth / totalMonths)
        self.logicalMonths = {}
        for month, gameCount in gamesPerMonth.items():
            if gameCount > meanGamesPerMonth - sigma:
                self.logicalMonths[month] = month
        for month in gamesPerMonth.keys():
            if month not in self.logicalMonths:
                # First, try to join a later month
                for newMonth in range(month + 1, totalMonths):
                    if newMonth in self.logicalMonths:
                        self.logicalMonths[month] = self.logicalMonths[newMonth]
                        break
            if month not in self.logicalMonths:
                # Otherwise, join an earlier month
                for newMonth in range(month - 1, -1, -1):
                    if newMonth in self.logicalMonths:
                        self.logicalMonths[month] = self.logicalMonths[newMonth]
                        break

    def LoadFans(self):
        #########################################################
        # Build a dictionary out of a list of games
        #
        #     buildCode == 0:    Create constraints for pair and quads
        #     buildCode == 2:    Create constraint for pairs only
        #     buildCode == 4:    Create constraint for quads only
        def BuildDict(gameList, buildCode = 0):
            pairList = []
            for game in gameList:
                if buildCode != 4:
                    pairList.append((game, 1.0))
                if buildCode != 2:
                    pairList.append((game + self.GamesInPlan, 1.0))
            return dict(pairList)

        ##### This constraint handles the spacing of games
        def Spacing(description, checked, comparator, value, pairsOrQuads = 0):
            constraint = Constraint(description, checked, comparator, np.float64(1))
            if not isinstance(value, (int,float,np.floating,np.integer)) or pd.isna(value) or value < 1 or value > self.GamesInPlan:
                self.errorReport += f"Bad constraint:{description}\n"
                return constraint
            daysApart = value + 1
            firstGame = 0
            lastGame = 0
            while True:
                while lastGame < self.GamesInPlan and self.schedule[firstGame].gameDay + daysApart > self.schedule[lastGame].gameDay:
                    lastGame += 1
                constraint.gameDictionaries.append(BuildDict(range(firstGame, lastGame), pairsOrQuads))
                if lastGame == self.GamesInPlan:
                    break
                while self.schedule[firstGame].gameDay + daysApart <= self.schedule[lastGame].gameDay:
                    firstGame += 1
            return constraint

        ##### Require or forbid games in various months
        def Monthly(description, checked, comparator, value, pairsOrQuads = 0):
            constraint = Constraint(description, checked, comparator, value)
            if not isinstance(value, (int,float,np.floating,np.integer)) or pd.isna(value) or value < 1 or value > 30:
                self.errorReport += f"Bad constraint:{description}\n"
                return constraint
            firstGame = 0
            month = self.logicalMonths[self.schedule[firstGame].date.month]
            lastGame = 0
            while True:
                while lastGame < self.GamesInPlan and self.logicalMonths[self.schedule[lastGame].date.month] == month:
                    lastGame += 1
                constraint.gameDictionaries.append(BuildDict(range(firstGame, lastGame), pairsOrQuads))
                if lastGame == self.GamesInPlan:
                    break
                firstGame = lastGame
                month = self.logicalMonths[self.schedule[firstGame].date.month]
            return constraint

        ##### Require or forbid games in different series
        def Series(description, checked, comparator, value, pairsOrQuads = 0):
            constraint = Constraint(description, checked, comparator, value)
            if not isinstance(value, (int,float,np.floating,np.integer)) or pd.isna(value) or value < 1 or value > self.GamesInPlan:
                self.errorReport += f"Bad constraint:{description}\n"
                return constraint
            firstGame = 0
            lastGame = 0
            while True:
                while lastGame < self.GamesInPlan and self.schedule[firstGame].opponent == self.schedule[lastGame].opponent:
                    lastGame += 1
                constraint.gameDictionaries.append(BuildDict(range(firstGame, lastGame), pairsOrQuads))
                if lastGame == self.GamesInPlan:
                    break
                firstGame = lastGame
            return constraint

        ##### Require or forbid games for different opponents

        def Opponents(description, checked, comparator, value, pairsOrQuads = 0):
            constraint = Constraint(description, checked, comparator, value)
            if not isinstance(value, (int,float,np.floating,np.integer)) or pd.isna(value) or value < 1 or value > self.GamesInPlan:
                self.errorReport += f"Bad constraint:{description}\n"
                return constraint
            firstGame = 0
            lastGame = 0
            opponentDict = {}
            while True:
                while lastGame < self.GamesInPlan and self.schedule[firstGame].opponent == self.schedule[lastGame].opponent:
                    lastGame += 1
                opponentGames = opponentDict.get(self.schedule[firstGame].opponent, [])
                opponentGames += range(firstGame, lastGame)
                opponentDict[self.schedule[firstGame].opponent] = opponentGames
                if lastGame == self.GamesInPlan:
                    break
                firstGame = lastGame
            for opponentGames in opponentDict.values():
                constraint.gameDictionaries.append(BuildDict(opponentGames, pairsOrQuads))
            return constraint

        SpreadSheetConstraint = namedtuple('SpreadSheetConstraint', ('function', 'comparator', 'pairsOrQuads'))
        constraintsToProcess = [
            SpreadSheetConstraint(Monthly, '>=', 0),
            SpreadSheetConstraint(Monthly, '<=', 0),
            SpreadSheetConstraint(Monthly, '>=', 2),
            SpreadSheetConstraint(Monthly, '<=', 2),
            SpreadSheetConstraint(Monthly, '>=', 4),
            SpreadSheetConstraint(Monthly, '<=', 4),
            SpreadSheetConstraint(Spacing, '<=', 0),
            SpreadSheetConstraint(Spacing, '>=', 0),
            SpreadSheetConstraint(Spacing, '<=', 2),
            SpreadSheetConstraint(Spacing, '>=', 2),
            SpreadSheetConstraint(Spacing, '<=', 4),
            SpreadSheetConstraint(Spacing, '>=', 4),
            SpreadSheetConstraint(Series, '<=', 0),
            SpreadSheetConstraint(Opponents, '<=', 0)
        ]

        ##### Define the participants here #####
        self.fans = []
        self.tixModel = None
        if self.mainSheet is None:
            return
        totalPairs = 0
        for fullName, nPairs, nQuads in zip(self.mainSheet.FullName, self.mainSheet.Pairs, self.mainSheet.Quads):
            if not isinstance(fullName, str) or fullName == "":
                break
            globFilename = self.directory + "/" + fullName + "*.xls*"
            excelFiles = glob.glob(globFilename)
            if len(excelFiles) < 1 or len(excelFiles) > 1:
                self.errorReport += f"Can't find unique excel file: {globFilename}\n"
                continue
            totalPairs += nPairs + 2 * nQuads
            fanSheet = pd.read_excel(excelFiles[0])
            pairsRank = [np.int64(fanSheet.Pick[ix]) for ix in range(self.GamesInPlan)]
            if not isinstance(fanSheet.QuadPick[0], np.float64) and not math.isnan(fanSheet.QuadPick[0]):
                quadsRank = [np.int64(fanSheet.QuadPick[ix]) for ix in range(self.GamesInPlan)]
                pairsRank += quadsRank

            # Add fan constraints
            extraConstraints = []
            for ix, sheetConstraint in enumerate(constraintsToProcess):
                row = self.constraintRow + ix
                if fanSheet.iat[row,1] or not pd.isna(fanSheet.iat[row,3]):
                    description = f"{fullName}{'' if fanSheet.iat[row,1] else ' (unchecked)'}: {fanSheet.iat[row,2]} {fanSheet.iat[row,3]} {fanSheet.iat[row,4]}"
                    extraConstraints.append(sheetConstraint.function(description, fanSheet.iat[row,1], sheetConstraint.comparator, fanSheet.iat[row,3], sheetConstraint.pairsOrQuads))
            self.fans.append(SportsFan(self.GamesInPlan, fullName, nPairs, nQuads, pairsRank, extraConstraints))

        # Create Spare Pairs for leftover games
        self.FansInPlan = len(self.fans)
        leftOver = self.PairsInPlan - totalPairs
        if leftOver < 0:
            self.errorReport += "Too many games requested\n"
        maxSparePairs = max((leftOver * self.GamesInPlan) // self.PairsInPlan, 1) # Maximum # of games that could be completely unassigned
        while leftOver > 0:
            pairsRank = (self.GamesInPlan * [np.int64(1)])[:]
            nPairs = min(leftOver, maxSparePairs)
            self.fans.append(SportsFan(self.GamesInPlan, f"Spare Pair", nPairs, 0, pairsRank))
            leftOver -= nPairs

    def GameRankingReport(self):
        gameRankingReport = "### Constraints:\n| Full Name | Pairs | Quads | Constraints |\n| :-: | :-: | :-: | :- |\n"
        for fan in self.fans[:self.FansInPlan]:
            gameRankingReport += f"| {fan.name} | {fan.pairs} | {fan.quads} | "
            for constraint in fan.constraints[2:]:
                gameRankingReport += f"{constraint.description[constraint.description.find(':') + 2:]}; "
            gameRankingReport += "\n"

        gameRankingReport += "\n### Games:\n| Day | Date | Time | Opponent | Type |"
        for fan in self.fans[:self.FansInPlan]:
            gameRankingReport += f" {fan.name} |"
        gameRankingReport += "\n| :-: | :-: | :-: | :-: | :-: |"  + " :-: |" * self.FansInPlan + "\n"
        for gix, game in enumerate(self.schedule):
            gameRankingReport += f"| {game.weekday} | {game.date.strftime('%x')} | {game.time} | {game.opponent} | {game.type} |"
            for fan in self.fans[:self.FansInPlan]:
                gameRankingReport += f"{int(fan.ranking[gix])}"
                if len(fan.ranking) > self.GamesInPlan:
                    gameRankingReport += f"({int(fan.ranking[self.GamesInPlan + gix])})"
                gameRankingReport += "|"
            gameRankingReport += "\n"
        return gameRankingReport

    def AllocateTickets(self):
        try:
            self.tixModel = mip.Model()
            self.tixModel.verbose = 0
            tixVars = []
            for fan in self.fans:
                tixVars += [self.tixModel.add_var(name = f"{fan.name}(pair {game.date.strftime('%x')} {game.time} {game.type})", var_type = mip.BINARY) for game in self.schedule]
                tixVars += [self.tixModel.add_var(name = f"{fan.name}(quad {game.date.strftime('%x')} {game.time} {game.type})", var_type = mip.BINARY) for game in self.schedule]
            slackVars = [self.tixModel.add_var(name = f"{fan.name}(slack+ {game.date.strftime('%x')} {game.time} {game.type})", var_type = mip.CONTINUOUS, ub = 0.0) for game in self.schedule]
            slackVars += [self.tixModel.add_var(name = f"{fan.name}(slack- {game.date.strftime('%x')} {game.time} {game.type})", var_type = mip.CONTINUOUS, ub = 0.0) for game in self.schedule]

            # All tickets must be allocated

            slackVarToConstraintMap = {}
            for ix in range(self.GamesInPlan):
                mipConstraint = self.tixModel.add_constr(mip.xsum(tixVars[ix + 2 * iy * self.GamesInPlan] + 2.0 * tixVars[ix + self.GamesInPlan + 2 * iy * self.GamesInPlan] for iy in range(len(self.fans))) + slackVars[2 * ix] - slackVars[2 * ix + 1] == self.schedule[ix].pairs, name = f"Allocate all tickets game {ix}")
                for var in slackVars:
                    slackVarToConstraintMap[var] = mipConstraint

            # Each fan must attend the correct number of games + satisfy all personal constraints

            for iy, fan in enumerate(self.fans):
                for ix, constraint in enumerate(fan.constraints):
                    for coefDict in constraint.gameDictionaries:
                        if constraint.comparator == '==':
                            slackVars.append(self.tixModel.add_var(name = f"slack+({constraint.description})", var_type = mip.CONTINUOUS, ub = 0.0))
                            slackVars.append(self.tixModel.add_var(name = f"slack-({constraint.description})", var_type = mip.CONTINUOUS, ub = 0.0))
                            linFunc = mip.xsum(count * tixVars[ix + iy * 2 * self.GamesInPlan] for ix, count in coefDict.items()) + slackVars[-2] - slackVars[-1]
                            mipConstraint = self.tixModel.add_constr(linFunc == constraint.value, name = f"{constraint.description}")
                            slackVarToConstraintMap[slackVars[-2]] = mipConstraint
                            slackVarToConstraintMap[slackVars[-1]] = mipConstraint
                        if constraint.comparator == '<=':
                            slackVars.append(self.tixModel.add_var(name = f"slack({constraint.description})", var_type = mip.CONTINUOUS, ub = 0.0))
                            linFunc = mip.xsum(count * tixVars[ix + iy * 2 * self.GamesInPlan] for ix, count in coefDict.items()) - slackVars[-1]
                            mipConstraint = self.tixModel.add_constr(linFunc <= constraint.value, name = f"{constraint.description}")
                            slackVarToConstraintMap[slackVars[-1]] = mipConstraint
                        if constraint.comparator == '>=':
                            slackVars.append(self.tixModel.add_var(name = f"slack({constraint.description})", var_type = mip.CONTINUOUS, ub = 0.0))
                            linFunc = mip.xsum(count * tixVars[ix + iy * 2 * self.GamesInPlan] for ix, count in coefDict.items()) + slackVars[-1]
                            mipConstraint = self.tixModel.add_constr(linFunc >= constraint.value, name = f"{constraint.description}")
                            slackVarToConstraintMap[slackVars[-1]] = mipConstraint

            # Establish the objective function

            costs = []
            for fan in self.fans:
                costs += fan.useRanking
            self.tixModel.objective = mip.xsum(costs[ix] * tixVars[ix] for ix in range(len(tixVars))) + mip.xsum(100000.0 * slackVars[ix] for ix in range(len(slackVars)))
        except Exception as e:
            self.errorReport += f"Mip setup exception: {e}\n"

        try:
            status = self.tixModel.optimize()
        except Exception as e:
            self.errorReport += f"Mip optimize exception: {e}\n"

        if status != mip.OptimizationStatus.OPTIMAL:
            self.errorReport += f"No solution found: {status}\n"
            if status == mip.OptimizationStatus.INFEASIBLE:
                self.errorReport += "Infeasible solution found.  Relaxing constraints to find a solution with minimum slack.\n"
                tixRelax = self.tixModel
                # Save a copy of the infeasible solution for later notebook cells
                self.tixModel = self.tixModel.copy() 
                # Reset the model, unrestrict the slack variables, and rerun the optimization to find the infeasible constraints
                tixRelax.reset()
                tixRelax.verbose = 0
                for var in slackVars:
                    var.ub = 1.0
                try:
                    status = tixRelax.optimize(max_seconds = 60)
                except Exception as e:
                    self.errorReport += f"Mip relax optimize exception: {e}\n"
                self.errorReport += f"{status} \n"
                for var in slackVars:
                    if var.x is not None and var.x > 0.0:
                        mipConstraint = slackVarToConstraintMap[var]
                        self.errorReport += f"Violated constraint: {mipConstraint.name}\n"
                        #self.errorReport += textwrap.fill(f"{mipConstraint.expr}", width = 80, initial_indent="    ", subsequent_indent="    ")

    def GameAllocationReport(self):
        if self.tixModel is None:
            return ""
        costs = {}
        gameAllocationReport = "### Game assignments:\n| Day | Date | Time | Opponent | Type | Seats |"
        for ix in range(self.MaxPairsPerGame):
            gameAllocationReport += f" Pair{ix+1} | Sent{ix+1} |"
        gameAllocationReport += "\n| :-: | :-: | :-: | :-: | :-: | :-: |"  + " :-: | :-: |" * self.MaxPairsPerGame + "\n"
        for gix, game in enumerate(self.schedule):
            gameAllocationReport += f"| {game.weekday} | {game.date.strftime('%x')} | {game.time} | {game.opponent} | {game.type} | {game.seats} |"
            for mix, mvar in enumerate(self.tixModel.vars):
                if mix % self.GamesInPlan == gix and mvar.x is not None and mvar.x > 0.5:
                    fix = mix // (2 * self.GamesInPlan)
                    if len(self.fans[fix].ranking) > self.GamesInPlan and mix % (2 * self.GamesInPlan) >= self.GamesInPlan:
                        gix += self.GamesInPlan
                    cost = costs.get(self.fans[fix].name, 0.0)
                    costs[self.fans[fix].name] = cost + 2.0 * game.price
                    gameAllocationReport += f" {self.fans[fix].name} ({self.fans[fix].ranking[gix]}) | |"
                    if mix % (2 * self.GamesInPlan) >= self.GamesInPlan:
                        costs[self.fans[fix].name] += 2.0 * game.price
                        gameAllocationReport += " | |"
            gameAllocationReport += " ❌ |" * (self.MaxPairsPerGame - game.pairs) + "\n"

        gameAllocationReport += "\n### Amount owed:\n| Full Name | Amount owed | Paid |\n"
        gameAllocationReport += "| :- | -: | -: |\n"
        for name, cost in sorted(costs.items()):
            gameAllocationReport += f"| {name} | {locale.currency(cost, grouping=True)} | |\n"

        return gameAllocationReport