from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import numpy as np
from math import floor
import pandas as pd
import time



class Bowler:
    def __init__(self, name, overs, runs, wickets):
        self.name = name
        self.overs = overs
        self.runs = runs
        self.wickets = wickets
        self.bowling_now = False 
        self.ball_number = int(10*(overs-floor(overs)))
    
    def is_bowling(self, bowler_list):

        # if not 0th ball
        # need and not gone off/injured after 2 balls etc,
        # so want it to have been different to previous ball

        
        for bowler in bowler_list:
    
            if (bowler.name==self.name and
                bowler.ball_number>0 
                and bowler.ball_number!=self.ball_number
                ):

                # actually want bowler.ball_number!=self.ball_number,
                # just for testing purposes
                self.bowling_now = True




class Batter:
    def __init__(self, name, runs, balls, batter_is_out, innings_in_progress):
        self.name = name
        self.runs = runs
        self.balls = balls
        self.innings_in_progress = innings_in_progress
        self.is_out = batter_is_out





class Innings:
    def __init__(self, runs, overs, wickets, ind):
        try:
            runs_use = int(runs)
        except:
            runs_use = runs

        self.runs = runs_use
        self.overs = overs
        self.wickets = wickets

        self.index = ind
        
        try: 
            ovs = float(overs)
            decimal_overs = floor(ovs) + (ovs-floor(ovs))*(10/6)
            rns = float(runs)
            self.rr = round(rns/decimal_overs,2)
        except:
            self.rr = ""
        
        self.batsmen = []
        self.not_out_batsmen = []

        self.bowlers = []
        self.current_bowler = None

        self.team_name = None
        self.short_team_name = None


    def add_not_out_batter(self, batter):
        self.not_out_batsmen.append(batter)
    
    def add_batter(self, batter):
        self.batsmen.append(batter)

    def add_bowler(self, bowler):
        self.bowlers.append(bowler)
    
    def add_current_bowler(self, bowler):
        self.current_bowler = bowler

    def add_team_name(self, team_name):
        self.team_name = team_name
        self.short_team_name = team_name[:3].upper()

    def add_fow(self, fow):
        self.fow = fow








def get_soup(url):
    """
    Get webpage
    """

    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    html = urlopen(req)

    soup = BeautifulSoup(html, "html.parser")
    
    return soup






def _create_scorecard(soup):
    ##
    table = soup.find_all("div", class_="table-responsive-sm")
    
    scorecard_dfs = []
    

    for inns in range(len(table)):

        table_rows = table[inns].find_all('tr')

        l = [[]]
        for tr in table_rows[:-2]:
            td = tr.find_all('td')

            if len(td)>0:
                row = [tr.text for tr in td]
                
                batsman = str(td[0]).split('<div class="bts">')[1]

                if 'href' in batsman.split('>')[0]:
                    long_name = batsman.split('>')[1].split('<')[0].strip()
                else:
                    long_name = batsman.split('>')[0].split('<')[0].strip()

                # how_out = " ".join(row[1:3]).lstrip()
                # row_use = [long_name] + [how_out] + row[3:]
                row_use = [long_name] + row[1:]
                

                l.append(row_use)
        

        try:
            df = pd.DataFrame(l, columns =["Batsman", "How", "out", "Runs", "Balls", "4s", "6s", "SR"])
            df = df.iloc[1:,:]
            scorecard_dfs.append(df)
        except:
            pass
    
    return scorecard_dfs








def _add_batters(scorecard_dfs, innings_list):
    for inns in range(len(scorecard_dfs)):
        df = scorecard_dfs[inns]
        for rr in range(df.shape[0]):
            row = df.iloc[rr,:]

            long_name = row.loc['Batsman']

            if 'not out' in row[1]:
                name_use = long_name.split(' ')[-1]
                score_use = row.loc['Runs']
                balls_use = row.loc['Balls']
                batter_is_out = False
                batter = Batter(name_use, score_use, balls_use, batter_is_out, inns)
                innings_list[inns].add_not_out_batter(batter)
    
    return innings_list








