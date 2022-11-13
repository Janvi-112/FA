from bdb import effective
from crypt import methods
from distutils.log import error
from flask import Flask, render_template, request
from flask_cors import CORS
import pandas as pd
import numpy as np

import json
from bs4 import BeautifulSoup
from urllib.request import urlopen

import warnings

# from pyrsistent import T
warnings.filterwarnings('ignore')

# team1 = pd.DataFrame()

full_df = pd.read_csv("FullData.csv")

app = Flask(__name__, static_url_path='/static')
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/Signin", methods=['POST'])
def get_team_name():
    try:
        global team
        team = request.json.get('team')
        clubname = team

        df = full_df[full_df['club_name'] == clubname]

        cris_scrape_url = 'https://understat.com/team/' + clubname + '/2021'
        page_connect = urlopen(cris_scrape_url)
        page_html = BeautifulSoup(page_connect, "html.parser")

        json_raw_string = page_html.findAll(name="script")[2].text

        start_ind = json_raw_string.index("\\")
        stop_ind = json_raw_string.index("')")

        json_data = json_raw_string[start_ind:stop_ind]
        json_data = json_data.encode("utf8").decode("unicode_escape")

        f_data = json.loads(json_data)
        formation = list(f_data['formation'].keys())[0]
        
        global team_form
        team_form = formation

        global form_img
        form_img="/assets/lineup/"+team_form.replace('-','')+'.png'


        formation_dict = {
            '4-3-3': ['GK', 'LB', 'CB', 'CB', 'RB', 'PCM', 'CCM', 'BCM', 'LW', 'ST', 'RW'],
            '4-2-3-1': ['GK', 'LB', 'CB', 'CB', 'RB', 'BCM', 'CCM', 'LW', 'PCM', 'RW', 'ST'],
            '3-4-2-1': ['GK', 'CB', 'CB', 'CB', 'LB', 'BCM', 'CCM', 'RB', 'PCM', 'PCM', 'ST'],
            '3-4-3': ['GK', 'CB', 'CB', 'CB', 'LB', 'BCM', 'CCM', 'RB', 'LW', 'ST', 'RW'],
            '3-5-2': ['GK', 'CB', 'CB', 'CB', 'LB', 'BCM', 'PCM', 'CCM', 'RB', 'ST', 'ST'],
            '4-4-2': ['GK', 'LB', 'CB', 'CB', 'RB', 'LW', 'BCM', 'CCM', 'RW', 'ST', 'ST'],
            '4-1-4-1': ['GK', 'LB', 'CB', 'CB', 'RB', 'BCM', 'LW', 'PCM', 'CCM', 'RW', 'ST'],
            '4-4-1-1': ['GK', 'LB', 'CB', 'CB', 'RB', 'LW', 'BCM', 'CCM', 'RW', 'PCM', 'ST'],
            '4-1-3-2': ['GK', 'LB', 'CB', 'CB', 'RB', 'BCM', 'LW', 'PCM', 'RW', 'ST', 'ST'],
            '5-3-2': ['GK', 'LB', 'CB', 'CB', 'CB', 'RB', 'BCM', 'PCM', 'CCM', 'ST', 'ST'],
            '3-4-1-2': ['GK', 'CB', 'CB', 'CB', 'LB', 'BCM', 'CCM', 'RB', 'PCM', 'ST', 'ST'],
            '4-3-1-2': ['GK', 'LB', 'CB', 'CB', 'RB', 'BCM', 'CCM', 'BCM', 'PCM', 'ST', 'ST'],
            '3-2-4-1': ['GK', 'CB', 'CB', 'CB', 'BCM', 'CCM', 'LW', 'PCM', 'PCM', 'RW', 'ST'],
            '5-4-1': ['GK', 'LB', 'CB', 'CB', 'CB', 'RB', 'LW','CCM', 'PCM', 'RW', 'ST'],
            '4-2-4': ['GK', 'LB', 'CB', 'CB', 'RB', 'BCM', 'CCM', 'LW', 'ST', 'ST', 'RW']
        }

        team_formation = formation_dict[formation]

        # weights

        a = 0.5
        b = 1
        c = 2
        d = 3 
        e = -0.5

        df['gk_Sweeper'] = (c*df.goalkeeping_speed + d*df.goalkeeping_reflexes + b*df.goalkeeping_positioning + d*df.goalkeeping_kicking + b*df.goalkeeping_handling + b*df.goalkeeping_diving + a*df.movement_reactions) / (a + 3*b + c + 2*d)
        df['df_centre_backs'] = ( d*df.movement_reactions + c*df.mentality_interceptions + d*df.defending_sliding_tackle + d*df.defending_standing_tackle + b*df.mentality_vision + b*df.attacking_crossing + a*df.attacking_short_passing + b*df.attacking_volleys+ c*df.movement_acceleration + b*df.movement_sprint_speed+ d*df.power_stamina + d*df.power_jumping + d*df.attacking_heading_accuracy + b*df.power_long_shots + d*df.defending_marking_awareness + c*df.mentality_aggression)/(5*b + 3*c + 7*d)
        df['df_wing_backs'] = (b*df.skill_ball_control + a*df.skill_dribbling + a*df.defending_marking_awareness + d*df.defending_sliding_tackle + d*df.defending_standing_tackle + a*df.mentality_positioning + c*df.mentality_vision + c*df.attacking_crossing + b*df.attacking_short_passing + c*df.attacking_volleys + d*df.movement_acceleration + d*df.movement_sprint_speed + c*df.power_stamina + a*df.attacking_finishing)/(4*a + 2*b + 4*c + 4*d)
        df['mf_playmaker'] = (d*df.skill_ball_control + d*df.skill_dribbling + d*df.movement_reactions + d*df.mentality_vision + c*df.mentality_positioning + c*df.attacking_crossing + d*df.attacking_short_passing + c*df.skill_long_passing + c*df.skill_curve + b*df.power_long_shots + c*df.skill_fk_accuracy)/(1*b + 5*c + 5*d)
        df['mf_beast'] = (d*df.movement_agility + c*df.movement_balance + b*df.power_jumping + c*df.power_strength + d*df.power_stamina + a*df.movement_sprint_speed + c*df.movement_acceleration + d*df.attacking_short_passing + c*df.mentality_aggression + d*df.movement_reactions + b*df.defending_marking_awareness + b*df.defending_standing_tackle + b*df.defending_sliding_tackle + b*df.mentality_interceptions)/(1*a + 5*b + 4*c + 4*d)
        df['mf_controller'] = (d*df.skill_ball_control + a*df.skill_dribbling + a*df.defending_marking_awareness + a*df.movement_reactions + c*df.mentality_vision + c*df.mentality_composure + d*df.attacking_short_passing + d*df.skill_long_passing)/(2*c + 3*d + 3*a)
        df['att_left_wing'] = (c*df.attacking_volleys + c*df.skill_ball_control + c*df.skill_dribbling + c*df.movement_sprint_speed + d*df.movement_acceleration + b*df.mentality_vision + c*df.attacking_crossing + b*df.attacking_short_passing + b*df.skill_long_passing + b*df.mentality_aggression + b*df.movement_agility + a*df.skill_curve + c*df.power_long_shots + b*df.skill_fk_accuracy + d*df.attacking_finishing)/(a + 6*b + 6*c + 2*d)
        df['att_right_wing'] = (c*df.attacking_volleys + c*df.skill_ball_control + c*df.skill_dribbling + c*df.movement_sprint_speed + d*df.movement_acceleration + b*df.mentality_vision + c*df.attacking_crossing + b*df.attacking_short_passing + b*df.skill_long_passing + b*df.mentality_aggression + b*df.movement_agility + a*df.skill_curve + c*df.power_long_shots + b*df.skill_fk_accuracy + d*df.attacking_finishing)/(a + 6*b + 6*c + 2*d)
        df['att_striker'] = (b*df.attacking_volleys + b*df.skill_ball_control + a*df.mentality_vision + b*df.mentality_aggression + b*df.movement_agility + a*df.skill_curve + a*df.power_long_shots + d*df.movement_balance + d*df.attacking_finishing + d*df.attacking_heading_accuracy + c*df.power_jumping + c*df.skill_dribbling)/(3*a + 4*b + 2*c + 3*d)

        f_df = df[['player_positions', 'short_name', 'gk_Sweeper', 'df_centre_backs', 'df_wing_backs', 'mf_playmaker', 'mf_beast', 'mf_controller', 'att_left_wing', 'att_right_wing', 'att_striker']]

        pos = []
        rating = []
        name = []
        a1, a2, a3, a4, a5, a6 = ([] for i in range(6))
        gk = ['GK']
        cb = ['LCB', 'CB', 'RCB']
        wb = ['RWB', 'RB', 'LB', 'LWB']
        mid = ['CAM', 'LAM', 'RAM', 'CM', 'LCM', 'RCM', 'CDM']
        lw = ['LW', 'LM', 'LS']
        rw = ['RW', 'RM', 'RS']
        st = ['ST', 'CF', 'RS', 'LS']

        for i in f_df.index.values:
            l = f_df.loc[i]['player_positions'].split(", ")[0]
            pos.append(l)
            p = f_df.loc[i]['short_name']
            name.append(p)
            if l in gk:
                r = f_df.loc[i]['gk_Sweeper']
                rating.append(r)
                a1.append(df.loc[i]['goalkeeping_diving'])
                a2.append(df.loc[i]['goalkeeping_handling'])
                a3.append(df.loc[i]['goalkeeping_kicking'])
                a4.append(df.loc[i]['goalkeeping_positioning'])
                a5.append(df.loc[i]['goalkeeping_reflexes'])
                a6.append(df.loc[i]['goalkeeping_speed'])

            elif l in cb:
                r = f_df.loc[i]['df_centre_backs']
                rating.append(r)
                a1.append(df.loc[i]['pace'])
                a2.append(df.loc[i]['shooting'])
                a3.append(df.loc[i]['passing'])
                a4.append(df.loc[i]['dribbling'])
                a5.append(df.loc[i]['defending'])
                a6.append(df.loc[i]['physic'])

            elif l in wb:
                r = f_df.loc[i]['df_wing_backs']
                rating.append(r)
                a1.append(df.loc[i]['pace'])
                a2.append(df.loc[i]['shooting'])
                a3.append(df.loc[i]['passing'])
                a4.append(df.loc[i]['dribbling'])
                a5.append(df.loc[i]['defending'])
                a6.append(df.loc[i]['physic'])

            elif l in mid:
                r = (f_df.loc[i]['mf_playmaker']+f_df.loc[i]['mf_beast']+f_df.loc[i]['mf_controller'])/3
                rating.append(r)
                a1.append(df.loc[i]['pace'])
                a2.append(df.loc[i]['shooting'])
                a3.append(df.loc[i]['passing'])
                a4.append(df.loc[i]['dribbling'])
                a5.append(df.loc[i]['defending'])
                a6.append(df.loc[i]['physic'])

            elif l in lw:
                r = f_df.loc[i]['att_left_wing']
                rating.append(r)
                a1.append(df.loc[i]['pace'])
                a2.append(df.loc[i]['shooting'])
                a3.append(df.loc[i]['passing'])
                a4.append(df.loc[i]['dribbling'])
                a5.append(df.loc[i]['defending'])
                a6.append(df.loc[i]['physic'])

            elif l in rw:
                r = f_df.loc[i]['att_right_wing']
                rating.append(r)
                a1.append(df.loc[i]['pace'])
                a2.append(df.loc[i]['shooting'])
                a3.append(df.loc[i]['passing'])
                a4.append(df.loc[i]['dribbling'])
                a5.append(df.loc[i]['defending'])
                a6.append(df.loc[i]['physic'])

            elif l in st:
                r = f_df.loc[i]['att_striker']
                rating.append(r)
                a1.append(df.loc[i]['pace'])
                a2.append(df.loc[i]['shooting'])
                a3.append(df.loc[i]['passing'])
                a4.append(df.loc[i]['dribbling'])
                a5.append(df.loc[i]['defending'])
                a6.append(df.loc[i]['physic'])


        final_rating  = pd.DataFrame(
            {'Player Position': pos,
            'Player Name': name,
            'Player Score': rating
            }
        )

        radial_rating  = pd.DataFrame(
            {
                'A1': a1,
                'A2': a2,
                'A3': a3,
                'A4': a4,
                'A5': a5,
                'A6': a6
            }
        )

        global radial_team
        radial_team = radial_rating.values.tolist()
        print(radial_team)

        global team1
        team1 = final_rating.values.tolist()

        print(team1)

        fin_df = df.copy()
        playing_11 = []
        playing_score = []

        for player_pos in team_formation:
            
            if player_pos == 'GK':
                sd = df.sort_values('gk_Sweeper', ascending=False)[:1]
                x2 = np.array(list(sd['long_name']))
                y2 = np.array(list(sd['gk_Sweeper']))

                playing_11.append(x2[0])
                playing_score.append(y2[0])
                ind = df[df['long_name'] == x2[0]].index.values[0]
                df = df.drop([ind])
                
            elif player_pos == 'LB':
                sd = pd.DataFrame(columns= df.columns)
                for i in df.index.values:
                    l = df.loc[i]['player_positions'].split(", ")
                    m = ['LWB', 'LB']
                    if any(x in l for x in m):
                        sd = sd.append(df.loc[i])

                sd = sd.sort_values('df_wing_backs', ascending=False)[:1]
                x2 = np.array(list(sd['long_name']))
                y2 = np.array(list(sd['df_wing_backs']))

                playing_11.append(x2[0])
                playing_score.append(y2[0])
                ind = df[df['long_name'] == x2[0]].index.values[0]
                df = df.drop([ind])
                
            elif player_pos == 'RB':
                sd = pd.DataFrame(columns= df.columns)
                for i in df.index.values:
                    l = df.loc[i]['player_positions'].split(", ")
                    m = ['RWB', 'RB']
                    if any(x in l for x in m):
                        sd = sd.append(df.loc[i])

                sd = sd.sort_values('df_wing_backs', ascending=False)[:1]
                x2 = np.array(list(sd['long_name']))
                y2 = np.array(list(sd['df_wing_backs']))

                playing_11.append(x2[0])
                playing_score.append(y2[0])
                ind = df[df['long_name'] == x2[0]].index.values[0]
                df = df.drop([ind])
                
            elif player_pos == 'CB':
                sd = pd.DataFrame(columns= df.columns)
                for i in df.index.values:
                    l = df.loc[i]['player_positions'].split(", ")
                    m = ['LCB', 'CB', 'RCB']
                    if any(x in l for x in m):
                        sd = sd.append(df.loc[i])

                sd = sd.sort_values('df_centre_backs', ascending=False)[:1]
                x2 = np.array(list(sd['long_name']))
                y2 = np.array(list(sd['df_centre_backs']))

                playing_11.append(x2[0])
                playing_score.append(y2[0])
                ind = df[df['long_name'] == x2[0]].index.values[0]
                df = df.drop([ind])
                
            elif player_pos == 'PCM':
                sd = pd.DataFrame(columns= df.columns)
                for i in df.index.values:
                    l = df.loc[i]['player_positions'].split(", ")
                    m = ['CAM', 'LAM', 'RAM', 'CM']
                    if any(x in l for x in m):
                        sd = sd.append(df.loc[i])

                sd = sd.sort_values('mf_playmaker', ascending=False)[:1]
                x2 = np.array(list(sd['long_name']))
                y2 = np.array(list(sd['mf_playmaker']))

                playing_11.append(x2[0])
                playing_score.append(y2[0])
                ind = df[df['long_name'] == x2[0]].index.values[0]
                df = df.drop([ind])
                
                
            elif player_pos == 'CCM':
                sd = pd.DataFrame(columns= df.columns)
                for i in df.index.values:
                    l = df.loc[i]['player_positions'].split(", ")
                    m = ['CM', 'LCM', 'RCM']
                    if any(x in l for x in m):
                        sd = sd.append(df.loc[i])

                sd = sd.sort_values('mf_controller', ascending=False)[:1]
                x2 = np.array(list(sd['long_name']))
                y2 = np.array(list(sd['mf_controller']))

                playing_11.append(x2[0])
                playing_score.append(y2[0])
                ind = df[df['long_name'] == x2[0]].index.values[0]
                df = df.drop([ind])
                
            elif player_pos == 'BCM':
                sd = pd.DataFrame(columns= df.columns)
                for i in df.index.values:
                    l = df.loc[i]['player_positions'].split(", ")
                    m = ['CM', 'LCM', 'RCM', 'CDM']
                    if any(x in l for x in m):
                        sd = sd.append(df.loc[i])

                sd = sd.sort_values('mf_beast', ascending=False)[:1]
                x2 = np.array(list(sd['long_name']))
                y2 = np.array(list(sd['mf_beast']))

                playing_11.append(x2[0])
                playing_score.append(y2[0])
                ind = df[df['long_name'] == x2[0]].index.values[0]
                df = df.drop([ind])  
                
            elif player_pos == 'LW':
                sd = pd.DataFrame(columns= df.columns)
                for i in df.index.values:
                    l = df.loc[i]['player_positions'].split(", ")
                    m = ['LW', 'LM', 'LS']
                    if any(x in l for x in m):
                        sd = sd.append(df.loc[i])

                sd = sd.sort_values('att_left_wing', ascending=False)[:1]
                x2 = np.array(list(sd['long_name']))
                y2 = np.array(list(sd['att_left_wing']))

                playing_11.append(x2[0])
                playing_score.append(y2[0])
                ind = df[df['long_name'] == x2[0]].index.values[0]
                df = df.drop([ind])
                
            elif player_pos == 'RW':
                sd = pd.DataFrame(columns= df.columns)
                for i in df.index.values:
                    l = df.loc[i]['player_positions'].split(", ")
                    m = ['RW', 'RM', 'RS']
                    if any(x in l for x in m):
                        sd = sd.append(df.loc[i])

                sd = sd.sort_values('att_right_wing', ascending=False)[:1]
                x2 = np.array(list(sd['long_name']))
                y2 = np.array(list(sd['att_right_wing']))

                playing_11.append(x2[0])
                playing_score.append(y2[0])
                ind = df[df['long_name'] == x2[0]].index.values[0]
                df = df.drop([ind])
                
                
            elif player_pos == 'ST':
                sd = pd.DataFrame(columns= df.columns)
                for i in df.index.values:
                    l = df.loc[i]['player_positions'].split(", ")
                    m = ['ST', 'CF', 'RS', 'LS']
                    if any(x in l for x in m):
                        sd = sd.append(df.loc[i])

                sd = sd.sort_values('att_striker', ascending=False)[:1]
                x2 = np.array(list(sd['long_name']))
                y2 = np.array(list(sd['att_striker']))

                playing_11.append(x2[0])
                playing_score.append(y2[0])
                ind = df[df['long_name'] == x2[0]].index.values[0]
                df = df.drop([ind])


        final_team  = pd.DataFrame(
            {'Player Position': team_formation,
            'Player Name': playing_11
            })

        global team2
        team2 = final_team.values.tolist()

        print(team2)
        print(team_form)
        print(form_img)
        return render_template('Home.html')
        
    except Exception as e:
        return render_template('Home.html')



