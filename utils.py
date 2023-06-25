from urllib.request import urlopen, Request
from bs4 import BeautifulSoup


class ScorecardExtractor:
    def __init__(self, url) -> None:
        soup = self.get_soup(url)
        self.get_data(soup)


    @staticmethod
    def get_soup(url):
        """
        Get webpage
        """

        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        html = urlopen(req)

        soup = BeautifulSoup(html, "html.parser")

        return soup


    def get_data(self, soup):

        teams_raw = soup.find_all("p", class_="team-name")[:2]

        team_data_raw = soup.find_all("p", class_="team-info-2")[:2]

        home_team = TeamData(teams_raw[0], team_data_raw[0])
        away_team = TeamData(teams_raw[1], team_data_raw[1])

        home_batting = self.check_which_team_batting(home_team, away_team)

        if home_batting:
            self.data = dict(batting=home_team,
                            bowling=away_team)
        else:
            self.data = dict(batting=away_team,
                            bowling=home_team)




    def check_which_team_batting(self, home_team, away_team):
        
        if len(home_team.scores)>len(away_team.scores):
            return True
        elif len(home_team.scores)<len(away_team.scores):
            return False
        else:
            return self.both_batted_same_n_times(home_team)
    


    @staticmethod
    def both_batted_same_n_times(home_team):
        """
        Check which one has declared or been bowled out (other will be bat)
        """
        
        if not home_team.wickets:
            return False

        if "dec" in home_team.wickets[-1] or "All out" in home_team.wickets[-1]:
            return False
        else:
            return True

# End of Scorecard Generator






class TeamData:
    def __init__(self, team_name, data) -> None:
        self.team_name_raw = team_name
        self.data = data
        self.extract_info()
        self.generate_outputs()

    
    def extract_info(self):
        self.team_name = self.get_team_name()
        self.scores = self.get_score_list()
        self.wickets = self.get_wkts()
        self.overs = self.get_overs()

    def generate_outputs(self):
        self.shortname_txt = self.get_shortname_txt()
        self.score_txt = self.get_score_txt()
        self.overs_txt = self.get_overs_txt()
        # self.run_rate_txt = self.get_run_rate_txt()
        self.other_score_txt = self.get_other_score_txt()
        self.first_inn_score_txt = self.get_first_inn_score_txt()
        

        


    def get_team_name(self):
        e = self.team_name_raw
        try:
            raw = str(e)
            end = raw.split('>')[1]
            correct = end.split('<')[0]
            out = correct.strip()
        except Exception:
            out = ""

        return out



    def get_score_list(self):
        e = self.data

        out = []
        try:
            raw = str(e)
            end = raw.split('</span>')[1:-1]
            
            # 1st innings
            e = end[0]
            to_strip = e.split('<')[0]
            correct = to_strip.strip()
            out.append(correct)

            if len(end)>1:
                # multi day, 2nd inns
                e = end[1]
                start = e.split('<span class="smalltxt">')[0]
                to_strip = start.split('<br/>')[1]
                correct = to_strip.strip()
                out.append(correct)

        except Exception:
            out = [""]
        
        return out



    def get_wkts(self):
        e = self.data
        out = []

        try:
            raw = str(e)
            end = raw.split(' / ')[1:]
                  
            for e in end:
                correct = e.split('(')[0]
                wkts = correct.strip()
                out.append(wkts)

        except Exception:
            out = [""]

        return out



    def get_overs(self):
        e = self.data

        out = []
        try:
            raw = str(e)
            end = raw.split(' (')[1:]
            
            for e in end:
                correct = e.split(')')[0]
                overs = correct.strip()
                if overs.endswith(" overs"):
                    txt = overs.split(" overs")[0]
                else:
                    txt = overs
                out.append(txt)

        except Exception:
            out = [""]

        return out

    def get_overs_txt(self):
        out = []
        for overs in self.overs:
            out.append(f"{overs} overs")
        return out

    def get_score_txt(self):
        out = []

        for score, wkt in zip(self.scores, self.wickets):
            
            if wkt == "All out":
                out.append(str(score))
            else:
                out.append(f"{score}/{wkt}")

        return out

    def get_shortname_txt(self):
        return self.team_name[:3].upper()

    
    def get_run_rate_txt(self):
        out = []

        for overs, runs in zip(self.overs, self.scores):
            if overs:
                try:
                    out.append(f"RR: {round(float(runs)/float(overs),2)}")
                except Exception:
                    pass
            else:
                out.append([""])
            
        return out


    def get_other_score_txt(self):
        out = f"{self.shortname_txt}: "
        
        batted_yet = False
        
        for ind, score in enumerate(self.score_txt):
            if score:
                batted_yet = True
                
                if ind==0:
                    # first innings
                    out = out + f"{score}"
                else:
                    # second innings
                    out = out + f" & {score}"

        if not batted_yet:
            out = f"{self.shortname_txt}: yet to bat"     

        return out



    def get_first_inn_score_txt(self):
        if len(self.score_txt)>1 and self.score_txt[1]:
            first_inn_score = f"& {self.score_txt[0]}"
        else:
            first_inn_score = ""
        return first_inn_score
    

# End of Team Data










class TextGenerator:
    def __init__(self, data) -> None:
        self.team_bat = data["batting"]
        self.team_bowl = data["bowling"]
        self.get_txt_output_dict()



    def get_txt_output_dict(self):
        short_team_names = self.team_bat.shortname_txt
        scores = self.team_bat.score_txt[-1]
        overs = self.team_bat.overs_txt[-1]
        first_inn_score = self.team_bat.first_inn_score_txt
        other_score = self.team_bowl.other_score_txt
        lead_by = self.get_lead_by_txt()
  

        self.txt_output_dict = {
            "teams": short_team_names,
            "scores": scores,
            "overs": overs,
            "run_rate": first_inn_score,
            "match": other_score,
            "lead_by": lead_by}


    def get_lead_by_txt(self):
        if self.team_bowl.scores[0]:
            bowl_scores = [float(e) for e in self.team_bowl.scores]
        else:
            return "Updates once per over"

        bat_scores = [float(e) for e in self.team_bat.scores]

        diff = int(sum(bowl_scores) - sum(bat_scores))
        
        if diff>0:
            out = f"{self.team_bowl.shortname_txt} lead by {diff}"
        elif diff<0:
            out = f"{self.team_bat.shortname_txt} lead by {-diff}"
        else:
            out = "Scores level"

        return out




# End of Text Generator







class FileWriter:
    def __init__(self, txt_output_dict) -> None:
        self.write_files(txt_output_dict)
   
    def write_files(self, txt_output_dict):
        print("\n")
        
        for key in txt_output_dict.keys():
            file_name = f"Generated_text/{key}.txt"
            txt = txt_output_dict[key]
            file_ = open(file_name, 'w')
            file_.writelines(txt)
            print(f"writing: {txt}")