def _get_team_scores(soup):

    scorecards = soup.find_all("div", class_="table-responsive-sm")

    innings_list = []


    for inns in range(len(scorecards)):
        scorecard = str(scorecards[inns])

        score = scorecard.split("<strong>Total: </strong>")[1]

        runs = score.split('(')[0].strip()

        overs = score.split('(')[1].split(',')[0].strip()
        overs = overs.split(' ')[0].strip()

        wickets = score.split(',')[1].split(')')[0].strip()
        wickets = wickets.split(' ')[0].strip()

        innings = Innings(runs, overs, wickets, inns)
        innings_list.append(innings)

    return innings_list









def _add_team_names(soup, innings_list):

    tables = soup.find_all("ul", class_="nav nav-tabs nav-justified subnav-2")

    table = str(tables[0])

    table_list = table.replace("\n","").split("</a>") # [0].split('>')[3].strip()

    for ind in range(len(table_list)-1):
        tab_list_temp = str(table_list[ind])
        try:
            
            if "1st Innings" in tab_list_temp:
                team = tab_list_temp.split('1st Innings </b><br/>')[1].strip()
            elif "2nd Innings" in tab_list_temp:
                team = tab_list_temp.split('2nd Innings </b><br/>')[1].strip()
            else:
                team = tab_list_temp.split('role="tab">')[1].strip()
            
            
            innings = innings_list[ind]
            innings.add_team_name(team)


        except:
            pass
    
    return innings_list
    

















def _add_fall_of_wicket(soup, innings_list):
    """
    Extract fall of wicket from soup.
    """
    scorecards = soup.find_all("div", class_="col-sm-12 fall-of-wickets pad-sm-1")
    
    for innings_in_progress in range(len(scorecards)):
        scorecard = str(scorecards[innings_in_progress])
        fow = scorecard.split('<strong>')[-1].split('</strong>')[0]
        innings_list[innings_in_progress].add_fow(fow)
    
    return innings_list







def _add_bowlers(soup, bowler_list, innings_list):
    """
    Extract bowling figures from soup. 
    
    See change to make below: bowler[1]!=ball_number
    """

    scorecards = soup.find_all("table", class_="table bowler-detail table-hover")

    bowlers_list_out = []

    for innings_in_progress in range(len(scorecards)):

        bowler_row = scorecards[innings_in_progress].find_all('tr')

        for tr in bowler_row:
            td = tr.find_all('td')

            
            if len(td)>0:
                bowler_str = str(td[0])
                

                if "href" in bowler_str:
                    long_name = bowler_str.split('>')[2].split('<')[0].split(" ")[-1].strip()
                else:
                    long_name = bowler_str.split('>')[1].split('<')[0].split(" ")[-1].strip()
                
                row = [tr.text for tr in td]

                overs = float(row[1])
                runs = row[3]
                wickets = row[4]
                
                bowler = Bowler(long_name, overs, runs, wickets)
                
                bowler.is_bowling(bowler_list) # check if this bowler is bowling now

                bowlers_list_out.append(bowler)
                
                innings_list[innings_in_progress].add_bowler(bowler)

                if bowler.bowling_now:
                    innings_list[innings_in_progress].add_current_bowler(bowler)
    
    return bowlers_list_out, innings_list