@app.route("/Signin")
def signin():
    return render_template("Signin.html")

@app.route("/Home")
def home():
    return render_template("Home.html")

@app.route("/Fixture")
def fixture():
    return render_template("Fixture.html", data1 = team1, data2 = radial_team)


@app.route("/TeamSelection")
def teamselection():
    return render_template("TeamSelection.html", data1 = team2, data2 = team_form, data3 = form_img)

@app.route("/DreamTeam", methods=['POST'])
def get_teams():
    try:
        team1 = request.json.get('value1')
        team2 = request.json.get('value2')
        
        clubname = [team1, team2]
        print(1)
        print(clubname)
        print(2)
        df = full_df[full_df['club_name'].isin(clubname)] 
        a = 0.5
        b = 1
        c = 2
        d = 3 

        df['gk_Sweeper'] = (c*df.goalkeeping_speed + d*df.goalkeeping_reflexes + b*df.goalkeeping_positioning + d*df.goalkeeping_kicking + b*df.goalkeeping_handling + b*df.goalkeeping_diving + a*df.movement_reactions) / (a + 3*b + c + 2*d)
        df['df_centre_backs'] = ( d*df.movement_reactions + c*df.mentality_interceptions + d*df.defending_sliding_tackle + d*df.defending_standing_tackle + b*df.mentality_vision + b*df.attacking_crossing + a*df.attacking_short_passing + b*df.attacking_volleys+ c*df.movement_acceleration + b*df.movement_sprint_speed+ d*df.power_stamina + d*df.power_jumping + d*df.attacking_heading_accuracy + b*df.power_long_shots + d*df.defending_marking_awareness + c*df.mentality_aggression)/(5*b + 3*c + 7*d)
        df['df_wing_backs'] = (b*df.skill_ball_control + a*df.skill_dribbling + a*df.defending_marking_awareness + d*df.defending_sliding_tackle + d*df.defending_standing_tackle + a*df.mentality_positioning + c*df.mentality_vision + c*df.attacking_crossing + b*df.attacking_short_passing + c*df.attacking_volleys + d*df.movement_acceleration + d*df.movement_sprint_speed + c*df.power_stamina + a*df.attacking_finishing)/(4*a + 2*b + 4*c + 4*d)
        df['mf_playmaker'] = (d*df.skill_ball_control + d*df.skill_dribbling + d*df.movement_reactions + d*df.mentality_vision + c*df.mentality_positioning + c*df.attacking_crossing + d*df.attacking_short_passing + c*df.skill_long_passing + c*df.skill_curve + b*df.power_long_shots + c*df.skill_fk_accuracy)/(1*b + 5*c + 5*d)
        df['mf_beast'] = (d*df.movement_agility + c*df.movement_balance + b*df.power_jumping + c*df.power_strength + d*df.power_stamina + a*df.movement_sprint_speed + c*df.movement_acceleration + d*df.attacking_short_passing + c*df.mentality_aggression + d*df.movement_reactions + b*df.defending_marking_awareness + b*df.defending_standing_tackle + b*df.defending_sliding_tackle + b*df.mentality_interceptions)/(1*a + 5*b + 4*c + 4*d)
        df['mf_controller'] = (d*df.skill_ball_control + a*df.skill_dribbling + a*df.defending_marking_awareness + a*df.movement_reactions + c*df.mentality_vision + c*df.mentality_composure + d*df.attacking_short_passing + d*df.skill_long_passing)/(2*c + 3*d + 3*a)
        df['att_left_wing'] = (c*df.attacking_volleys + c*df.skill_ball_control + c*df.skill_dribbling + c*df.movement_sprint_speed + d*df.movement_acceleration + b*df.mentality_vision + c*df.attacking_crossing + b*df.attacking_short_passing + b*df.skill_long_passing + b*df.mentality_aggression + b*df.movement_agility + a*df.skill_curve + c*df.power_long_shots + b*df.skill_fk_accuracy + d*df.attacking_finishing)/(a + 6*b + 6*c + 2*d)
        df['att_right_wing'] = (c*df.attacking_volleys + c*df.skill_ball_control + c*df.skill_dribbling + c*df.movement_sprint_speed + d*df.movement_acceleration + b*df.mentality_vision + c*df.attacking_crossing + b*df.attacking_short_passing + b*df.skill_long_passing + b*df.mentality_aggression + b*df.movement_agility + a*df.skill_curve + c*df.power_long_shots + b*df.skill_fk_accuracy + d*df.attacking_finishing)/(a + 6*b + 6*c + 2*d)
        df['att_striker'] = (b*df.attacking_volleys + b*df.skill_ball_control + a*df.mentality_vision + b*df.mentality_aggression + b*df.movement_agility + a*df.skill_curve + a*df.power_long_shots + d*df.movement_balance + d*df.attacking_finishing + d*df.attacking_heading_accuracy + c*df.power_jumping + c*df.skill_dribbling)/(3*a + 4*b + 2*c + 3*d)

        playing_11 = []
        sd = df.sort_values('gk_Sweeper', ascending=False)[:1]
        x2 = np.array(list(sd['long_name']))
        playing_11.append(x2)
        ind = df[df['long_name'] == x2[0]].index.values[0]
        df = df.drop([ind])

        sd = pd.DataFrame(columns= df.columns)
        for i in df.index.values:
            l = df.loc[i]['player_positions'].split(", ")
            m = ['LWB', 'LB']
            if any(x in l for x in m):
                sd = sd.append(df.loc[i])
        sd = sd.sort_values('df_wing_backs', ascending=False)[:1]
        x2 = np.array(list(sd['long_name']))
        playing_11.append(x2)
        ind = df[df['long_name'] == x2[0]].index.values[0]
        df = df.drop([ind])

        sd = pd.DataFrame(columns= df.columns)
        for i in df.index.values:
            l = df.loc[i]['player_positions'].split(", ")
            m = ['LCB', 'CB']
            if any(x in l for x in m):
                sd = sd.append(df.loc[i])
        sd = sd.sort_values('df_centre_backs', ascending=False)[:1]
        x2 = np.array(list(sd['long_name']))
        playing_11.append(x2)
        ind = df[df['long_name'] == x2[0]].index.values[0]
        df = df.drop([ind])

        sd = pd.DataFrame(columns= df.columns)
        for i in df.index.values:
            l = df.loc[i]['player_positions'].split(", ")
            m = ['RCB', 'CB']
            if any(x in l for x in m):
                sd = sd.append(df.loc[i])
        sd = sd.sort_values('df_centre_backs', ascending=False)[:1]
        x2 = np.array(list(sd['long_name']))
        playing_11.append(x2)
        ind = df[df['long_name'] == x2[0]].index.values[0]
        df = df.drop([ind])

        sd = pd.DataFrame(columns= df.columns)
        for i in df.index.values:
            l = df.loc[i]['player_positions'].split(", ")
            m = ['RWB', 'RB']
            if any(x in l for x in m):
                sd = sd.append(df.loc[i])
        sd = sd.sort_values('df_wing_backs', ascending=False)[:1]
        x2 = np.array(list(sd['long_name']))
        playing_11.append(x2)
        ind = df[df['long_name'] == x2[0]].index.values[0]
        df = df.drop([ind])

        sd = pd.DataFrame(columns= df.columns)
        for i in df.index.values:
            l = df.loc[i]['player_positions'].split(", ")
            m = ['CAM', 'LAM', 'RAM']
            if any(x in l for x in m):
                sd = sd.append(df.loc[i])
        sd = sd.sort_values('mf_playmaker', ascending=False)[:1]
        x2 = np.array(list(sd['long_name']))
        playing_11.append(x2)
        ind = df[df['long_name'] == x2[0]].index.values[0]
        df = df.drop([ind])

        sd = pd.DataFrame(columns= df.columns)
        for i in df.index.values:
            l = df.loc[i]['player_positions'].split(", ")
            m = ['CM', 'RM', 'RCM']
            if any(x in l for x in m):
                sd = sd.append(df.loc[i])
        sd = sd.sort_values('mf_beast', ascending=False)[:1]
        x2 = np.array(list(sd['long_name']))
        playing_11.append(x2)
        ind = df[df['long_name'] == x2[0]].index.values[0]
        df = df.drop([ind])

        sd = pd.DataFrame(columns= df.columns)
        for i in df.index.values:
            l = df.loc[i]['player_positions'].split(", ")
            m = ['CM', 'LM', 'LCM']
            if any(x in l for x in m):
                sd = sd.append(df.loc[i])
        sd = sd.sort_values('mf_controller', ascending=False)[:1]
        x2 = np.array(list(sd['long_name']))
        playing_11.append(x2)
        ind = df[df['long_name'] == x2[0]].index.values[0]
        df = df.drop([ind])

        sd = pd.DataFrame(columns= df.columns)
        for i in df.index.values:
            l = df.loc[i]['player_positions'].split(", ")
            m = ['LW', 'LM', 'LS']
            if any(x in l for x in m):
                sd = sd.append(df.loc[i])
        sd = sd.sort_values('att_left_wing', ascending=False)[:1]
        x2 = np.array(list(sd['long_name']))
        playing_11.append(x2)
        ind = df[df['long_name'] == x2[0]].index.values[0]
        df = df.drop([ind])

        sd = pd.DataFrame(columns= df.columns)
        for i in df.index.values:
            l = df.loc[i]['player_positions'].split(", ")
            m = ['ST', 'CF', 'RS', 'LS']
            if any(x in l for x in m):
                sd = sd.append(df.loc[i])
        sd = sd.sort_values('att_striker', ascending=False)[:1]
        x2 = np.array(list(sd['long_name']))
        playing_11.append(x2)
        ind = df[df['long_name'] == x2[0]].index.values[0]
        df = df.drop([ind])

        sd = pd.DataFrame(columns= df.columns)
        for i in df.index.values:
            l = df.loc[i]['player_positions'].split(", ")
            m = ['RW', 'RM', 'RS']
            if any(x in l for x in m):
                sd = sd.append(df.loc[i])
        sd = sd.sort_values('att_right_wing', ascending=False)[:1]
        x2 = np.array(list(sd['long_name']))
        playing_11.append(x2)
        ind = df[df['long_name'] == x2[0]].index.values[0]
        df = df.drop([ind])

        play_pos = ['GK', 'LB', 'CB', 'CB', 'RB', 'PCM', 'BCM', 'CCM', 'LW', 'ST', 'RW']
        
        fin_team  = pd.DataFrame({
                'Player Position': play_pos,
                'Player Name': playing_11
            })

        global dt 
        dt = fin_team.values.tolist()
        print(dt)

        return render_template("DreamTeamOutput.html")

    except Exception as e:
        return render_template('Home.html')

@app.route("/DreamTeam")
def dreamteam():
    return render_template("DreamTeam.html")

@app.route("/DreamTeamOutput")
def dreamteamoutput():
    return render_template("DreamTeamOutput.html", data=dt)

if __name__ == "__main__":
    app.run(debug=False,host='0.0.0.0',port=8080)