class ScoresFileWriter:
    def __init__(self):
        file_names_full_sc = []
        for col in range(5):
            file_names_full_sc.append(f'Generated_text/Full_scorecard/column_{str(col)}.txt')

        filenames_main = []
        for name in ["match", 
            "teams",
            "scores",
            "overs",
            "rr",
            "batsmen1",
            "batsmen2",
            "fow",
            "bowlers",
            ]:
            filenames_main.append(f"Generated_text/{name}.txt")
        
        self.filenames_full_sc = file_names_full_sc
        self.filenames_main = filenames_main




    def _get_dismissal_scorecard_text(self, txt):
        txt = str(txt)

        if txt=="lbw":
            return "LBW"
        elif txt.startswith("c"):
            return "ct " + txt[1:]
        else:
            return txt





    def _get_bowler_scorecard_text(self, txt):
        txt = str(txt)
        
        if txt.startswith("b"):
            return "b " + txt[1:]
        else:
            return txt






    def write_full_scorecard(self, sc_in, wickets, overs, score, team_name):
        
        scorecard = sc_in.applymap(str)

        team_name_use = team_name.upper()

        title = [team_name_use, "", "", "", ""]

        column_names = ["", "", "", "Runs", "Balls"]

        wickets_use = "10" if wickets=="All" else wickets

        final_text = ["", f"for {wickets_use} wickets", f"in {overs} overs", f"{score}", ""]
        
        space_list_left = [1,1,1,4,4]

        space_list_right = [100,20,20,4,4]
        
        scorecard_text_dict = {}
        
        # generate scores
        for col in range(len(self.filenames_full_sc)):
            # goes through columns: Name/how out/bowler/runs/balls
            df = scorecard.iloc[:,int(col)]

            spaces_l = space_list_left[int(col)]
            spaces_r = space_list_right[int(col)]
            
            # team name
            txt_out = [" "*spaces_l + title[int(col)] + " "*spaces_r +"\n"]

            # column headings
            txt_out.append(" "*spaces_l + column_names[int(col)] + " "*spaces_r +"\n")

            # scorecard content
            for txt in df:
                if col==1:
                    # txt_use=txt
                    txt_use = self._get_dismissal_scorecard_text(txt)
                elif col==2:
                    # txt_use=txt
                    txt_use = self._get_bowler_scorecard_text(txt)
                else:
                    txt_use = txt

                txt_out.append(" "*spaces_l + txt_use + " "*spaces_r +"\n")
            
            # totals/bottom text
            txt_out.append("\n" + " "*spaces_l + final_text[int(col)] + " "*spaces_r +"\n")

            scorecard_text_dict[col] = txt_out

        for col in range(len(self.filenames_full_sc)):
            file_ = open(self.filenames_full_sc[col], 'w')
            file_.writelines(scorecard_text_dict[col])

        



    def erase_full_scorecard(self):
        for col in range(len(self.filenames_full_sc)):
            file_ = open(self.filenames_full_sc[col], 'w')
            file_.writelines("")



    def did_not_work(self):
        lines_out = ["error updating scorecard..."] + [""]*(len(self.filenames_main)+len(self.filenames_full_sc)-1)

        file_names_use = self.filenames_main + self.filenames_full_sc

        for file_name_, lines in zip(file_names_use,lines_out):
            file_ = open(file_name_, 'w')
            file_.writelines(lines)
    
    

    def _get_current_innings_index(self, innings_list):
        
        N_innings = len(innings_list)
        
        current_inns_index = N_innings-1

        condition = True
        while condition:
            if innings_list[current_inns_index].overs=='Overs': 
                # instead of a number, so that 2nd innings hasn't started yet, 
                # then try previous innings, and iterate
                current_inns_index = current_inns_index-1
            else:
                condition = False
                # end loop
        
        return current_inns_index
    



    def _get_bowler_out(self, innings_use):
        bowler_out = [""]
        
        bowler = innings_use.current_bowler
        if bowler is not None:
            bowler_out = [f" {bowler.name} {bowler.wickets}-{bowler.runs} ({bowler.overs})"]
        
        return bowler_out


    def _get_batsmen_info(self, innings_use):
        batsmen_info = [[""]]*2
        
        for ind, batter in enumerate(innings_use.not_out_batsmen):
            batsmen_info[ind] = [f" {batter.name} {batter.runs} ({batter.balls})"]

        return batsmen_info






    def _get_team_score_df(self, innings_list):
        names_list = []
        scores_list = []
        wickets_list = []

        for inn in innings_list:
            names_list.append(inn.short_team_name)
            scores_list.append(inn.runs)
            wickets_list.append(inn.wickets)

        team_score_df = pd.DataFrame(data=dict(
            team_name = names_list,
            score = scores_list,
            wickets = wickets_list
        ))

        return team_score_df

    def _get_match_situation_not_first_inns(self, team_score_df, current_name, current_inns_index):
        
        score_current = team_score_df[team_score_df.team_name==current_name].score.sum()
        
        score_other_team = team_score_df[team_score_df.team_name!=current_name].score.sum()

        difference = int(score_current - score_other_team)

        match_sit_name = current_name[:3].upper()
            
        if difference>0:
            try:
                # if 4 day game - needs to say leads by...
                # need to see what scorecard looks like midway through
                # suspect current method will work
                if current_inns_index in [1,3]: # 2nd or 4th innings
                    wickets_curr = float(team_score_df.loc[current_inns_index,'wickets'])
                    win_wicks = int(10-wickets_curr)
                
                    if win_wicks==1:
                        match_situation = f" {match_sit_name} win by 1 wicket"
                    else:
                        match_situation = f" {match_sit_name} win by {win_wicks} wickets"
                
                elif current_inns_index==1: # 3rd innings
                    if difference==1:
                        match_situation = f" Lead by 1 run"
                    elif difference>1:
                        match_situation = f" Lead by {difference} runs"
                
            except:
                match_situation = ""

        elif difference==0:
            match_situation = f" Scores tied"
        elif difference==-1:
            match_situation = f" Trail by 1 run"
        else:
            match_situation = f" Trail by {-difference} runs"
        
        return match_situation





    def _get_match_situation(self, team_score_df, current_inns_index):
          
        current_name = team_score_df.loc[current_inns_index, 'team_name']

        match_situation = ""

        try:
            if current_inns_index==0: # 1st innings
                match_situation = " 1st Innings"
            
            else: # if not first innings
                match_situation = self._get_match_situation_not_first_inns(team_score_df,
                            current_name, 
                            current_inns_index)
        
        except:
            pass

        return match_situation





    
    def _get_run_rate(self, innings_use):

        if innings_use.rr!="":
            out = [f" RR: {innings_use.rr}"]
        else:
            out = [""]
        
        return out



    def _get_scores_out(self, innings_use):

        if innings_use.wickets in ['All out','All']:
            out = [f" {innings_use.runs}"]
        else:
            out = [f" {innings_use.runs}/{innings_use.wickets}"]

        return out



    def _get_overs_out(self, innings_use):

        if innings_use.overs=='1':
            out = [f" 1 over"]
            # singular not plural
        else:
            out = [f" {innings_use.overs} overs"]
        
        return out




    def _get_fow_out(self, innings_use):

        fow_out = [""]
        try:
            if innings_use.fow is not "":
                fow_out = [f" Last wkt: {innings_use.fow}"]
        except:
            pass

        return fow_out
    
    
    def _save_and_print(self, lines_out, print_output):
        if print_output:
            print(lines_out)


        for file_name_, lines in zip(self.filenames_main, lines_out):
            file_ = open(file_name_, 'w')
            file_.writelines(lines)




    def write_files(self, innings_list, print_output=False):
        
        current_inns_index = self._get_current_innings_index(innings_list)
        
        innings_use = innings_list[current_inns_index]

        bowler_out = self._get_bowler_out(innings_use)
        
        batsmen_info = self._get_batsmen_info(innings_use)

        team_score_df = self._get_team_score_df(innings_list)

        match_situation = self._get_match_situation(team_score_df, current_inns_index)

        teams_out = [f" {innings_use.short_team_name}"]

        rr_out = self._get_run_rate(innings_use)
        
        scores_out = self._get_scores_out(innings_use)
        
        overs_out = self._get_overs_out(innings_use)

        fow_out = self._get_fow_out(innings_use)


        # output to be saved
        lines_out = [
                    [match_situation],
                    teams_out,
                    scores_out,
                    overs_out,
                    rr_out,
                    batsmen_info[0],
                    batsmen_info[1],
                    fow_out,
                    bowler_out
                ]

        self._save_and_print(lines_out, print_output)
        
        return None
        



def _get_full_scorecard(innings_list, file_writer, scorecards, current_inns_index):
    """
    Writes a full scorecard to appear momentarily on the screen
    """

    fs_innings = innings_list[current_inns_index]

    ov_use = fs_innings.overs
    runs_use = fs_innings.runs
    wickets_use = fs_innings.wickets
    team_use = fs_innings.team_name

    sc_in = scorecards[current_inns_index]

    file_writer.write_full_scorecard(sc_in, wickets_use, ov_use,
                    runs_use, team_use)
    






def _get_updated_scores(url_use, sleeptime, scorecard_overs, 
                max_time_full_scorecard, bowlers_list, t_shown):

    file_writer = ScoresFileWriter()

    try:
    # if True:

        soup = get_soup(url_use)
        
        scorecards = _create_scorecard(soup)

        # most important is this, can operate without the rest
        innings_list = _get_team_scores(soup)

        innings_list = _add_team_names(soup, innings_list)

        try:
            innings_list = _add_batters(scorecards, innings_list)
        except Exception as e:
            print(f"_add_batters Error: {e}")

        try:
            innings_list = _add_fall_of_wicket(soup, innings_list)
        except Exception as e:
            print(f"_add_fall_of_wicket Error: {e}")

        try:
            bowlers_list, innings_list = _add_bowlers(soup, bowlers_list, innings_list)
        except Exception as e:
            print(f"_add_bowlers Error: {e}")

        file_writer.write_files(innings_list, print_output=False)



        # full scorecard
        try:
            current_inns_index = ScoresFileWriter()._get_current_innings_index(innings_list)

            if (float(innings_list[current_inns_index].overs) in scorecard_overs and
                    t_shown<max_time_full_scorecard
                    ):

                _get_full_scorecard(innings_list, file_writer, scorecards, current_inns_index)
            
                # assume it takes 1.2 seconds to run the loop
                t_shown += sleeptime + 1.2
                print(f'showing full scorecard, shown for={t_shown} seconds')


            else:
                print(f"\n")
                print(f"no longer show scorecard")
                print(f"shown for={round(t_shown,2)} seconds already,")
                print(f'or overs not in scorecard_overs')

                file_writer.erase_full_scorecard()
                
                if not float(innings_list[current_inns_index].overs) in scorecard_overs:
                    # only reset if overs have moved on
                    print('reset t_shown')
                    t_shown = 0
        
        except Exception as e:
            print(f"Full Scorecard Error: {e}")
            file_writer.erase_full_scorecard()
            t_shown = 0
        


    except Exception as e:
        print(f"Loop Error: {e}")
        
        file_writer.did_not_work()
    
    return t_shown, bowlers_list






def generate_scorecard_all_day(
            url_use,
            sleeptime,
            scorecard_every_n_overs = None,
            max_time_full_scorecard = 10
            ):
    
    # initialise variables
    bowlers_list = []
    t_shown = 0

    scorecard_overs = [float(i) for i in range(0,51,scorecard_every_n_overs)][1:]
    # scorecard_overs = [float(38) for i in range(0,51,scorecard_every_n_overs)][1:]

    while True:
        
        t_shown, bowlers_list = _get_updated_scores(url_use, sleeptime, scorecard_overs, 
                    max_time_full_scorecard, bowlers_list, t_shown)
        
        time.sleep(sleeptime)






def generate_scorecard_once(
            url_use,
            sleeptime,
            scorecard_every_n_overs = None,
            max_time_full_scorecard = 10
            ):
    
    # initialise variables
    bowlers_list = []
    t_shown = 0
    
    scorecard_overs = [float(i) for i in range(0,51,scorecard_every_n_overs)][1:]

    for _ in [1, 2]:
        
        t_shown, bowlers_list = _get_updated_scores(url_use, sleeptime, scorecard_overs, 
                    max_time_full_scorecard, bowlers_list, t_shown)
        
        time.sleep(sleeptime)